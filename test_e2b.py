"""Test script for E2B sandbox execution tool."""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from namicode_cli.onboarding import SecretManager


def test_e2b_import():
    """Test if E2B executor can be imported."""
    print("Test 1: Importing E2BExecutor...")
    try:
        from namicode_cli.integrations.e2b_executor import E2BExecutor, format_e2b_result
        print("[OK] E2BExecutor imported successfully")
        return True
    except ImportError as e:
        print(f"[FAIL] Failed to import E2BExecutor: {e}")
        return False


def test_e2b_tool_import():
    """Test if execute_in_e2b tool can be imported."""
    print("\nTest 2: Importing execute_in_e2b tool...")
    try:
        from namicode_cli.tools import execute_in_e2b
        print("[OK] execute_in_e2b tool imported successfully")
        return True
    except ImportError as e:
        print(f"[FAIL] Failed to import execute_in_e2b: {e}")
        return False


def test_e2b_api_key():
    """Test if E2B API key is configured."""
    print("\nTest 3: Checking E2B API key...")
    secret_manager = SecretManager()
    api_key = secret_manager.get_secret("e2b_api_key") or os.environ.get("E2B_API_KEY")

    if api_key:
        print(f"[OK] E2B API key found (length: {len(api_key)})")
        return True, api_key
    else:
        print("[FAIL] E2B API key not configured")
        print("  Set it with: nami secrets set e2b_api_key")
        print("  Or: export E2B_API_KEY=your-key-here")
        return False, None


def test_e2b_execution(api_key):
    """Test actual E2B code execution."""
    print("\nTest 4: Testing E2B code execution...")
    try:
        from namicode_cli.integrations.e2b_executor import E2BExecutor

        executor = E2BExecutor(api_key=api_key)

        # Test 1: Simple Python print
        print("  -> Test 4a: Simple Python print")
        result = executor.execute("print('Hello from E2B!')", language="python", timeout=10)

        if result.exit_code == 0:
            print(f"    [OK] Exit code: {result.exit_code}")
            print(f"    [OK] Output: {result.stdout.strip()}")
            print(f"    [OK] Execution time: {result.execution_time:.2f}s")
        else:
            print(f"    [FAIL] Failed with exit code: {result.exit_code}")
            print(f"    Error: {result.error}")
            return False

        # Test 2: Python with imports
        print("\n  -> Test 4b: Python with imports")
        result = executor.execute("import sys; print(f'Python {sys.version}')", language="python", timeout=10)

        if result.exit_code == 0:
            print(f"    [OK] Exit code: {result.exit_code}")
            print(f"    [OK] Output: {result.stdout.strip()}")
        else:
            print(f"    [FAIL] Failed with exit code: {result.exit_code}")
            return False

        # Test 3: File upload
        print("\n  -> Test 4c: File upload test")
        result = executor.execute(
            "with open('test.txt') as f: print(f.read())",
            language="python",
            files=[("test.txt", "Hello from file!")],
            timeout=10
        )

        if result.exit_code == 0:
            print(f"    [OK] Exit code: {result.exit_code}")
            print(f"    [OK] Output: {result.stdout.strip()}")
        else:
            print(f"    [FAIL] Failed with exit code: {result.exit_code}")
            return False

        print("\n[OK] All E2B execution tests passed!")
        return True

    except Exception as e:
        print(f"[FAIL] E2B execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_e2b_tool_function(api_key):
    """Test the execute_in_e2b tool function."""
    print("\nTest 5: Testing execute_in_e2b tool function...")
    try:
        from namicode_cli.tools import execute_in_e2b

        # Set API key in environment for the tool
        os.environ["E2B_API_KEY"] = api_key

        # Test simple execution
        print("  -> Running simple Python code")
        result = execute_in_e2b(code="print('Tool test successful!')", language="python")

        print(f"    Result:\n{result}")

        if "Tool test successful!" in result and "Exit code: 0" in result:
            print("\n[OK] execute_in_e2b tool works correctly!")
            return True
        else:
            print("\n[FAIL] execute_in_e2b tool output unexpected")
            return False

    except Exception as e:
        print(f"[FAIL] Tool function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("E2B Sandbox Execution Tool Test Suite")
    print("="*60)

    # Test imports
    if not test_e2b_import():
        print("\n[X] E2B executor import failed - check dependencies")
        return False

    if not test_e2b_tool_import():
        print("\n[X] E2B tool import failed")
        return False

    # Check API key
    has_key, api_key = test_e2b_api_key()
    if not has_key:
        print("\n[WARN] E2B API key not configured - skipping execution tests")
        print("\nTo complete testing:")
        print("1. Get API key from https://e2b.dev")
        print("2. Set it with: export E2B_API_KEY=your-key-here")
        print("3. Run this test again")
        return False

    # Test execution
    if not test_e2b_execution(api_key):
        print("\n[X] E2B execution tests failed")
        return False

    # Test tool function
    if not test_e2b_tool_function(api_key):
        print("\n[X] E2B tool function tests failed")
        return False

    print("\n" + "="*60)
    print("[SUCCESS] ALL TESTS PASSED!")
    print("="*60)
    print("\nE2B sandbox execution tool is working correctly!")
    print("You can now use execute_in_e2b() in the agent.")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
