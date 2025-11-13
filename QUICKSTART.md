# Quick Start Guide - FAIR Risk Calculator

Get started in under 5 minutes!

## ⚡ Fastest Method - One Command Install

### Linux / macOS
```bash
./install.sh
```

### Windows
```cmd
install.bat
```

Then run:
```bash
fair-quick
```

## 🚀 Alternative Methods

### Method 1: Docker (Zero Setup)
```bash
docker-compose up
```
Open browser to: http://localhost:8501

### Method 2: Python Pip
```bash
pip install -e .
fair-app
```

### Method 3: Direct Run
```bash
pip install -r requirements.txt
python quick_risk_analysis.py
```

## 📝 Your First Risk Analysis

1. **Run the quick tool:**
   ```bash
   fair-quick
   # or: python quick_risk_analysis.py
   ```

2. **Answer the prompts:**
   ```
   Risk Scenario: Ransomware Attack

   TEF (times/year):
     Low: 1
     Medium: 2
     High: 5

   Vulnerability (0-1):
     Low: 0.1
     Medium: 0.25
     High: 0.4

   Loss Magnitude ($):
     Low: 500000
     Medium: 2000000
     High: 5000000
   ```

3. **Get instant results!**
   - Mean Annual Loss
   - Risk percentiles
   - Probability analysis
   - Visualizations

## 🎯 Available Commands

After installation, you have three tools:

| Command | Purpose | Best For |
|---------|---------|----------|
| `fair-quick` | Quick single analysis | Fast risk assessment |
| `fair-calc` | Full calculator | Multiple scenarios, comparisons |
| `fair-app` | Web application | Interactive dashboards, sharing |

## 📊 Quick Examples

### Example 1: Quick Assessment
```bash
fair-quick
```

### Example 2: Interactive Mode
```bash
fair-calc
# Select: 1. Add new risk scenario
# Follow prompts, then run simulations
```

### Example 3: Web Interface
```bash
fair-app
# Opens browser automatically
# Point-and-click interface
```

### Example 4: Batch Processing
```bash
fair-calc --batch scenarios_template.json --export-excel results.xlsx
```

## 💡 Common Use Cases

### Single Risk Assessment
```bash
fair-quick
```
Follow prompts → Get results → Done in 2 minutes

### Compare Multiple Risks
```bash
fair-calc
```
Add 3-5 scenarios → Run simulations → Compare results

### Professional Report
```bash
fair-calc --export-excel my_report.xlsx
```
Creates multi-sheet Excel with all data and statistics

### Team Presentation
```bash
fair-app
```
Use web interface for live demos and collaboration

## 🔧 Makefile Commands (Optional)

If you prefer using `make`:

```bash
make install    # Install package
make quick      # Run quick analysis
make calc       # Run calculator
make app        # Run web app
make test       # Run tests
make docker-run # Run in Docker
```

## 🐳 Docker Quick Reference

```bash
# Start
docker-compose up

# Start in background
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose build --no-cache
```

## 📖 Documentation

- **Installation**: See [INSTALL.md](INSTALL.md)
- **Full Guide**: See [README.md](README.md)
- **Packaging**: See [PACKAGING.md](PACKAGING.md)

## ❓ Quick Troubleshooting

### "Command not found" after install
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Import errors
```bash
pip install --upgrade -r requirements.txt
```

### Docker issues
```bash
docker-compose down
docker system prune -a
docker-compose up --build
```

## 🎓 Learning Path

1. **Day 1**: Run `fair-quick` with example data
2. **Day 2**: Try `fair-app` for interactive analysis
3. **Day 3**: Use `fair-calc` for multiple scenarios
4. **Day 4**: Export results to Excel
5. **Day 5**: Customize for your organization

## 📞 Need Help?

1. Run with `--help`:
   ```bash
   fair-quick --help
   fair-calc --help
   fair-app --help
   ```

2. Check test validation:
   ```bash
   python test_validation.py
   ```

3. Review documentation in this repository

## 🎯 Next Steps

Once installed:
1. ✅ Run validation tests: `python test_validation.py`
2. ✅ Try quick analysis: `fair-quick`
3. ✅ Explore web app: `fair-app`
4. ✅ Read full README for advanced features

## ⚙️ System Check

Verify your installation:

```bash
# Check Python
python --version  # Should be 3.7+

# Check pip
pip --version

# Check installation
fair-quick --help  # Should show help text

# Run tests
python test_validation.py  # Should pass all tests
```

## 🌟 Pro Tips

1. **Start Simple**: Use `fair-quick` first
2. **Use Defaults**: Press Enter to accept default values
3. **Save Results**: Always export to Excel for records
4. **Document Assumptions**: Add notes in the scenario builder
5. **Update Regularly**: Revisit scenarios quarterly

---

**That's it! You're ready to start analyzing risks with FAIR methodology.**

For detailed documentation, see [README.md](README.md)
