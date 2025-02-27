"""Test the package setup"""
import os
import sys

def test_imports():
    """Test that we can import the package"""
    print(f"Python version: {sys.version}")
    print(f"PYTHONPATH: {os.getenv('PYTHONPATH')}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir('.')}")
    
    try:
        import aso_tool
        print("✅ Successfully imported aso_tool")
        print(f"Version: {aso_tool.__version__}")
    except Exception as e:
        print(f"❌ Failed to import aso_tool: {str(e)}")
        sys.exit(1)

    try:
        from aso_tool.main import app
        print("✅ Successfully imported aso_tool.main")
    except Exception as e:
        print(f"❌ Failed to import aso_tool.main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_imports()