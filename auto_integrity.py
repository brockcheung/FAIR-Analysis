"""
FAIR Risk Calculator - Automatic Integrity Protection

This module provides automatic integrity checking that:
1. Auto-generates integrity baseline on first run
2. Auto-verifies on subsequent runs
3. Seamlessly integrates into all tools

Usage:
    from auto_integrity import ensure_integrity

    # At the start of your script
    if not ensure_integrity():
        print("Security check failed!")
        sys.exit(1)
"""

import os
import sys
from typing import Optional, Tuple
from generate_integrity_manifest import IntegrityManifestGenerator
from integrity_checker import RuntimeIntegrityChecker


class AutoIntegrity:
    """Handles automatic integrity generation and verification"""

    def __init__(self,
                 manifest_name: str = 'integrity_manifest.json',
                 auto_generate: bool = True,
                 strict: bool = False,
                 silent: bool = False):
        """
        Initialize auto-integrity system

        Args:
            manifest_name: Name of the manifest file
            auto_generate: If True, auto-generate on first run
            strict: If True, exit program on verification failure
            silent: If True, suppress informational messages (warnings still shown)
        """
        self.manifest_name = manifest_name
        self.auto_generate = auto_generate
        self.strict = strict
        self.silent = silent

        # Determine base directory (where the script is located)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.manifest_path = os.path.join(self.base_dir, manifest_name)

    def manifest_exists(self) -> bool:
        """Check if integrity manifest exists"""
        return os.path.exists(self.manifest_path)

    def generate_manifest(self) -> bool:
        """
        Generate integrity manifest automatically

        Returns:
            True if generation successful, False otherwise
        """
        try:
            if not self.silent:
                print("\n" + "="*70)
                print("🔒 FIRST RUN DETECTED - Establishing Security Baseline")
                print("="*70)
                print("Generating cryptographic integrity baseline...")
                print("This protects your FAIR Risk Calculator from tampering.")

            # Create generator
            generator = IntegrityManifestGenerator(base_dir=self.base_dir)

            # Generate manifest (suppress detailed output if silent)
            if self.silent:
                # Redirect stdout temporarily
                import io
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()

            manifest = generator.generate_manifest(include_additional=True)
            generator.manifest = manifest
            generator.save_manifest(self.manifest_name)

            if self.silent:
                sys.stdout = old_stdout

            if not self.silent:
                print("\n✅ Security baseline established successfully!")
                print(f"   Files monitored: {len(manifest['files'])}")
                print(f"   Manifest saved: {self.manifest_name}")
                print("\nYour FAIR Risk Calculator is now protected against tampering.")
                print("="*70 + "\n")

            return True

        except Exception as e:
            if not self.silent:
                print(f"\n⚠️  Warning: Failed to generate integrity baseline: {e}")
                print("Continuing without integrity protection...")
            return False

    def verify_integrity(self) -> Tuple[bool, str]:
        """
        Verify integrity against existing manifest

        Returns:
            Tuple of (success, message)
        """
        try:
            # Create checker
            checker = RuntimeIntegrityChecker(
                manifest_path=self.manifest_path,
                silent=True,  # We'll handle our own messaging
                base_dir=self.base_dir
            )

            # Load manifest
            if not checker.load_manifest():
                return False, "Failed to load integrity manifest"

            # Verify all critical files
            verified = checker.verify_critical_files()

            if verified:
                if not self.silent:
                    print("🔒 Security Check: ✅ PASSED - Code integrity verified")
                return True, "All files verified successfully"
            else:
                return False, "Code tampering detected"

        except Exception as e:
            return False, f"Verification error: {e}"

    def run(self) -> bool:
        """
        Main entry point - handles auto-generation and verification

        Returns:
            True if integrity check passed or was generated, False if failed
        """
        # Check if manifest exists
        if not self.manifest_exists():
            # First run - generate manifest
            if self.auto_generate:
                if not self.generate_manifest():
                    if not self.strict:
                        return True  # Continue without protection
                    else:
                        return False  # Strict mode - fail if can't generate
                return True  # Successfully generated
            else:
                if not self.silent:
                    print("⚠️  Warning: No integrity baseline found")
                    print("   Run: python generate_integrity_manifest.py")
                return True  # Continue without protection

        # Subsequent runs - verify integrity
        success, message = self.verify_integrity()

        if not success:
            # Always show alert if not in silent mode
            if not self.silent:
                print("\n" + "="*70)
                print("⚠️  SECURITY ALERT: CODE TAMPERING DETECTED!")
                print("="*70)
                print(f"Details: {message}")
                print("\nThe FAIR Risk Calculator has been modified since the baseline")
                print("was established. This could indicate:")
                print("  • Malicious tampering by an adversary")
                print("  • Accidental modification")
                print("  • Legitimate update without regenerating baseline")
                print("\nRecommended actions:")
                print("  1. If you made legitimate changes:")
                print("     python generate_integrity_manifest.py")
                print("  2. If you did NOT make changes:")
                print("     Restore from backup and investigate")
                print("  3. For more details:")
                print("     python verify_integrity.py --verbose")
                print("="*70 + "\n")

            if self.strict:
                if not self.silent:
                    print("❌ STRICT MODE: Exiting due to integrity failure")
                return False
            else:
                if not self.silent:
                    print("⚠️  WARNING MODE: Continuing despite integrity failure")
                    print("   (Results may not be trustworthy)")
                # Return False to indicate tampering detected, even in warning mode
                # The caller can decide whether to continue or not
                return False

        return True


def ensure_integrity(auto_generate: bool = True,
                    strict: bool = False,
                    silent: bool = False) -> bool:
    """
    Convenience function to ensure code integrity

    This function should be called at the start of your script to:
    1. Auto-generate integrity baseline on first run
    2. Auto-verify on subsequent runs

    Args:
        auto_generate: Auto-generate manifest on first run (default: True)
        strict: Exit if integrity check fails (default: False)
        silent: Suppress informational messages (default: False)

    Returns:
        True if integrity check passed, False if failed

    Example:
        from auto_integrity import ensure_integrity

        # At start of script
        if not ensure_integrity(strict=True):
            sys.exit(1)
    """
    auto = AutoIntegrity(
        auto_generate=auto_generate,
        strict=strict,
        silent=silent
    )
    return auto.run()


def ensure_integrity_silent() -> bool:
    """
    Silent mode - no output except critical warnings
    Useful for background processes or when output needs to be clean

    Returns:
        True if integrity check passed, False if failed
    """
    return ensure_integrity(auto_generate=True, strict=False, silent=True)


def ensure_integrity_strict() -> bool:
    """
    Strict mode - exits immediately if integrity check fails
    Recommended for production environments

    Returns:
        True if integrity check passed, False if failed (will exit on failure)
    """
    return ensure_integrity(auto_generate=True, strict=True, silent=False)


# Self-test
if __name__ == '__main__':
    print("="*70)
    print("Auto-Integrity System - Self Test")
    print("="*70)
    print("\nThis test will demonstrate the auto-integrity system:\n")

    # Test 1: Check current state
    auto = AutoIntegrity(silent=False)

    if auto.manifest_exists():
        print("ℹ️  Existing manifest detected")
        print(f"   Location: {auto.manifest_path}")
    else:
        print("ℹ️  No manifest detected - will auto-generate")

    print("\n" + "-"*70)
    print("Running auto-integrity check...")
    print("-"*70)

    # Test 2: Run auto-integrity
    result = ensure_integrity(auto_generate=True, strict=False, silent=False)

    print("\n" + "="*70)
    print("SELF TEST RESULT")
    print("="*70)

    if result:
        print("✅ SUCCESS: Auto-integrity system working correctly")
        print("\nThe system will:")
        print("  • Auto-generate baseline on first run")
        print("  • Auto-verify on subsequent runs")
        print("  • Alert on tampering detection")
    else:
        print("❌ FAILURE: Auto-integrity check failed")
        print("\nPlease investigate the issue")

    print("="*70)

    sys.exit(0 if result else 1)
