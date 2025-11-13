#!/usr/bin/env python3
"""
Test Suite for Integrity Protection System

This script validates that the integrity protection system correctly:
1. Generates valid manifests
2. Detects file modifications
3. Handles missing files
4. Works with the runtime checker

Usage:
    python test_integrity_system.py
"""

import json
import os
import sys
import tempfile
import shutil
from generate_integrity_manifest import IntegrityManifestGenerator
from verify_integrity import IntegrityVerifier
from integrity_checker import RuntimeIntegrityChecker


class TestIntegritySystem:
    """Test the integrity protection system"""

    def __init__(self):
        self.test_dir = None
        self.passed = 0
        self.failed = 0

    def setup(self):
        """Create temporary test directory"""
        self.test_dir = tempfile.mkdtemp(prefix='fair_integrity_test_')
        print(f"Test directory: {self.test_dir}")

        # Create test files
        test_files = {
            'test_file1.py': b'print("Hello World")',
            'test_file2.py': b'def calculate(x): return x * 2',
            'test_file3.py': b'import os\nprint(os.getcwd())',
        }

        for filename, content in test_files.items():
            with open(os.path.join(self.test_dir, filename), 'wb') as f:
                f.write(content)

    def teardown(self):
        """Clean up test directory"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"Cleaned up: {self.test_dir}")

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

    def test_manifest_generation(self):
        """Test 1: Manifest generation creates valid JSON"""
        # Create a minimal generator (override critical files)
        generator = IntegrityManifestGenerator(base_dir=self.test_dir)
        generator.CRITICAL_FILES = ['test_file1.py', 'test_file2.py']
        generator.ADDITIONAL_FILES = ['test_file3.py']

        manifest = generator.generate_manifest(include_additional=True)

        # Verify manifest structure
        assert 'version' in manifest, "Manifest missing version"
        assert 'generated_at' in manifest, "Manifest missing timestamp"
        assert 'algorithm' in manifest, "Manifest missing algorithm"
        assert 'files' in manifest, "Manifest missing files"
        assert manifest['algorithm'] == 'SHA-256', "Wrong algorithm"

        # Verify files are present
        assert 'test_file1.py' in manifest['files'], "test_file1.py not in manifest"
        assert 'test_file2.py' in manifest['files'], "test_file2.py not in manifest"
        assert 'test_file3.py' in manifest['files'], "test_file3.py not in manifest"

        # Verify hashes exist
        assert manifest['files']['test_file1.py']['hash'] is not None, "Missing hash"

        print("✓ Manifest structure is valid")
        print(f"✓ Files monitored: {len(manifest['files'])}")
        print(f"✓ Algorithm: {manifest['algorithm']}")

        return True

    def test_hash_calculation(self):
        """Test 2: SHA-256 hashes are calculated correctly"""
        import hashlib

        # Create generator
        generator = IntegrityManifestGenerator(base_dir=self.test_dir)

        # Calculate hash for test_file1.py
        test_file = os.path.join(self.test_dir, 'test_file1.py')
        calculated_hash = generator.calculate_file_hash(test_file)

        # Calculate expected hash
        with open(test_file, 'rb') as f:
            expected_hash = hashlib.sha256(f.read()).hexdigest()

        assert calculated_hash == expected_hash, f"Hash mismatch: {calculated_hash} != {expected_hash}"

        print(f"✓ Hash calculated correctly: {calculated_hash[:16]}...{calculated_hash[-16:]}")

        return True

    def test_verification_success(self):
        """Test 3: Verification succeeds for unmodified files"""
        # Generate manifest
        generator = IntegrityManifestGenerator(base_dir=self.test_dir)
        generator.CRITICAL_FILES = ['test_file1.py', 'test_file2.py']
        generator.ADDITIONAL_FILES = []

        manifest = generator.generate_manifest(include_additional=False)
        manifest_file = os.path.join(self.test_dir, 'integrity_manifest.json')
        generator.manifest = manifest
        generator.save_manifest(manifest_file)

        # Verify
        verifier = IntegrityVerifier(manifest_file, base_dir=self.test_dir)
        success = verifier.verify_all(verbose=False)

        assert success, "Verification should succeed for unmodified files"
        assert len(verifier.verification_results['verified']) == 2, "Should verify 2 files"
        assert len(verifier.verification_results['modified']) == 0, "Should have no modified files"

        print("✓ Verification succeeded for unmodified files")
        print(f"✓ Verified files: {len(verifier.verification_results['verified'])}")

        return True

    def test_tampering_detection(self):
        """Test 4: Verification detects modified files"""
        # Generate manifest
        generator = IntegrityManifestGenerator(base_dir=self.test_dir)
        generator.CRITICAL_FILES = ['test_file1.py']
        generator.ADDITIONAL_FILES = []

        manifest = generator.generate_manifest(include_additional=False)
        manifest_file = os.path.join(self.test_dir, 'integrity_manifest.json')
        generator.manifest = manifest
        generator.save_manifest(manifest_file)

        # Modify file (simulate tampering)
        test_file = os.path.join(self.test_dir, 'test_file1.py')
        with open(test_file, 'w') as f:
            f.write('print("TAMPERED!")  # Malicious code')

        # Verify (should detect tampering)
        verifier = IntegrityVerifier(manifest_file, base_dir=self.test_dir)
        success = verifier.verify_all(verbose=False)

        assert not success, "Verification should fail for modified files"
        assert len(verifier.verification_results['modified']) == 1, "Should detect 1 modified file"
        assert verifier.verification_results['modified'][0]['file'] == 'test_file1.py', "Wrong file detected"

        print("✓ Tampering detected successfully")
        print(f"✓ Modified files: {verifier.verification_results['modified'][0]['file']}")

        return True

    def test_missing_file_detection(self):
        """Test 5: Verification detects missing files"""
        # Generate manifest
        generator = IntegrityManifestGenerator(base_dir=self.test_dir)
        generator.CRITICAL_FILES = ['test_file1.py', 'test_file2.py']
        generator.ADDITIONAL_FILES = []

        manifest = generator.generate_manifest(include_additional=False)
        manifest_file = os.path.join(self.test_dir, 'integrity_manifest.json')
        generator.manifest = manifest
        generator.save_manifest(manifest_file)

        # Delete file (simulate deletion)
        test_file = os.path.join(self.test_dir, 'test_file2.py')
        os.remove(test_file)

        # Verify (should detect missing file)
        verifier = IntegrityVerifier(manifest_file, base_dir=self.test_dir)
        success = verifier.verify_all(verbose=False)

        assert not success, "Verification should fail for missing files"
        assert len(verifier.verification_results['missing']) == 1, "Should detect 1 missing file"
        assert 'test_file2.py' in verifier.verification_results['missing'], "Wrong file detected"

        print("✓ Missing file detected successfully")
        print(f"✓ Missing files: {verifier.verification_results['missing']}")

        return True

    def test_runtime_checker(self):
        """Test 6: Runtime integrity checker works"""
        # Generate manifest
        generator = IntegrityManifestGenerator(base_dir=self.test_dir)
        generator.CRITICAL_FILES = ['test_file1.py']
        generator.ADDITIONAL_FILES = []

        manifest = generator.generate_manifest(include_additional=False)
        manifest_file = os.path.join(self.test_dir, 'integrity_manifest.json')
        generator.manifest = manifest
        generator.save_manifest(manifest_file)

        # Test runtime checker
        checker = RuntimeIntegrityChecker(manifest_file, base_dir=self.test_dir, silent=True)
        result = checker.load_manifest()

        assert result, "Should load manifest successfully"
        assert checker.manifest is not None, "Manifest should be loaded"

        # Verify file
        file_verified = checker.verify_file('test_file1.py')
        assert file_verified, "File should be verified"

        print("✓ Runtime checker loaded manifest")
        print("✓ Runtime checker verified file")

        return True

    def test_hash_consistency(self):
        """Test 7: Hash calculation is consistent"""
        generator = IntegrityManifestGenerator(base_dir=self.test_dir)
        test_file = os.path.join(self.test_dir, 'test_file1.py')

        # Calculate hash multiple times
        hash1 = generator.calculate_file_hash(test_file)
        hash2 = generator.calculate_file_hash(test_file)
        hash3 = generator.calculate_file_hash(test_file)

        assert hash1 == hash2 == hash3, "Hashes should be consistent"

        print(f"✓ Hash calculation is consistent: {hash1[:16]}...")

        return True

    def test_manifest_persistence(self):
        """Test 8: Manifest can be saved and loaded"""
        # Generate and save manifest
        generator = IntegrityManifestGenerator(base_dir=self.test_dir)
        generator.CRITICAL_FILES = ['test_file1.py']
        generator.ADDITIONAL_FILES = []

        manifest = generator.generate_manifest(include_additional=False)
        manifest_file = os.path.join(self.test_dir, 'integrity_manifest.json')
        generator.manifest = manifest
        generator.save_manifest(manifest_file)

        # Load manifest
        with open(manifest_file, 'r') as f:
            loaded_manifest = json.load(f)

        assert loaded_manifest['version'] == manifest['version'], "Version mismatch"
        assert loaded_manifest['algorithm'] == manifest['algorithm'], "Algorithm mismatch"
        assert len(loaded_manifest['files']) == len(manifest['files']), "File count mismatch"

        print("✓ Manifest saved and loaded successfully")
        print(f"✓ Files in manifest: {len(loaded_manifest['files'])}")

        return True

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("FAIR RISK CALCULATOR - INTEGRITY SYSTEM TEST SUITE")
        print("="*70)

        # Setup
        self.setup()

        # Run tests
        self.run_test("Manifest Generation", self.test_manifest_generation)
        self.run_test("Hash Calculation", self.test_hash_calculation)
        self.run_test("Verification Success", self.test_verification_success)
        self.run_test("Tampering Detection", self.test_tampering_detection)
        self.run_test("Missing File Detection", self.test_missing_file_detection)
        self.run_test("Runtime Checker", self.test_runtime_checker)
        self.run_test("Hash Consistency", self.test_hash_consistency)
        self.run_test("Manifest Persistence", self.test_manifest_persistence)

        # Teardown
        self.teardown()

        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print("="*70)

        if self.failed == 0:
            print("\n✅ ALL TESTS PASSED - Integrity system is working correctly!")
            return True
        else:
            print(f"\n❌ {self.failed} TEST(S) FAILED - Please review errors above")
            return False


def main():
    """Main entry point"""
    tester = TestIntegritySystem()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
