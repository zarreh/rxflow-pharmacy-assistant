"""
Basic setup test for RxFlow Pharmacy Assistant
"""


def test_imports():
    """Test that all main components can be imported"""
    try:
        from rxflow import RefillState, get_logger, get_settings
        from rxflow.config import Settings
        from rxflow.utils import calculate_distance, format_currency
        from rxflow.workflow import RefillState as WorkflowState

        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_settings():
    """Test settings configuration"""
    try:
        from rxflow import get_settings

        settings = get_settings()

        print(f"✅ Settings loaded: {settings.app_name}")
        print(f"✅ LLM Model: {settings.ollama_model}")
        print(f"✅ Debug mode: {settings.debug}")
        return True
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False


def test_logging():
    """Test logging setup"""
    try:
        from rxflow.utils import get_logger

        logger = get_logger("test")
        logger.info("Test log message")

        print("✅ Logging setup successful")
        return True
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False


def test_state_creation():
    """Test state creation"""
    try:
        from rxflow.workflow.state import create_initial_state

        state = create_initial_state()

        print(f"✅ State created with patient: {state['patient_id']}")
        return True
    except Exception as e:
        print(f"❌ State creation failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Running RxFlow Setup Tests...")
    print("=" * 50)

    tests = [test_imports, test_settings, test_logging, test_state_creation]

    results = []
    for test in tests:
        print(f"\n🔄 Running {test.__name__}...")
        results.append(test())

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)

    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! RxFlow is ready for development.")
    else:
        print("⚠️  Some tests failed. Please check the setup.")
