# FAIR Risk Calculator - Security Guide

## Code Integrity Protection System

This document describes the code integrity protection mechanisms implemented in the FAIR Risk Calculator to prevent unauthorized modifications and ensure the tool performs accurate, trustworthy risk assessments.

---

## Table of Contents

1. [Overview](#overview)
2. [Threat Model](#threat-model)
3. [Integrity Protection System](#integrity-protection-system)
4. [Setup and Usage](#setup-and-usage)
5. [Integration with Applications](#integration-with-applications)
6. [Best Practices](#best-practices)
7. [Incident Response](#incident-response)
8. [Advanced Security](#advanced-security)

---

## Overview

### Why Code Integrity Matters

The FAIR Risk Calculator performs critical quantitative risk analysis for organizations. If an adversary modifies the code, they could:

- **Manipulate risk calculations** to underestimate threats
- **Inject malicious code** to exfiltrate sensitive risk data
- **Alter validation logic** to accept invalid scenarios
- **Compromise decision-making** based on incorrect risk assessments

### Protection Mechanisms

This tool implements **cryptographic integrity verification** using SHA-256 hashing to:

1. **Detect unauthorized modifications** to critical files
2. **Establish a trusted baseline** for code verification
3. **Provide runtime checks** before execution
4. **Generate audit trails** of verification results

---

## Threat Model

### Threats Protected Against

✅ **Local file tampering** - Adversary modifies files on disk
✅ **Insider threats** - Unauthorized changes by users with access
✅ **Accidental modifications** - Unintentional code changes
✅ **Supply chain attacks** - Modified dependencies (partial)

### Threats NOT Protected Against

❌ **Memory-based attacks** - Runtime code injection
❌ **Compiler/interpreter compromise** - Python itself is compromised
❌ **Privileged attackers** - Root/admin can bypass file protections
❌ **Advanced persistent threats** - Sophisticated rootkit-level attacks

### Risk Mitigation Strategy

This system provides **detection** capabilities, not prevention. It alerts you to tampering so you can:

1. Investigate the source of modifications
2. Restore from trusted backups
3. Implement additional security controls
4. Update your incident response procedures

---

## Integrity Protection System

### Components

#### 1. Manifest Generator (`generate_integrity_manifest.py`)

**Purpose:** Creates a cryptographic baseline of all critical files

**Usage:**
```bash
python generate_integrity_manifest.py
```

**Output:** `integrity_manifest.json` containing:
- SHA-256 hashes of all monitored files
- File sizes and modification times
- Generation timestamp
- Metadata about the baseline

**Critical Files Monitored:**
- `fair_risk_calculator.py` - Core calculator
- `quick_risk_analysis.py` - Quick CLI tool
- `fair_risk_app.py` - Web application
- `setup.py` - Installation configuration
- `requirements.txt` - Dependencies

**Additional Files Monitored:**
- `test_validation.py` - Validation tests
- `test_mathematical_correctness.py` - Mathematical tests
- `Dockerfile` - Container definition
- `docker-compose.yml` - Docker orchestration

#### 2. Integrity Verifier (`verify_integrity.py`)

**Purpose:** Verifies current files against the baseline manifest

**Usage:**
```bash
# Basic verification
python verify_integrity.py

# Verbose output (show all files)
python verify_integrity.py --verbose

# Strict mode (exit with error if tampering detected)
python verify_integrity.py --strict

# Generate verification report
python verify_integrity.py --report
```

**Exit Codes:**
- `0` - All files verified successfully
- `1` - Tampering detected or verification failed
- `2` - Manifest file missing or invalid

**Output:**
```
======================================================================
FAIR Risk Calculator - Integrity Verification
======================================================================
Manifest created: 2025-11-13T10:30:45.123456
Hash algorithm: SHA-256
Files to verify: 9
======================================================================
✅ VERIFIED: fair_risk_calculator.py
✅ VERIFIED: quick_risk_analysis.py
✅ VERIFIED: fair_risk_app.py
...
======================================================================
VERIFICATION SUMMARY
======================================================================
Total files checked: 9
✅ Verified: 9
⚠️  Modified: 0
❌ Missing: 0
⚠️  Errors: 0
======================================================================

✅ SUCCESS: All files verified - No tampering detected
```

#### 3. Runtime Integrity Checker (`integrity_checker.py`)

**Purpose:** Provides runtime verification for integration into applications

**Usage in Python code:**
```python
from integrity_checker import verify_runtime_integrity

# Option 1: Basic check (warnings only)
if not verify_runtime_integrity():
    print("WARNING: Code integrity check failed!")

# Option 2: Strict mode (exits if tampering detected)
verify_runtime_integrity(strict=True)

# Option 3: Check specific files
verify_runtime_integrity(files=['fair_risk_calculator.py'], strict=True)

# Option 4: Silent mode (no console output)
verified = verify_runtime_integrity(silent=True)
```

---

## Setup and Usage

### Initial Setup (One-Time)

**Step 1: Generate Baseline**

After installing or downloading the FAIR Risk Calculator:

```bash
cd FAIR-Analysis
python generate_integrity_manifest.py
```

This creates `integrity_manifest.json` containing cryptographic hashes of all files.

**Step 2: Secure the Manifest**

⚠️ **CRITICAL:** Protect the integrity manifest from tampering:

```bash
# Linux/macOS: Set read-only permissions
chmod 444 integrity_manifest.json

# Windows: Set read-only attribute
attrib +r integrity_manifest.json
```

**Step 3: Backup the Manifest**

Store a copy in a secure location:
- Offline USB drive or CD
- Git repository (separate from code)
- Secure network share with restricted access
- Password-protected archive

### Regular Verification

**Before Running Risk Analysis:**

```bash
# Verify integrity before using the tool
python verify_integrity.py

# If verification passes, safe to proceed
fair-quick
```

**Automated Verification (Recommended):**

Create a wrapper script that verifies before execution:

**Linux/macOS (`fair-quick-secure`):**
```bash
#!/bin/bash
python verify_integrity.py --strict || exit 1
python quick_risk_analysis.py "$@"
```

**Windows (`fair-quick-secure.bat`):**
```batch
@echo off
python verify_integrity.py --strict
if %ERRORLEVEL% NEQ 0 exit /b 1
python quick_risk_analysis.py %*
```

### After Authorized Updates

When you legitimately update the code:

```bash
# 1. Make your changes
# 2. Test thoroughly
python test_validation.py
python test_mathematical_correctness.py

# 3. Regenerate the baseline
python generate_integrity_manifest.py

# 4. Verify the new baseline
python verify_integrity.py
```

---

## Integration with Applications

### Optional Runtime Checks

The core calculator files can optionally perform runtime integrity checks:

**fair_risk_calculator.py** (example integration):

```python
# At the top of the file, after imports
try:
    from integrity_checker import verify_runtime_integrity
    # Perform optional integrity check (non-strict)
    if not verify_runtime_integrity(files=['fair_risk_calculator.py'], silent=True):
        import warnings
        warnings.warn(
            "Code integrity verification failed. Results may not be trustworthy.",
            category=SecurityWarning
        )
except ImportError:
    pass  # integrity_checker not available, skip check
```

### Web Application Integration

**fair_risk_app.py** can show integrity status in the UI:

```python
import streamlit as st
from integrity_checker import RuntimeIntegrityChecker

# In sidebar
with st.sidebar:
    st.subheader("🔒 Security Status")

    checker = RuntimeIntegrityChecker(silent=True)
    if checker.verify_critical_files():
        st.success("✅ Code integrity verified")
    else:
        st.error("⚠️ Code integrity check failed!")
        st.warning("Do not trust results. Restore from backup.")
```

### CI/CD Integration

Add verification to your build pipeline:

**GitHub Actions example:**
```yaml
- name: Verify Code Integrity
  run: |
    python verify_integrity.py --strict
  continue-on-error: false
```

---

## Best Practices

### 1. Secure Deployment

**Production Environments:**
- Run FAIR Risk Calculator in a dedicated, isolated environment
- Use read-only file system mounts where possible
- Implement file integrity monitoring (FIM) at the OS level
- Use containerization (Docker) to ensure consistent baselines

**Example Docker Security:**
```dockerfile
# Read-only container filesystem
docker run --read-only \
  -v /path/to/data:/data \
  fair-risk-calculator
```

### 2. Access Controls

**File System Permissions:**
```bash
# Linux/macOS: Restrict write access to critical files
chmod 555 fair_risk_calculator.py
chmod 555 quick_risk_analysis.py
chmod 555 fair_risk_app.py

# Only administrators can modify
chown root:root *.py
```

**Windows Permissions:**
- Use NTFS permissions to restrict modification to Administrators only
- Consider using Windows Defender Application Control (WDAC)

### 3. Monitoring and Auditing

**Automated Daily Verification:**

Create a scheduled task/cron job:

**Linux cron:**
```cron
# Daily integrity check at 2 AM
0 2 * * * cd /path/to/FAIR-Analysis && python verify_integrity.py --report >> /var/log/fair-integrity.log
```

**Windows Task Scheduler:**
```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\verify_integrity.py --report"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "FAIR Integrity Check" -Action $action -Trigger $trigger
```

**Log Analysis:**
- Review verification logs regularly
- Alert on any detected modifications
- Investigate failures immediately

### 4. Version Control Integration

**Git-based Integrity:**

```bash
# Track manifest in version control
git add integrity_manifest.json
git commit -m "Update integrity baseline after authorized changes"

# Verify against git history
git log integrity_manifest.json
git diff HEAD~1 integrity_manifest.json
```

### 5. Multi-Layer Defense

**Don't rely solely on this system:**
- Use antivirus/anti-malware software
- Implement network segmentation
- Enable audit logging
- Use host-based intrusion detection (HIDS)
- Implement least-privilege access controls
- Regular security training for users

---

## Incident Response

### If Tampering is Detected

**Step 1: STOP**
- Do NOT run the modified code
- Do NOT trust any risk analysis results from modified code
- Do NOT attempt to "fix" the files

**Step 2: ISOLATE**
- Disconnect the system from the network if malicious activity is suspected
- Prevent further modifications
- Preserve evidence (don't delete files)

**Step 3: INVESTIGATE**

Check file modification times:
```bash
# Linux/macOS
ls -la *.py

# Windows
dir /T:W *.py
```

Check system logs:
```bash
# Linux: Check auth logs for unauthorized access
sudo grep -i "COMMAND" /var/log/auth.log

# Windows: Check Security Event Log
Get-EventLog -LogName Security -Newest 100 | Where-Object {$_.EventID -eq 4663}
```

Determine:
- When were files modified?
- Who had access to the system at that time?
- What other files were modified?
- Is this an isolated incident or part of a broader attack?

**Step 4: RESTORE**

From trusted backup:
```bash
# Verify backup integrity first
python verify_integrity.py

# Restore from git
git checkout HEAD -- fair_risk_calculator.py

# Or restore from backup
cp /backup/fair_risk_calculator.py .

# Verify restoration
python verify_integrity.py
```

**Step 5: DOCUMENT**

Create an incident report including:
- Timeline of events
- Files affected
- Investigation findings
- Remediation actions taken
- Root cause analysis
- Lessons learned

**Step 6: IMPROVE**

Implement additional controls:
- Strengthen access controls
- Add file integrity monitoring
- Review and update security policies
- Conduct security awareness training
- Consider more restrictive deployment (containers, VMs, etc.)

### False Positives

**Legitimate modification detected?**

If you or an authorized administrator made changes:

```bash
# Review changes
git diff fair_risk_calculator.py

# Test thoroughly
python test_validation.py
python test_mathematical_correctness.py

# If changes are correct, regenerate baseline
python generate_integrity_manifest.py

# Verify new baseline
python verify_integrity.py
```

---

## Advanced Security

### Digital Signatures (Advanced)

For highest security, use GPG signatures:

**Step 1: Sign the manifest**
```bash
gpg --output integrity_manifest.json.sig --detach-sign integrity_manifest.json
```

**Step 2: Verify signature before use**
```bash
gpg --verify integrity_manifest.json.sig integrity_manifest.json
```

**Step 3: Integrate into verification script**

Modify `verify_integrity.py` to check GPG signature before verifying hashes.

### Hardware Security Modules (HSM)

For enterprise deployments:
- Store cryptographic keys in HSM
- Use TPM (Trusted Platform Module) for attestation
- Implement measured boot

### Container Security

**Docker Content Trust:**
```bash
export DOCKER_CONTENT_TRUST=1
docker build -t fair-risk-calculator .
docker push registry/fair-risk-calculator
```

**Image Scanning:**
```bash
docker scan fair-risk-calculator
trivy image fair-risk-calculator
```

### Secure Distribution

**Checksum File:**

Create and distribute checksums:
```bash
sha256sum *.py > SHA256SUMS
sha256sum -c SHA256SUMS
```

**Signed Releases:**

For public distribution:
1. Create release archives
2. Generate SHA-256 checksums
3. Sign checksums with GPG
4. Publish signature alongside releases

---

## Security Checklist

### Initial Setup
- [ ] Generate integrity manifest
- [ ] Set manifest to read-only
- [ ] Create offline backup of manifest
- [ ] Test verification process
- [ ] Document baseline creation date

### Regular Operations
- [ ] Verify integrity before each use
- [ ] Review verification logs weekly
- [ ] Update baseline after authorized changes
- [ ] Maintain secure backups
- [ ] Train users on security procedures

### Incident Response
- [ ] Document incident response procedures
- [ ] Identify security contacts
- [ ] Test restoration procedures
- [ ] Review access logs regularly
- [ ] Conduct periodic security audits

### Advanced (Optional)
- [ ] Implement automated monitoring
- [ ] Set up alerting for tampering
- [ ] Use containerization for isolation
- [ ] Implement digital signatures
- [ ] Integrate with SIEM/logging system

---

## Technical Reference

### SHA-256 Hash Algorithm

**Properties:**
- 256-bit (32-byte) output
- Cryptographically secure
- Collision-resistant
- One-way function (pre-image resistant)

**Why SHA-256?**
- Industry standard for file integrity
- NIST-approved (FIPS 180-4)
- No known practical attacks
- Fast computation
- Widely supported

### File Coverage

**Critical Files (Always Monitored):**
- Core calculation logic
- User interfaces
- Configuration files
- Dependencies manifest

**Excluded Files:**
- User data files (*.json scenarios)
- Output files (*.xlsx reports)
- Log files
- Temporary files

### Performance Impact

**Manifest Generation:**
- Time: < 1 second for all files
- Disk I/O: Read all monitored files once
- CPU: Minimal (SHA-256 is efficient)

**Verification:**
- Time: < 500ms for all files
- Overhead: Negligible for startup
- Can be run in background

---

## Support and Updates

### Questions?

- Review this documentation
- Check `TROUBLESHOOTING.md` for common issues
- Run test suite to verify installation
- Contact security team for incidents

### Reporting Security Issues

If you discover a security vulnerability:
1. Do NOT publish publicly
2. Document the issue clearly
3. Contact maintainers privately
4. Provide reproduction steps
5. Allow time for remediation

### Updates

This security system will be updated to:
- Support additional hash algorithms
- Add GPG signature verification
- Integrate with enterprise security tools
- Provide web-based verification UI
- Add HMAC for tamper-proof manifests

---

**Last Updated:** 2025-11-13
**Version:** 1.0
**Status:** Production Ready

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│         FAIR RISK CALCULATOR - SECURITY QUICK REFERENCE         │
├─────────────────────────────────────────────────────────────────┤
│ SETUP (One-Time)                                                │
│   python generate_integrity_manifest.py                         │
│   chmod 444 integrity_manifest.json                             │
│   # Back up manifest to secure location                         │
│                                                                 │
│ VERIFY (Before Each Use)                                        │
│   python verify_integrity.py                                    │
│                                                                 │
│ UPDATE (After Changes)                                          │
│   # Make changes                                                │
│   python test_validation.py  # Test                             │
│   python generate_integrity_manifest.py  # Regenerate           │
│                                                                 │
│ IF TAMPERING DETECTED                                           │
│   1. STOP - Do not run code                                     │
│   2. ISOLATE - Disconnect if needed                             │
│   3. INVESTIGATE - Check logs, access                           │
│   4. RESTORE - From trusted backup                              │
│   5. DOCUMENT - Create incident report                          │
│   6. IMPROVE - Add security controls                            │
└─────────────────────────────────────────────────────────────────┘
```
