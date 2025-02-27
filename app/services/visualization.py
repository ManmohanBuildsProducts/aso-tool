from typing import Dict, Any, List
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime
import pandas as pd
import numpy as np

class Visualizer:
    def __init__(self):
        # Set style
        plt.style.use('default')
        sns.set_theme(style="whitegrid")
        sns.set_palette("husl")

    def create_keyword_comparison_chart(self, data: Dict[str, Any]) -> str:
        """Create a visualization comparing keyword metrics"""
        plt.figure(figsize=(12, 6))
        
        # Extract data
        keywords = list(data.get("keyword_trends", {}).keys())
        difficulty_scores = [
            data["keyword_trends"][k]["difficulty_score"]
            for k in keywords
        ]
        
        # Create bar chart
        bars = plt.bar(keywords, difficulty_scores)
        
        # Customize chart
        plt.title("Keyword Difficulty Comparison")
        plt.xlabel("Keywords")
        plt.ylabel("Difficulty Score")
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom')
        
        # Convert plot to base64 string
        return self._fig_to_base64()

    def create_historical_trend_chart(self, metrics: List[Dict[str, Any]]) -> str:
        """Create a visualization of historical trends"""
        # Convert data to DataFrame
        df = pd.DataFrame(metrics)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot ratings and reviews
        ax1.plot(df['timestamp'], df['ratings'], label='Rating', marker='o')
        ax1.set_title('Rating Over Time')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Rating')
        
        # Plot installs on second subplot
        ax2.plot(df['timestamp'], df['installs'], label='Installs', marker='o', color='green')
        ax2.set_title('Installs Over Time')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Number of Installs')
        
        # Format the plot
        plt.tight_layout()
        
        return self._fig_to_base64()

    def create_competitor_comparison_chart(self, data: Dict[str, Any]) -> str:
        """Create a visualization comparing app with competitors"""
        # Extract data
        main_app = data["main_app"]
        competitors = data["competitors"]
        
        # Prepare data for plotting
        metrics = ['ratings', 'installs', 'reviews']
        app_names = [main_app["app_id"]] + [comp["app_id"] for comp in competitors]
        
        # Create figure with subplots
        fig, axes = plt.subplots(len(metrics), 1, figsize=(12, 12))
        
        for i, metric in enumerate(metrics):
            # Get values for each app
            values = [
                main_app["details"].get(metric, 0),
                *[comp["details"].get(metric, 0) for comp in competitors]
            ]
            
            # Create bar chart
            bars = axes[i].bar(app_names, values)
            axes[i].set_title(f'{metric.title()} Comparison')
            axes[i].set_xticklabels(app_names, rotation=45, ha='right')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                axes[i].text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:,.0f}',
                        ha='center', va='bottom')
        
        plt.tight_layout()
        return self._fig_to_base64()

    def _fig_to_base64(self) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')