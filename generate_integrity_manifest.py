#!/usr/bin/env python3
"""
FAIR Risk Calculator - Integrity Manifest Generator

This script generates cryptographic hashes (SHA-256) of all critical files
to create an integrity baseline. The manifest can be used to detect unauthorized
modifications to the codebase.

Usage:
    python generate_integrity_manifest.py

Output:
    integrity_manifest.json - Contains SHA-256 hashes of all critical files
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List


class IntegrityManifestGenerator:
    """Generates cryptographic hashes for code integrity verification"""

    # Critical files that should be monitored for tampering
    CRITICAL_FILES = [
        'fair_risk_calculator.py',
        'quick_risk_analysis.py',
        'fair_risk_app.py',
        'setup.py',
        'requirements.txt',
    ]

    # Additional files to monitor
    ADDITIONAL_FILES = [
        'test_validation.py',
        'test_mathematical_correctness.py',
        'Dockerfile',
        'docker-compose.yml',
    ]

    def __init__(self, base_dir: str = '.'):
        """
        Initialize the manifest generator

        Args:
            base_dir: Base directory of the project (default: current directory)
        """
        self.base_dir = base_dir
        self.manifest = {
            'version': '1.0',
            'generated_at': None,
            'algorithm': 'SHA-256',
            'files': {},
            'metadata': {
                'generator': 'FAIR Risk Calculator Integrity System',
                'purpose': 'Detect unauthorized code modifications'
            }
        }

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
                # Read file in chunks to handle large files efficiently
                for byte_block in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error hashing {file_path}: {e}")
            return None

    def get_file_info(self, file_path: str) -> Dict:
        """
        Get detailed information about a file

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing file hash, size, and modification time
        """
        full_path = os.path.join(self.base_dir, file_path)

        if not os.path.exists(full_path):
            return {
                'status': 'missing',
                'hash': None,
                'size': None,
                'modified': None
            }

        file_hash = self.calculate_file_hash(full_path)
        file_stat = os.stat(full_path)

        return {
            'status': 'present',
            'hash': file_hash,
            'size': file_stat.st_size,
            'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            'path': file_path
        }

    def generate_manifest(self, include_additional: bool = True) -> Dict:
        """
        Generate complete integrity manifest

        Args:
            include_additional: Include additional (non-critical) files

        Returns:
            Complete manifest dictionary
        """
        self.manifest['generated_at'] = datetime.now().isoformat()

        # Process critical files
        print("Generating integrity manifest...")
        print("\nCritical Files:")
        for file_path in self.CRITICAL_FILES:
            file_info = self.get_file_info(file_path)
            self.manifest['files'][file_path] = file_info

            status_icon = "✅" if file_info['status'] == 'present' else "❌"
            print(f"  {status_icon} {file_path}")
            if file_info['hash']:
                print(f"     SHA-256: {file_info['hash'][:16]}...{file_info['hash'][-16:]}")

        # Process additional files if requested
        if include_additional:
            print("\nAdditional Files:")
            for file_path in self.ADDITIONAL_FILES:
                file_info = self.get_file_info(file_path)
                self.manifest['files'][file_path] = file_info

                status_icon = "✅" if file_info['status'] == 'present' else "❌"
                print(f"  {status_icon} {file_path}")

        return self.manifest

    def save_manifest(self, output_file: str = 'integrity_manifest.json'):
        """
        Save manifest to JSON file

        Args:
            output_file: Output file path (default: integrity_manifest.json)
        """
        output_path = os.path.join(self.base_dir, output_file)

        with open(output_path, 'w') as f:
            json.dump(self.manifest, f, indent=2, sort_keys=True)

        print(f"\n✅ Integrity manifest saved to: {output_file}")
        print(f"   Total files monitored: {len(self.manifest['files'])}")
        print(f"   Generated at: {self.manifest['generated_at']}")

    def print_summary(self):
        """Print summary of generated manifest"""
        total_files = len(self.manifest['files'])
        present_files = sum(1 for f in self.manifest['files'].values() if f['status'] == 'present')
        missing_files = total_files - present_files

        print("\n" + "="*60)
        print("INTEGRITY MANIFEST SUMMARY")
        print("="*60)
        print(f"Total files monitored: {total_files}")
        print(f"Files present: {present_files}")
        print(f"Files missing: {missing_files}")
        print(f"Hash algorithm: {self.manifest['algorithm']}")
        print("="*60)


def main():
    """Main entry point"""
    print("="*60)
    print("FAIR Risk Calculator - Integrity Manifest Generator")
    print("="*60)
    print("\nThis tool creates a cryptographic baseline of all critical files.")
    print("Use verify_integrity.py to check for unauthorized modifications.\n")

    # Generate manifest
    generator = IntegrityManifestGenerator()
    generator.generate_manifest(include_additional=True)
    generator.save_manifest()
    generator.print_summary()

    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("   1. Store integrity_manifest.json in a secure location")
    print("   2. Protect this file with read-only permissions")
    print("   3. Consider storing a backup offline or in version control")
    print("   4. Re-generate after any authorized code updates")
    print("\n✅ Integrity baseline established successfully!")


if __name__ == '__main__':
    main()
