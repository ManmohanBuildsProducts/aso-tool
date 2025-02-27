from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime, timedelta
import logging
from app.services.app_scraper import AppScraper
from app.services.text_analyzer import TextAnalyzer

logger = logging.getLogger(__name__)

class MetadataTracker:
    def __init__(self):
        self.data_dir = "data/metadata_history"
        self.ensure_data_directory()
        self.app_scraper = AppScraper()
        self.text_analyzer = TextAnalyzer()
        
        # Define metadata fields to track
        self.tracked_fields = [
            'title',
            'description',
            'version',
            'score',
            'ratings',
            'reviews',
            'installs',
            'size',
            'released',
            'updated',
            'category'
        ]

    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(self.data_dir, exist_ok=True)

    def get_history_file(self, app_id: str) -> str:
        """Get the path to app's history file"""
        return os.path.join(self.data_dir, f"{app_id}_history.json")

    async def track_metadata(self, app_id: str) -> Dict[str, Any]:
        """
        Track and store app metadata
        """
        try:
            # Get current app data
            current_data = await self.app_scraper.get_app_details(app_id)
            
            # Prepare metadata record
            metadata = self._prepare_metadata(current_data)
            
            # Add text analysis
            metadata['text_analysis'] = {
                'title': self.text_analyzer.analyze_text(
                    metadata.get('title', ''),
                    'title'
                ),
                'description': self.text_analyzer.analyze_text(
                    metadata.get('description', ''),
                    'full_description'
                )
            }
            
            # Load existing history
            history = self.load_history(app_id)
            
            # Add new metadata
            history['metadata'].append(metadata)
            
            # Keep only last 90 days of data
            history['metadata'] = self._cleanup_old_data(history['metadata'])
            
            # Save updated history
            self.save_history(app_id, history)
            
            # Calculate changes and trends
            changes = self._calculate_changes(history['metadata'])
            trends = self._analyze_trends(history['metadata'])
            
            return {
                "current_metadata": metadata,
                "changes": changes,
                "trends": trends,
                "history": history['metadata']
            }
        
        except Exception as e:
            logger.error(f"Error tracking metadata for {app_id}: {str(e)}")
            raise

    def load_history(self, app_id: str) -> Dict[str, Any]:
        """Load historical data from file"""
        history_file = self.get_history_file(app_id)
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading history file: {str(e)}")
        
        return {"metadata": []}

    def save_history(self, app_id: str, data: Dict[str, Any]):
        """Save historical data to file"""
        try:
            history_file = self.get_history_file(app_id)
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving history file: {str(e)}")

    def _prepare_metadata(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare metadata record for storage
        """
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "record_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Extract tracked fields
        for field in self.tracked_fields:
            if field in app_data:
                metadata[field] = app_data[field]
        
        return metadata

    def parse_timestamp(self, timestamp: str) -> str:
        """
        Parse timestamp into date string
        """
        try:
            if isinstance(timestamp, (int, float)):
                dt = datetime.fromtimestamp(timestamp)
            else:
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return ""

    def _cleanup_old_data(self, metadata_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Keep only last 90 days of data
        """
        cutoff_date = datetime.now() - timedelta(days=90)
        return [
            m for m in metadata_list
            if datetime.fromisoformat(m["timestamp"]) > cutoff_date
        ]

    def _calculate_changes(self, metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate changes between current and previous metadata
        """
        if len(metadata_list) < 2:
            return {}
        
        current = metadata_list[-1]
        previous = metadata_list[-2]
        
        changes = {}
        
        # Calculate numeric changes
        numeric_fields = ['score', 'ratings', 'reviews', 'installs']
        for field in numeric_fields:
            if field in current and field in previous:
                curr_val = float(str(current[field]).replace(',', '').replace('+', '')) if current[field] is not None else 0
                prev_val = float(str(previous[field]).replace(',', '').replace('+', '')) if previous[field] is not None else 0
                
                absolute_change = curr_val - prev_val
                percent_change = (absolute_change / prev_val * 100) if prev_val > 0 else 0
                
                changes[field] = {
                    "absolute": absolute_change,
                    "percentage": round(percent_change, 2)
                }
        
        # Track text changes
        text_fields = ['title', 'description']
        for field in text_fields:
            if field in current and field in previous:
                if current[field] != previous[field]:
                    changes[field] = {
                        "changed": True,
                        "previous_length": len(previous[field]),
                        "current_length": len(current[field])
                    }
                else:
                    changes[field] = {"changed": False}
        
        return changes

    def _analyze_trends(self, metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trends in metadata over time
        """
        if len(metadata_list) < 2:
            return {}
        
        trends = {}
        
        # Group by date
        daily_data = {}
        for record in metadata_list:
            date = record["record_date"]
            if date not in daily_data:
                daily_data[date] = record
        
        # Sort dates
        sorted_dates = sorted(daily_data.keys())
        
        # Calculate trends for numeric fields
        numeric_fields = ['score', 'ratings', 'reviews', 'installs']
        for field in numeric_fields:
            field_values = []
            for date in sorted_dates:
                record = daily_data[date]
                if field in record and record[field] is not None:
                    try:
                        value = float(record[field])
                        field_values.append(value)
                    except (ValueError, TypeError):
                        continue
            
            if field_values:
                trends[field] = self._calculate_field_trend(field_values)
        
        # Analyze update frequency
        if len(sorted_dates) >= 2:
            date_diffs = []
            for i in range(1, len(sorted_dates)):
                prev_date = datetime.strptime(sorted_dates[i-1], "%Y-%m-%d")
                curr_date = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
                diff_days = (curr_date - prev_date).days
                date_diffs.append(diff_days)
            
            avg_update_frequency = sum(date_diffs) / len(date_diffs)
            trends["update_frequency"] = {
                "average_days": round(avg_update_frequency, 1),
                "total_updates": len(metadata_list)
            }
        
        return trends

    def _calculate_field_trend(self, values: List[float]) -> Dict[str, Any]:
        """
        Calculate trend metrics for a field
        """
        if not values:
            return {}
        
        # Calculate basic metrics
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
        
        # Calculate trend direction
        if len(values) >= 2:
            recent_change = values[-1] - values[-2]
            trend_direction = "increasing" if recent_change > 0 else "decreasing" if recent_change < 0 else "stable"
        else:
            trend_direction = "stable"
        
        # Calculate volatility
        if len(values) >= 2:
            changes = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
            volatility = sum(changes) / len(changes)
        else:
            volatility = 0
        
        return {
            "current": values[-1],
            "minimum": min_val,
            "maximum": max_val,
            "average": avg_val,
            "direction": trend_direction,
            "volatility": volatility
        }