# Security Quick Start Guide

Protect your FAIR Risk Calculator from unauthorized modifications - **now fully automated!**

---

## 🎉 **NEW: Automatic Protection (Zero Setup!)**

**Starting now, security is automatic!** Just run any tool and integrity protection activates:

```bash
# Run any tool - security protection happens automatically!
python quick_risk_analysis.py

# First run: Auto-generates security baseline
# Subsequent runs: Auto-verifies integrity
```

**That's it!** No manual setup required. The system:
- ✅ Auto-generates baseline on first run
- ✅ Auto-verifies on every subsequent run
- ✅ Alerts immediately if tampering detected
- ✅ Works with CLI tools and web app

---

## 📋 What Happens Automatically

### First Run (Any Tool)
```
======================================================================
🔒 FIRST RUN DETECTED - Establishing Security Baseline
======================================================================
Generating cryptographic integrity baseline...
This protects your FAIR Risk Calculator from tampering.

✅ Security baseline established successfully!
   Files monitored: 9
   Manifest saved: integrity_manifest.json

Your FAIR Risk Calculator is now protected against tampering.
======================================================================
```

### Subsequent Runs (Every Time)
```
🔒 Security Check: ✅ PASSED - Code integrity verified

[Tool continues normally...]
```

### If Tampering Detected
```
======================================================================
⚠️  SECURITY ALERT: CODE TAMPERING DETECTED!
======================================================================
Details: Code tampering detected

Recommended actions:
  1. If you made legitimate changes:
     python generate_integrity_manifest.py
  2. If you did NOT make changes:
     Restore from backup and investigate
======================================================================
```

---

## ⚡ Quick Start (Optional Manual Setup)

**Note:** This is now optional! Automatic protection is enabled by default.

If you want to manually generate the baseline before first use:

### Step 1: Generate Baseline (30 seconds)

```bash
cd FAIR-Analysis
python generate_integrity_manifest.py
```

This creates `integrity_manifest.json` with cryptographic hashes of all critical files.

### Step 2: Secure the Manifest (15 seconds)

**Linux/macOS:**
```bash
chmod 444 integrity_manifest.json
```

**Windows:**
```cmd
attrib +r integrity_manifest.json
```

### Step 3: Create Backup (30 seconds)

Copy `integrity_manifest.json` to a secure location:
- USB drive
- Secure network share
- Git repository (separate from code)

**✅ Done! Your code is now protected.**

---

## 🔍 Daily Use

### Before Running Any Analysis

```bash
# Verify integrity (takes < 1 second)
python verify_integrity.py

# If it says "SUCCESS", you're safe to proceed
fair-quick
```

### If Tampering is Detected

```
⚠️  WARNING: CODE TAMPERING DETECTED!
```

**DO:**
1. ❌ **STOP** - Do not run the code
2. 🔍 **INVESTIGATE** - Check who modified files
3. 💾 **RESTORE** - From your secure backup
4. 📝 **DOCUMENT** - Create incident report

**DON'T:**
- ❌ Don't ignore the warning
- ❌ Don't try to "fix" files manually
- ❌ Don't trust results from modified code

---

## 🔄 After Updates

When YOU make legitimate changes:

```bash
# 1. Make your changes
# 2. Test them
python test_validation.py

# 3. Regenerate baseline
python generate_integrity_manifest.py

# 4. Verify new baseline
python verify_integrity.py
```

---

## 🛡️ Security Modes

### Mode 1: Manual Verification (Recommended for Most Users)

```bash
# Run before each use
python verify_integrity.py
```

### Mode 2: Strict Mode (Recommended for Production)

```bash
# Exits immediately if tampering detected
python verify_integrity.py --strict
```

### Mode 3: Automated Wrapper (Recommended for Teams)

Create `fair-secure` script:

**Linux/macOS:**
```bash
#!/bin/bash
python verify_integrity.py --strict || exit 1
python quick_risk_analysis.py "$@"
```

```bash
chmod +x fair-secure
./fair-secure
```

**Windows (`fair-secure.bat`):**
```batch
@echo off
python verify_integrity.py --strict
if %ERRORLEVEL% NEQ 0 exit /b 1
python quick_risk_analysis.py %*
```

```cmd
fair-secure.bat
```

### Mode 4: Runtime Checks (Advanced)

For developers integrating into applications:

```python
from integrity_checker import verify_runtime_integrity

# Check at startup
if not verify_runtime_integrity(strict=True):
    sys.exit(1)

# Now safe to proceed
calculator = FAIRRiskCalculator()
```

---

## 📋 Cheat Sheet

```
┌──────────────────────────────────────────────────────┐
│            SECURITY COMMAND REFERENCE                │
├──────────────────────────────────────────────────────┤
│ GENERATE BASELINE                                    │
│   python generate_integrity_manifest.py              │
│                                                      │
│ VERIFY INTEGRITY                                     │
│   python verify_integrity.py                         │
│   python verify_integrity.py --strict  # Exit if bad │
│   python verify_integrity.py --verbose # Show all    │
│   python verify_integrity.py --report  # JSON report │
│                                                      │
│ RUNTIME CHECK (in code)                              │
│   from integrity_checker import verify_runtime_...   │
│   verify_runtime_integrity(strict=True)              │
│                                                      │
│ SECURE FILES (Linux/macOS)                           │
│   chmod 444 integrity_manifest.json                  │
│   chmod 555 *.py  # Make scripts read-only           │
│                                                      │
│ SECURE FILES (Windows)                               │
│   attrib +r integrity_manifest.json                  │
│   attrib +r *.py  # Make scripts read-only           │
└──────────────────────────────────────────────────────┘
```

---

## ❓ FAQs

### Q: How often should I verify integrity?
**A:** Before each use, or at minimum once per day if the tool is running continuously.

### Q: What if I forget to regenerate after making changes?
**A:** The verification will show "MODIFIED" warnings. Simply regenerate the baseline if the changes were legitimate.

### Q: Can an attacker modify both the code AND the manifest?
**A:** Yes! That's why you MUST keep a secure backup of the manifest in a separate location.

### Q: Does this slow down the tool?
**A:** No. Verification takes < 1 second and has negligible performance impact.

### Q: What if I don't have the manifest file?
**A:** The tools will still run, but you have NO protection against tampering. Generate it immediately!

### Q: Should I commit the manifest to Git?
**A:** No. It's in `.gitignore` for a reason. Each deployment should generate its own baseline.

### Q: What about dependencies in requirements.txt?
**A:** The manifest checks the requirements.txt file itself. Consider using `pip hash` for dependencies.

---

## 🔗 Additional Resources

- **Full Security Guide:** [SECURITY.md](SECURITY.md)
- **Incident Response:** [SECURITY.md#incident-response](SECURITY.md#incident-response)
- **Advanced Security:** [SECURITY.md#advanced-security](SECURITY.md#advanced-security)
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## ⚠️ Important Reminders

1. **Backup the manifest** - It's your security baseline!
2. **Verify before use** - Make it a habit
3. **Investigate tampering** - Never ignore warnings
4. **Update after changes** - Regenerate the baseline
5. **Secure the files** - Use read-only permissions

---

## 🎯 Security Checklist

- [ ] Generated integrity manifest
- [ ] Secured manifest with read-only permissions
- [ ] Created backup of manifest in secure location
- [ ] Tested verification process
- [ ] Added verification to daily workflow
- [ ] Configured automated alerts (optional)
- [ ] Documented incident response procedures
- [ ] Trained team on security procedures

---

**Remember:** This system DETECTS tampering, it doesn't PREVENT it. Combine with:
- File system permissions
- Access controls
- Antivirus software
- Network security
- User training

**Stay secure! 🔒**

---

*For detailed information, see [SECURITY.md](SECURITY.md)*
