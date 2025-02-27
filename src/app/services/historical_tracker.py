from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import os
import logging
from app.services.app_scraper import AppScraper

logger = logging.getLogger(__name__)

class HistoricalTracker:
    def __init__(self):
        self.data_dir = "data/historical"
        self.ensure_data_directory()
        self.app_scraper = AppScraper()

    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(self.data_dir, exist_ok=True)

    def get_app_history_file(self, app_id: str) -> str:
        """Get the path to the app's history file"""
        return os.path.join(self.data_dir, f"{app_id}_history.json")

    async def track_app_metrics(self, app_id: str) -> Dict[str, Any]:
        """
        Track and store app metrics
        """
        try:
            # Get current app data
            current_data = await self.app_scraper.get_app_details(app_id)
            
            # Prepare metrics to track
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "ratings": current_data.get("score", 0),
                "total_ratings": current_data.get("ratings", 0),
                "reviews": current_data.get("reviews", 0),
                "installs": current_data.get("minInstalls", 0),
                "version": current_data.get("version", "unknown")
            }

            # Load existing history
            history_file = self.get_app_history_file(app_id)
            history = self.load_history(history_file)
            
            # Add new metrics
            history["metrics"].append(metrics)
            
            # Keep only last 90 days of data
            cutoff_date = datetime.now() - timedelta(days=90)
            history["metrics"] = [
                m for m in history["metrics"]
                if datetime.fromisoformat(m["timestamp"]) > cutoff_date
            ]
            
            # Save updated history
            self.save_history(history_file, history)
            
            # Calculate trends
            trends = self.calculate_trends(history["metrics"])
            
            return {
                "current_metrics": metrics,
                "trends": trends,
                "historical_data": history["metrics"]
            }

        except Exception as e:
            logger.error(f"Error tracking metrics for {app_id}: {str(e)}")
            raise

    def load_history(self, history_file: str) -> Dict[str, Any]:
        """Load historical data from file"""
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading history file: {str(e)}")
        
        return {"metrics": []}

    def save_history(self, history_file: str, data: Dict[str, Any]):
        """Save historical data to file"""
        try:
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving history file: {str(e)}")

    def calculate_trends(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trends from historical data"""
        if len(metrics) < 2:
            return {}

        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x["timestamp"])
        
        # Calculate changes over different periods
        day_change = self.calculate_period_change(sorted_metrics, days=1)
        week_change = self.calculate_period_change(sorted_metrics, days=7)
        month_change = self.calculate_period_change(sorted_metrics, days=30)

        return {
            "daily_change": day_change,
            "weekly_change": week_change,
            "monthly_change": month_change
        }

    def calculate_period_change(self, metrics: List[Dict[str, Any]], days: int) -> Dict[str, Any]:
        """Calculate changes over a specific period"""
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        
        # Get current and previous metrics
        current = metrics[-1]
        previous = next(
            (m for m in reversed(metrics) 
             if datetime.fromisoformat(m["timestamp"]) <= cutoff),
            metrics[0]
        )

        # Calculate changes
        changes = {}
        for key in ["ratings", "total_ratings", "reviews", "installs"]:
            if key in current and key in previous:
                current_val = float(current[key])
                previous_val = float(previous[key])
                absolute_change = current_val - previous_val
                percent_change = (absolute_change / previous_val * 100) if previous_val > 0 else 0
                
                changes[key] = {
                    "absolute": absolute_change,
                    "percentage": round(percent_change, 2)
                }

        return changes