from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent.parent / 'backend' / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', "mongodb://localhost:27017/aso_tool")
client = MongoClient(mongo_url)
db = client.aso_tool

# Initial app data
apps = [
    {
        "package_name": "com.badhobuyer",
        "name": "BadhoBuyer",
        "category": "Business",
        "is_main_app": True,
        "is_competitor": False,
        "metadata": {
            "title": "BadhoBuyer - B2B Wholesale Trading App",
            "description": "BadhoBuyer is a B2B wholesale trading platform connecting businesses with suppliers.",
            "category": "Business",
            "keywords": ["wholesale", "b2b", "business", "trading", "supplier"],
            "ratings": {
                "average": 4.5,
                "count": 1000
            },
            "installs": "10,000+"
        }
    },
    {
        "package_name": "club.kirana",
        "name": "Kirana Club",
        "category": "Business",
        "is_main_app": False,
        "is_competitor": True,
        "metadata": {
            "title": "Kirana Club - B2B Wholesale App",
            "description": "Kirana Club is a B2B wholesale app for retailers and suppliers.",
            "category": "Business",
            "keywords": ["wholesale", "b2b", "kirana", "retail", "supplier"],
            "ratings": {
                "average": 4.3,
                "count": 5000
            },
            "installs": "50,000+"
        }
    },
    {
        "package_name": "com.udaan.android",
        "name": "Udaan",
        "category": "Business",
        "is_main_app": False,
        "is_competitor": True,
        "metadata": {
            "title": "Udaan - B2B Trading Platform",
            "description": "Udaan is India's largest B2B trading platform for businesses.",
            "category": "Business",
            "keywords": ["wholesale", "b2b", "trading", "marketplace", "business"],
            "ratings": {
                "average": 4.4,
                "count": 100000
            },
            "installs": "1,000,000+"
        }
    }
]

# Clear existing data
db.apps.delete_many({})

# Insert new data
db.apps.insert_many(apps)

print("Database initialized with test data!")