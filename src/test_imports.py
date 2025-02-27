"""Test imports to verify module structure"""
try:
    from app.main import app
    print("✅ Successfully imported app.main")
except Exception as e:
    print(f"❌ Failed to import app.main: {str(e)}")

try:
    from app.services.app_scraper import AppScraper
    print("✅ Successfully imported app.services.app_scraper")
except Exception as e:
    print(f"❌ Failed to import app.services.app_scraper: {str(e)}")

try:
    from app.services.competitor_analyzer import CompetitorAnalyzer
    print("✅ Successfully imported app.services.competitor_analyzer")
except Exception as e:
    print(f"❌ Failed to import app.services.competitor_analyzer: {str(e)}")

if __name__ == "__main__":
    print("\nTesting imports with current PYTHONPATH...")
    import os
    print(f"PYTHONPATH: {os.getenv('PYTHONPATH')}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir('.')}")