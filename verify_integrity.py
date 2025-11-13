#!/usr/bin/env python3
"""
FAIR Risk Calculator - Integrity Verification Tool

This script verifies the integrity of critical files by comparing their current
SHA-256 hashes against the baseline stored in integrity_manifest.json.

Usage:
    python verify_integrity.py [--verbose] [--strict]

Options:
    --verbose: Show detailed information for all files
    --strict: Exit with error code if any tampering detected

Exit Codes:
    0: All files verified successfully
    1: Tampering detected or verification failed
    2: Manifest file missing or invalid
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple


class IntegrityVerifier:
    """Verifies code integrity against baseline manifest"""

    def __init__(self, manifest_file: str = 'integrity_manifest.json', base_dir: str = '.'):
        """
        Initialize the integrity verifier

        Args:
            manifest_file: Path to the integrity manifest file
            base_dir: Base directory of the project
        """
        self.manifest_file = os.path.join(base_dir, manifest_file)
        self.base_dir = base_dir
        self.manifest = None
        self.verification_results = {
            'verified': [],
            'modified': [],
            'missing': [],
            'new_files': [],
            'errors': []
        }

    def load_manifest(self) -> bool:
        """
        Load the integrity manifest

        Returns:
            True if manifest loaded successfully, False otherwise
        """
        if not os.path.exists(self.manifest_file):
            print(f"❌ ERROR: Manifest file not found: {self.manifest_file}")
            print("\nPlease run 'python generate_integrity_manifest.py' first.")
            return False

        try:
            with open(self.manifest_file, 'r') as f:
                self.manifest = json.load(f)
            return True
        except json.JSONDecodeError as e:
            print(f"❌ ERROR: Invalid manifest file format: {e}")
            return False
        except Exception as e:
            print(f"❌ ERROR: Failed to load manifest: {e}")
            return False

    def calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file

        Args:
            file_path: Path to the file

        Returns:
            Hexadecimal SHA-256 hash string
        """
        sha256_hash = hashlib.sha256()

        try:
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error hashing {file_path}: {e}")
            return None

    def verify_file(self, file_path: str, expected_info: Dict) -> Tuple[str, Dict]:
        """
        Verify a single file against its expected hash

        Args:
            file_path: Path to the file
            expected_info: Expected file information from manifest

        Returns:
            Tuple of (status, details) where status is 'verified', 'modified', 'missing', or 'error'
        """
        full_path = os.path.join(self.base_dir, file_path)

        # Check if file exists
        if not os.path.exists(full_path):
            if expected_info['status'] == 'missing':
                return 'verified', {'note': 'File was already missing in baseline'}
            return 'missing', {'expected': expected_info['hash'], 'current': None}

        # Calculate current hash
        current_hash = self.calculate_file_hash(full_path)
        if current_hash is None:
            return 'error', {'message': 'Failed to calculate hash'}

        # Compare hashes
        expected_hash = expected_info.get('hash')
        if current_hash == expected_hash:
            return 'verified', {
                'hash': current_hash,
                'size': os.path.getsize(full_path)
            }
        else:
            return 'modified', {
                'expected': expected_hash,
                'current': current_hash,
                'size': os.path.getsize(full_path)
            }

    def verify_all(self, verbose: bool = False) -> bool:
        """
        Verify all files in the manifest

        Args:
            verbose: Show detailed information for all files

        Returns:
            True if all files verified successfully, False if tampering detected
        """
        # Auto-load manifest if not already loaded
        if not self.manifest:
            if not self.load_manifest():
                return False

        print("="*70)
        print("FAIR Risk Calculator - Integrity Verification")
        print("="*70)
        print(f"Manifest created: {self.manifest.get('generated_at', 'Unknown')}")
        print(f"Hash algorithm: {self.manifest.get('algorithm', 'Unknown')}")
        print(f"Files to verify: {len(self.manifest['files'])}")
        print("="*70)

        # Verify each file
        for file_path, expected_info in sorted(self.manifest['files'].items()):
            status, details = self.verify_file(file_path, expected_info)

            # Categorize results
            if status == 'verified':
                self.verification_results['verified'].append(file_path)
                if verbose:
                    print(f"✅ VERIFIED: {file_path}")
            elif status == 'modified':
                self.verification_results['modified'].append({
                    'file': file_path,
                    'details': details
                })
                print(f"⚠️  MODIFIED: {file_path}")
                print(f"   Expected: {details['expected']}")
                print(f"   Current:  {details['current']}")
            elif status == 'missing':
                self.verification_results['missing'].append(file_path)
                print(f"❌ MISSING: {file_path}")
            elif status == 'error':
                self.verification_results['errors'].append({
                    'file': file_path,
                    'details': details
                })
                print(f"⚠️  ERROR: {file_path} - {details.get('message', 'Unknown error')}")

        # Check for tampering
        tampering_detected = (
            len(self.verification_results['modified']) > 0 or
            len(self.verification_results['missing']) > 0
        )

        return not tampering_detected

    def print_summary(self):
        """Print verification summary"""
        total_files = len(self.manifest['files']) if self.manifest else 0
        verified_count = len(self.verification_results['verified'])
        modified_count = len(self.verification_results['modified'])
        missing_count = len(self.verification_results['missing'])
        error_count = len(self.verification_results['errors'])

        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        print(f"Total files checked: {total_files}")
        print(f"✅ Verified: {verified_count}")
        print(f"⚠️  Modified: {modified_count}")
        print(f"❌ Missing: {missing_count}")
        print(f"⚠️  Errors: {error_count}")
        print("="*70)

        if modified_count > 0 or missing_count > 0:
            print("\n⚠️  WARNING: CODE TAMPERING DETECTED!")
            print("="*70)
            print("CRITICAL SECURITY ALERT")
            print("="*70)
            print("\nUnauthorized modifications have been detected in the codebase.")
            print("\nPossible causes:")
            print("  1. Malicious tampering by an adversary")
            print("  2. Accidental modification by a user")
            print("  3. Legitimate update without regenerating manifest")
            print("\nRecommended actions:")
            print("  1. Do NOT run the modified code")
            print("  2. Investigate the source of modifications")
            print("  3. Restore from a trusted backup if tampering is confirmed")
            print("  4. If changes are legitimate, regenerate the manifest:")
            print("     python generate_integrity_manifest.py")
            print("="*70)
            return False
        else:
            print("\n✅ SUCCESS: All files verified - No tampering detected")
            print("\nThe codebase integrity is intact. Safe to execute.")
            return True

    def save_verification_report(self, output_file: str = 'integrity_verification_report.json'):
        """
        Save verification results to a JSON report

        Args:
            output_file: Output file path
        """
        report = {
            'verification_time': datetime.now().isoformat(),
            'manifest_date': self.manifest.get('generated_at') if self.manifest else None,
            'results': self.verification_results,
            'summary': {
                'total': len(self.manifest['files']) if self.manifest else 0,
                'verified': len(self.verification_results['verified']),
                'modified': len(self.verification_results['modified']),
                'missing': len(self.verification_results['missing']),
                'errors': len(self.verification_results['errors'])
            },
            'tampering_detected': (
                len(self.verification_results['modified']) > 0 or
                len(self.verification_results['missing']) > 0
            )
        }

        output_path = os.path.join(self.base_dir, output_file)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Verification report saved to: {output_file}")


def main():
    """Main entry point"""
    # Parse command line arguments
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    strict = '--strict' in sys.argv
    save_report = '--report' in sys.argv

    # Create verifier and load manifest
    verifier = IntegrityVerifier()

    if not verifier.load_manifest():
        sys.exit(2)

    # Verify all files
    all_verified = verifier.verify_all(verbose=verbose)

    # Print summary
    success = verifier.print_summary()

    # Save report if requested
    if save_report:
        verifier.save_verification_report()

    # Exit with appropriate code
    if strict and not all_verified:
        sys.exit(1)
    elif not success:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
