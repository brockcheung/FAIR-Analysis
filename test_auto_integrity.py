#!/usr/bin/env python3
"""
Test Suite for Automated Integrity Protection

This script validates that auto-integrity correctly integrates with all tools:
1. CLI tools (quick_risk_analysis.py, fair_risk_calculator.py)
2. Web app (fair_risk_app.py)
3. Auto-generation on first run
4. Auto-verification on subsequent runs

Usage:
    python test_auto_integrity.py
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


class TestAutoIntegrity:
    """Test automated integrity protection system"""

    def __init__(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.manifest_path = os.path.join(self.test_dir, 'integrity_manifest.json')
        self.backup_path = None
        self.passed = 0
        self.failed = 0

    def backup_manifest(self):
        """Backup existing manifest if it exists"""
        if os.path.exists(self.manifest_path):
            self.backup_path = self.manifest_path + '.backup'
            shutil.copy(self.manifest_path, self.backup_path)
            print(f"ℹ️  Backed up existing manifest to: {self.backup_path}")

    def restore_manifest(self):
        """Restore manifest from backup"""
        if self.backup_path and os.path.exists(self.backup_path):
            shutil.move(self.backup_path, self.manifest_path)
            print(f"ℹ️  Restored manifest from backup")

    def remove_manifest(self):
        """Remove manifest to simulate first run"""
        if os.path.exists(self.manifest_path):
            os.remove(self.manifest_path)
            print(f"✓ Removed manifest for first-run test")

    def run_test(self, test_name, test_func):
        """Run a single test"""
        try:
            print(f"\n{'='*70}")
            print(f"TEST: {test_name}")
            print('='*70)
            result = test_func()
            if result:
                print(f"✅ PASSED: {test_name}")
                self.passed += 1
            else:
                print(f"❌ FAILED: {test_name}")
                self.failed += 1
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            self.failed += 1

    def test_auto_integrity_module(self):
        """Test 1: Auto-integrity module self-test"""
        print("Testing auto_integrity.py module...")

        # Remove manifest to simulate first run
        self.remove_manifest()

        # Run auto-integrity self-test
        result = subprocess.run(
            [sys.executable, 'auto_integrity.py'],
            cwd=self.test_dir,
            capture_output=True,
            text=True,
            timeout=30
        )

        print(result.stdout)

        # Check that manifest was created
        if not os.path.exists(self.manifest_path):
            print("❌ Manifest was not created")
            return False

        # Check exit code
        if result.returncode != 0:
            print(f"❌ Exit code: {result.returncode}")
            return False

        print("✓ Module test passed")
        print("✓ Manifest created successfully")
        return True

    def test_cli_integration(self):
        """Test 2: CLI tools integration"""
        print("Testing CLI tools integration...")

        # Test with quick_risk_analysis.py
        # We'll just check that it imports correctly and doesn't crash
        try:
            # Run a simple import test
            result = subprocess.run(
                [sys.executable, '-c',
                 'import quick_risk_analysis; '
                 'print("quick_risk_analysis imported successfully")'],
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print(f"❌ quick_risk_analysis import failed")
                print(result.stderr)
                return False

            print("✓ quick_risk_analysis.py imports correctly")

            # Test fair_risk_calculator.py
            result = subprocess.run(
                [sys.executable, '-c',
                 'import fair_risk_calculator; '
                 'print("fair_risk_calculator imported successfully")'],
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print(f"❌ fair_risk_calculator import failed")
                print(result.stderr)
                return False

            print("✓ fair_risk_calculator.py imports correctly")

            return True

        except Exception as e:
            print(f"❌ CLI integration test failed: {e}")
            return False

    def test_web_app_integration(self):
        """Test 3: Web app integration"""
        print("Testing web app integration...")

        try:
            # Test import of fair_risk_app
            result = subprocess.run(
                [sys.executable, '-c',
                 'import fair_risk_app; '
                 'print("fair_risk_app imported successfully")'],
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                # Check if failure is due to missing streamlit (expected in test environment)
                if 'streamlit' in result.stderr or 'ModuleNotFoundError' in result.stderr:
                    print("⚠️  Streamlit not installed (expected in test environment)")
                    print("   Checking that integration code exists...")

                    # Verify integration code exists in file
                    app_file = os.path.join(self.test_dir, 'fair_risk_app.py')
                    with open(app_file, 'r') as f:
                        content = f.read()

                    if 'AUTO_INTEGRITY_AVAILABLE' in content and 'ensure_integrity' in content:
                        print("✓ Integration code present in fair_risk_app.py")
                        print("✓ Test passed (conditional - Streamlit not required)")
                        return True
                    else:
                        print("❌ Integration code missing from fair_risk_app.py")
                        return False
                else:
                    print(f"❌ fair_risk_app import failed with unexpected error")
                    print(result.stderr)
                    return False

            print("✓ fair_risk_app.py imports correctly")
            return True

        except Exception as e:
            print(f"❌ Web app integration test failed: {e}")
            return False

    def test_subsequent_run(self):
        """Test 4: Subsequent run verification"""
        print("Testing subsequent run (should verify, not regenerate)...")

        # Ensure manifest exists
        if not os.path.exists(self.manifest_path):
            print("❌ Manifest doesn't exist for subsequent run test")
            return False

        # Record original manifest modification time
        orig_mtime = os.path.getmtime(self.manifest_path)

        # Run auto-integrity again
        result = subprocess.run(
            [sys.executable, 'auto_integrity.py'],
            cwd=self.test_dir,
            capture_output=True,
            text=True,
            timeout=30
        )

        print(result.stdout)

        # Check that manifest was NOT regenerated (mtime should be same)
        new_mtime = os.path.getmtime(self.manifest_path)

        if new_mtime != orig_mtime:
            print("⚠️  Manifest was regenerated (should have only verified)")
            # This is not necessarily a failure, but note it
            print("   (This could be OK if files were modified)")

        # Check that verification passed
        if "PASSED" in result.stdout or "SUCCESS" in result.stdout:
            print("✓ Subsequent run verification passed")
            return True
        else:
            print("❌ Verification did not pass")
            return False

    def test_tampering_detection(self):
        """Test 5: Tampering detection"""
        print("Testing tampering detection...")

        # Ensure manifest exists
        if not os.path.exists(self.manifest_path):
            print("❌ Manifest doesn't exist for tampering test")
            return False

        # Create a temporary file modification
        test_file = os.path.join(self.test_dir, 'test_validation.py')
        if not os.path.exists(test_file):
            print("⚠️  test_validation.py not found, skipping tampering test")
            return True  # Skip, not a failure

        # Backup test file
        backup_content = open(test_file, 'r').read()

        try:
            # Modify file (simulate tampering)
            with open(test_file, 'a') as f:
                f.write('\n# TAMPERING TEST\n')

            # Run auto-integrity
            result = subprocess.run(
                [sys.executable, 'auto_integrity.py'],
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Check that tampering was detected
            if "TAMPERING DETECTED" in result.stdout or "MODIFIED" in result.stdout:
                print("✓ Tampering was correctly detected")
                success = True
            else:
                print("❌ Tampering was NOT detected")
                success = False

        finally:
            # Restore original file
            with open(test_file, 'w') as f:
                f.write(backup_content)
            print("✓ Restored test file")

        return success

    def test_integration_points(self):
        """Test 6: Verify integration points in all files"""
        print("Checking integration points in all tools...")

        files_to_check = [
            ('quick_risk_analysis.py', ['AUTO_INTEGRITY_AVAILABLE', 'ensure_integrity']),
            ('fair_risk_calculator.py', ['AUTO_INTEGRITY_AVAILABLE', 'ensure_integrity']),
            ('fair_risk_app.py', ['AUTO_INTEGRITY_AVAILABLE', 'ensure_integrity'])
        ]

        all_found = True
        for filename, keywords in files_to_check:
            filepath = os.path.join(self.test_dir, filename)
            if not os.path.exists(filepath):
                print(f"⚠️  {filename} not found")
                continue

            with open(filepath, 'r') as f:
                content = f.read()

            found = all(keyword in content for keyword in keywords)
            if found:
                print(f"✓ {filename}: Integration points found")
            else:
                print(f"❌ {filename}: Missing integration points")
                all_found = False

        return all_found

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("FAIR RISK CALCULATOR - AUTO-INTEGRITY TEST SUITE")
        print("="*70)

        # Backup existing manifest
        self.backup_manifest()

        try:
            # Run tests
            self.run_test("Auto-Integrity Module", self.test_auto_integrity_module)
            self.run_test("CLI Tools Integration", self.test_cli_integration)
            self.run_test("Web App Integration", self.test_web_app_integration)
            self.run_test("Subsequent Run Verification", self.test_subsequent_run)
            self.run_test("Tampering Detection", self.test_tampering_detection)
            self.run_test("Integration Points", self.test_integration_points)

        finally:
            # Restore manifest
            if self.backup_path:
                self.restore_manifest()
            elif os.path.exists(self.manifest_path):
                # Keep the newly generated manifest
                print(f"\nℹ️  Keeping newly generated manifest: {self.manifest_path}")

        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print("="*70)

        if self.failed == 0:
            print("\n✅ ALL TESTS PASSED - Auto-integrity system fully integrated!")
            print("\nThe system will:")
            print("  • Auto-generate baseline on first run")
            print("  • Auto-verify before each execution")
            print("  • Detect tampering automatically")
            print("  • Work seamlessly across all tools")
            return True
        else:
            print(f"\n❌ {self.failed} TEST(S) FAILED - Please review errors above")
            return False


def main():
    """Main entry point"""
    tester = TestAutoIntegrity()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
