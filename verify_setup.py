"""Verify the setup"""
import os
import sys

def main():
    print("Current directory:", os.getcwd())
    print("Python path:", sys.path)
    print("Environment variables:")
    for key, value in os.environ.items():
        print(f"  {key}={value}")
    
    try:
        from aso_tool.main import app
        print("\n✅ Successfully imported aso_tool.main")
    except Exception as e:
        print(f"\n❌ Failed to import aso_tool.main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()