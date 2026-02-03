"""
Simple test to verify the setup works correctly.
"""

def test_imports():

    """Test that all modules can be imported."""
    try:
        import core.config
        import core.deps
        import schema.synology
        import service.synology_service
        print("✅ All core modules imported successfully")
        
        # Check that key classes exist
        assert hasattr(core.config, 'Settings')
        assert hasattr(core.deps, 'get_synology_service')
        assert hasattr(schema.synology, 'LoginResponse')
        assert hasattr(service.synology_service, 'SynologyService')
        print("✅ All key classes found")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    print("Running setup tests...")
    print("Note: Install dependencies first with: pip install -r requirements.txt")
    print()
    
    if test_imports():
        print("✅ All tests passed!")
        print("\nTo start the server:")
        print("1. Copy .env.example to .env and configure your Synology NAS details")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run server: uvicorn main:app --reload")
        print("4. Access docs: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed")