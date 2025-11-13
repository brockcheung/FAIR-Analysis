"""
FAIR Risk Calculator - Runtime Integrity Checker

This module provides runtime integrity checking capabilities that can be
embedded in the core calculator modules to detect tampering before execution.

Usage:
    from integrity_checker import verify_runtime_integrity

    # At the start of your script
    if not verify_runtime_integrity():
        print("WARNING: Code integrity check failed!")
        # Take appropriate action
"""

import hashlib
import json
import os
import sys
from typing import Optional, Dict


class RuntimeIntegrityChecker:
    """Performs runtime integrity checks against baseline manifest"""

    def __init__(self, manifest_path: str = 'integrity_manifest.json', silent: bool = False, base_dir: str = '.'):
        """
        Initialize runtime integrity checker

        Args:
            manifest_path: Path to integrity manifest file
            silent: If True, suppress all output
            base_dir: Base directory for file resolution (default: current directory)
        """
        # Handle absolute vs relative manifest path
        if os.path.isabs(manifest_path):
            self.manifest_path = manifest_path
        else:
            self.manifest_path = os.path.join(base_dir, manifest_path)
        self.base_dir = base_dir
        self.silent = silent
        self.manifest = None

    def load_manifest(self) -> bool:
        """Load integrity manifest"""
        if not os.path.exists(self.manifest_path):
            if not self.silent:
                print(f"⚠️  Warning: Integrity manifest not found at {self.manifest_path}")
                print("   Run 'python generate_integrity_manifest.py' to create baseline.")
            return False

        try:
            with open(self.manifest_path, 'r') as f:
                self.manifest = json.load(f)
            return True
        except Exception as e:
            if not self.silent:
                print(f"⚠️  Warning: Failed to load integrity manifest: {e}")
            return False

    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate SHA-256 hash of a file"""
        try:
            # Resolve file path relative to base_dir if not absolute
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.base_dir, file_path)

            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return None

    def verify_file(self, file_path: str) -> bool:
        """
        Verify a single file's integrity

        Args:
            file_path: Path to the file to verify

        Returns:
            True if file is verified or not in manifest, False if tampered
        """
        if not self.manifest:
            return True  # No manifest = no verification

        # Check if file is in manifest
        if file_path not in self.manifest.get('files', {}):
            return True  # File not monitored

        expected_info = self.manifest['files'][file_path]
        expected_hash = expected_info.get('hash')

        if not expected_hash:
            return True  # No hash to verify against

        # Calculate current hash
        current_hash = self.calculate_file_hash(file_path)
        if current_hash is None:
            if not self.silent:
                print(f"⚠️  Warning: Could not verify {file_path}")
            return False

        # Compare hashes
        if current_hash != expected_hash:
            if not self.silent:
                print(f"⚠️  SECURITY ALERT: File has been modified: {file_path}")
                print(f"   Expected: {expected_hash[:32]}...")
                print(f"   Current:  {current_hash[:32]}...")
            return False

        return True

    def verify_critical_files(self, files_to_check: list = None) -> bool:
        """
        Verify critical files before execution

        Args:
            files_to_check: List of files to verify (default: all monitored files)

        Returns:
            True if all files verified, False if any tampering detected
        """
        if not self.load_manifest():
            # No manifest - return True but with warning
            return True

        if files_to_check is None:
            files_to_check = list(self.manifest.get('files', {}).keys())

        all_verified = True
        for file_path in files_to_check:
            if not self.verify_file(file_path):
                all_verified = False

        return all_verified


def verify_runtime_integrity(
    files: list = None,
    strict: bool = False,
    silent: bool = False
) -> bool:
    """
    Convenience function to verify runtime integrity

    Args:
        files: List of specific files to check (default: critical files)
        strict: If True, exit program if tampering detected
        silent: If True, suppress warnings

    Returns:
        True if integrity verified, False if tampering detected

    Example:
        # Check integrity at program startup
        if not verify_runtime_integrity(['fair_risk_calculator.py'], strict=True):
            sys.exit(1)
    """
    checker = RuntimeIntegrityChecker(silent=silent)

    # Default critical files
    if files is None:
        files = [
            'fair_risk_calculator.py',
            'quick_risk_analysis.py',
            'fair_risk_app.py'
        ]

    verified = checker.verify_critical_files(files)

    if not verified and strict:
        print("\n" + "="*70)
        print("CRITICAL SECURITY ERROR: Code tampering detected!")
        print("="*70)
        print("The application has been modified and may not be safe to execute.")
        print("Please restore from a trusted backup or contact your administrator.")
        print("="*70)
        sys.exit(1)

    return verified


def generate_file_signature(file_path: str) -> Optional[str]:
    """
    Generate SHA-256 signature for a single file

    Args:
        file_path: Path to the file

    Returns:
        SHA-256 hash string or None if error

    Example:
        sig = generate_file_signature('fair_risk_calculator.py')
        print(f"File signature: {sig}")
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b''):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error generating signature for {file_path}: {e}")
        return None


def compare_signatures(file_path: str, expected_signature: str) -> bool:
    """
    Compare a file's current signature with expected signature

    Args:
        file_path: Path to the file
        expected_signature: Expected SHA-256 hash

    Returns:
        True if signatures match, False otherwise

    Example:
        if not compare_signatures('setup.py', expected_hash):
            print("File has been modified!")
    """
    current_signature = generate_file_signature(file_path)
    if current_signature is None:
        return False
    return current_signature == expected_signature


# Self-test
if __name__ == '__main__':
    print("="*70)
    print("Runtime Integrity Checker - Self Test")
    print("="*70)

    checker = RuntimeIntegrityChecker()

    if not checker.load_manifest():
        print("\n❌ No integrity manifest found.")
        print("   Please run: python generate_integrity_manifest.py")
        sys.exit(1)

    print(f"\n✅ Manifest loaded successfully")
    print(f"   Files monitored: {len(checker.manifest['files'])}")
    print(f"   Created: {checker.manifest.get('generated_at', 'Unknown')}")

    print("\nVerifying critical files...")
    result = checker.verify_critical_files()

    if result:
        print("\n✅ SUCCESS: All files verified")
    else:
        print("\n❌ FAILURE: Tampering detected")

    sys.exit(0 if result else 1)
