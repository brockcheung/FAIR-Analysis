# FAIR Risk Calculator - Interactive Cyber Risk Assessment

## 🎯 Overview

Three powerful tools for **Factor Analysis of Information Risk (FAIR)** that let YOU create and analyze YOUR OWN risk scenarios:

1. **Quick Analysis Tool** (`quick_risk_analysis.py`) - ⚡ Fastest way to get risk assessment results
2. **Full Interactive Tool** (`fair_risk_calculator.py`) - 💪 Complete analysis with multiple scenarios
3. **Web Application** (`fair_risk_app.py`) - 🌐 Browser-based interface with dashboards

All tools are designed for **YOUR custom scenarios** - not pre-loaded data!

## 🚀 Quick Start - Analyze Your Risk in 60 Seconds

```bash
# Install dependencies (one time only)
pip install numpy pandas matplotlib seaborn plotly streamlit xlsxwriter

# Run quick analysis - just answer the prompts!
python quick_risk_analysis.py
```

That's it! The tool will guide you through creating your scenario and show results immediately.

## 📊 Three Ways to Analyze YOUR Risks

### Option 1: Quick Analysis (Fastest) ⚡

Perfect for single scenario analysis with immediate results:

```bash
python quick_risk_analysis.py
```

**What happens:**
1. Enter your scenario name
2. Input your TEF estimates (how often the threat occurs)
3. Input vulnerability estimates (chance of success)
4. Input loss estimates (financial impact)
5. Get instant results with risk metrics and visualizations!

**Example Session:**
```
Risk Scenario Name: Ransomware Attack on Production Systems

THREAT EVENT FREQUENCY (TEF)
TEF - Low estimate: 1
TEF - Most likely: 2
TEF - High estimate: 5

VULNERABILITY
Vulnerability - Low: 0.1
Vulnerability - Most likely: 0.25
Vulnerability - High: 0.4

LOSS MAGNITUDE
Loss - Low: 500000
Loss - Most likely: 2000000
Loss - High: 5000000

Results: Mean Annual Loss: $923,456
         90th Percentile: $2,134,567
         Risk Level: MODERATE
```

### Option 2: Full Interactive Mode (Most Flexible) 💪

For multiple scenarios and detailed analysis:

```bash
# Interactive menu-driven interface
python fair_risk_calculator.py

# Or quick single scenario
python fair_risk_calculator.py --quick
```

**Features:**
- Build unlimited scenarios interactively
- Compare multiple risks side-by-side
- Generate professional reports
- Export to Excel/JSON
- Batch processing support

### Option 3: Web Application (Most User-Friendly) 🌐

```bash
streamlit run fair_risk_app.py
# Opens in browser at http://localhost:8501
```

**Features:**
- Point-and-click interface
- Real-time visualizations
- Scenario comparison dashboards
- One-click exports

## 📝 Creating YOUR Risk Scenarios

### What You Need to Estimate

For each risk scenario, you provide THREE estimates (Low, Most Likely, High) for:

#### 1. **Threat Event Frequency (TEF)**
*How many times per year could this threat occur?*

| Threat Type | Low | Most Likely | High |
|------------|-----|-------------|------|
| Phishing Attacks | 50 | 200 | 365 |
| Ransomware | 1 | 3 | 10 |
| Insider Threat | 0.5 | 2 | 5 |
| DDoS Attack | 5 | 15 | 50 |
| Data Breach | 0.5 | 1 | 3 |

#### 2. **Vulnerability (%)**
*Probability the threat succeeds (0-1 scale)*

| Control Strength | Low | Most Likely | High |
|-----------------|-----|-------------|------|
| Strong Controls | 0.05 | 0.10 | 0.20 |
| Average Controls | 0.20 | 0.40 | 0.60 |
| Weak Controls | 0.50 | 0.70 | 0.90 |

#### 3. **Loss Magnitude ($)**
*Total financial impact when incident occurs*

Include:
- Incident response costs
- Legal fees and regulatory fines
- Business interruption/downtime
- Reputation damage
- Recovery and remediation
- Customer notification costs

## 💡 Interactive Usage Examples

### Example 1: Quick Assessment of a Specific Risk

```bash
python quick_risk_analysis.py
```
Then follow prompts:
```
Risk Scenario Name: Cloud Service Outage
TEF - Low: 2
TEF - Most Likely: 5
TEF - High: 12
Vulnerability - Low: 0.3
Vulnerability - Most Likely: 0.5
Vulnerability - High: 0.7
Loss - Low: 50000
Loss - Most Likely: 150000
Loss - High: 500000
```

### Example 2: Building Multiple Scenarios Interactively

```bash
python fair_risk_calculator.py
```
Select from menu:
```
OPTIONS:
  1. Add new risk scenario    <- Start here!
  2. Run simulations
  3. View results
  4. Generate visualizations
  5. Compare scenarios
  6. Export results
```

### Example 3: Batch Processing Your Scenarios

1. Create a JSON file with your scenarios (use `scenarios_template.json` as a guide)
2. Run batch analysis:
```bash
python fair_risk_calculator.py --batch my_scenarios.json --export-excel results.xlsx
```

## 📈 Understanding Your Results

### Risk Metrics Explained

| Metric | What It Means | How to Use It |
|--------|---------------|---------------|
| **Mean Annual Loss** | Average expected loss per year | Budget planning baseline |
| **90th Percentile** | Loss exceeded only 10% of the time | Likely worst-case planning |
| **VaR (95%)** | Maximum loss with 95% confidence | Risk tolerance threshold |
| **CVaR (95%)** | Average loss when VaR is exceeded | Catastrophic scenario planning |
| **P(Loss > $1M)** | Chance of million-dollar loss | Insurance decision factor |

### Risk Levels

- 🟢 **LOW** (< $100K): Acceptable risk, monitor only
- 🟡 **MODERATE** ($100K-$1M): Active management needed
- 🟠 **HIGH** ($1M-$5M): Priority mitigation required
- 🔴 **CRITICAL** (> $5M): Immediate action required

## 🎨 Visualizations Generated

All tools create professional visualizations including:
- Loss distribution histograms
- Cumulative probability curves
- Risk component analysis
- Comparison matrices
- Statistical summaries

## 💾 Export Options

### Quick Export (Single Command)
```bash
# Excel export with your scenario
python fair_risk_calculator.py --quick --export-excel my_risk.xlsx

# JSON export for integration
python fair_risk_calculator.py --quick --export-json my_risk.json
```

### Export Formats Available
- **Excel**: Full report with multiple sheets
- **JSON**: For API integration
- **CSV**: Raw data for further analysis
- **PNG**: Publication-ready charts

## 🔧 Advanced Features

### Custom Iterations
```bash
# More iterations = more accuracy (but slower)
python fair_risk_calculator.py --iterations 50000
```

### Different Distributions
```bash
# Use uniform distribution instead of PERT
python fair_risk_calculator.py --distribution uniform
```

### Save All Visualizations
```bash
# Save charts to directory
python fair_risk_calculator.py --save-plots ./charts
```

## 📋 Template for Your Scenarios

Use this template to prepare your risk scenarios:

```json
{
  "scenario_id": "S1",
  "description": "Your Risk Scenario Description",
  "tef_low": 1,
  "tef_medium": 3,
  "tef_high": 6,
  "vuln_low": 0.2,
  "vuln_medium": 0.5,
  "vuln_high": 0.85,
  "loss_low": 500000,
  "loss_medium": 2080000,
  "loss_high": 3500000,
  "notes": "Your assumptions and notes"
}
```

## 🤝 Tips for Better Risk Estimates

1. **Use Historical Data**: Review past incidents for frequency estimates
2. **Consult Experts**: Get input from security and business teams
3. **Industry Benchmarks**: Reference industry reports (Verizon DBIR, etc.)
4. **Start Conservative**: Better to overestimate risk initially
5. **Document Assumptions**: Keep notes on how you derived estimates
6. **Update Regularly**: Revisit estimates quarterly

## 🚦 Quick Decision Framework

Based on your results:

| Mean Annual Loss | Action |
|-----------------|---------|
| < $50K | Accept risk, document decision |
| $50K - $250K | Implement basic controls |
| $250K - $1M | Prioritize mitigation projects |
| $1M - $5M | Immediate action plan required |
| > $5M | Executive escalation needed |

## 📞 Support

Having issues? Try these steps:

1. **Check Python version**: Requires Python 3.7+
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Start simple**: Try `quick_risk_analysis.py` first
4. **Use defaults**: Press Enter to use default values when unsure

## 🎯 Next Steps

1. Start with ONE risk scenario using `quick_risk_analysis.py`
2. Build confidence with the estimates
3. Add more scenarios using the full tool
4. Compare and prioritize risks
5. Export results for management reporting

---

**Remember**: These tools analyze YOUR scenarios with YOUR estimates. No pre-loaded data - it's all about your specific risks!
