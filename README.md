# FAIR Risk Calculator - Automated Cyber Risk Assessment

## Overview

This repository contains two powerful implementations of the **Factor Analysis of Information Risk (FAIR)** methodology for quantitative cyber risk assessment:

1. **Command-line tool** (`fair_risk_calculator.py`) - Full-featured Python script with extensive analysis capabilities
2. **Web application** (`fair_risk_app.py`) - Interactive Streamlit interface for easy risk assessment

Both tools automate the risk calculation process from your Excel spreadsheet, adding Monte Carlo simulation, advanced statistics, and professional visualizations.

## Features

### Core Functionality
- ✅ **Monte Carlo Simulation** - 10,000+ iterations for accurate risk quantification
- ✅ **PERT & Uniform Distributions** - Realistic probability modeling
- ✅ **Multiple Risk Scenarios** - Analyze and compare multiple risks simultaneously
- ✅ **Statistical Analysis** - Mean, median, percentiles, VaR, CVaR, and more
- ✅ **Professional Visualizations** - Distribution charts, cumulative curves, risk matrices
- ✅ **Export Capabilities** - Excel, JSON, and CSV formats

### Enhanced Features (Beyond Original Excel)
- 📊 **Interactive Dashboards** - Real-time risk visualization
- 🎯 **Value at Risk (VaR)** - Industry-standard risk metrics
- 📈 **Conditional VaR (CVaR)** - Tail risk analysis
- 🔄 **Scenario Comparison** - Side-by-side risk assessment
- 📉 **Exceedance Curves** - Probability of loss thresholds
- 💾 **Automated Reporting** - Generate professional reports instantly

## Installation

### Prerequisites
```bash
# Python 3.7+ required
python --version

# Install required packages
pip install numpy pandas matplotlib seaborn plotly streamlit xlsxwriter
```

### Quick Start

#### Option 1: Command-Line Tool
```bash
# Run demo with sample scenarios
python fair_risk_calculator.py --demo

# Run with custom iterations
python fair_risk_calculator.py --demo --iterations 50000

# Export results
python fair_risk_calculator.py --demo --export-excel results.xlsx --export-json results.json
```

#### Option 2: Web Application
```bash
# Launch the web interface
streamlit run fair_risk_app.py

# The app will open in your browser at http://localhost:8501
```

## Usage Guide

### Command-Line Tool

#### Basic Usage
```python
from fair_risk_calculator import FAIRRiskCalculator

# Initialize calculator
calculator = FAIRRiskCalculator(iterations=10000)

# Add a risk scenario
calculator.add_scenario(
    scenario_id="S1",
    description="Data Breach - Customer PII",
    tef_low=1,          # Threat Event Frequency (low estimate)
    tef_medium=3,       # TEF (most likely)
    tef_high=6,         # TEF (high estimate)
    vuln_low=0.2,       # Vulnerability % (low: 20%)
    vuln_medium=0.5,    # Vulnerability % (most likely: 50%)
    vuln_high=0.85,     # Vulnerability % (high: 85%)
    loss_low=500000,    # Loss Magnitude (low: $500K)
    loss_medium=2080000,# Loss Magnitude (most likely: $2.08M)
    loss_high=3500000,  # Loss Magnitude (high: $3.5M)
    asset="Customer Database",
    threat_actor="External Attacker",
    loss_effect="Confidentiality"
)

# Run simulation
results = calculator.run_simulation("S1", distribution="pert")

# Create visualizations
calculator.create_visualizations("S1", save_path="risk_analysis.png")

# Export results
calculator.export_to_excel("risk_results.xlsx")
calculator.export_to_json("risk_results.json")
```

#### Advanced Features
```python
# Run all scenarios at once
summary = calculator.run_all_scenarios(distribution="pert")
print(summary)

# Create comparison charts
calculator.create_comparison_chart(save_path="comparison.png")

# Access detailed statistics
stats = calculator.simulation_results["S1"]["statistics"]
print(f"Mean Annual Loss: ${stats['mean_loss']:,.0f}")
print(f"90th Percentile: ${stats['percentile_90']:,.0f}")
print(f"Value at Risk (95%): ${stats['var_95']:,.0f}")
```

### Web Application

1. **Launch the app**: `streamlit run fair_risk_app.py`

2. **Add scenarios** (Scenario Input tab):
   - Enter scenario details (ID, name, risk parameters)
   - Or load sample scenarios from the sidebar

3. **Run simulations** (Run Simulations tab):
   - Configure iterations and distribution type in sidebar
   - Click "Run All Simulations"

4. **Analyze results** (Analysis Results tab):
   - View key metrics and visualizations
   - Examine detailed statistics

5. **Compare scenarios** (Scenario Comparison tab):
   - Bar charts and risk matrices
   - Side-by-side comparisons

6. **Export data** (Export Data tab):
   - Download Excel reports
   - Export JSON or CSV data

## Input Parameters Explained

### Threat Event Frequency (TEF)
- **Definition**: Expected number of threat events per year
- **Example**: For phishing attacks, might be 100-365 attempts/year

### Vulnerability (%)
- **Definition**: Probability that a threat succeeds (0-100%)
- **Example**: With good controls, vulnerability might be 10-30%

### Loss Magnitude ($)
- **Definition**: Financial impact when a loss occurs
- **Components**: Response costs, legal fees, regulatory fines, business interruption

### Distribution Types
- **PERT**: Weighted toward the "most likely" value (recommended)
- **Uniform**: Equal probability across the range

## Output Metrics

| Metric | Description |
|--------|-------------|
| **Mean Loss** | Average expected annual loss |
| **Median Loss** | 50th percentile loss value |
| **90th Percentile** | Loss exceeded only 10% of the time |
| **VaR (95%)** | Value at Risk - maximum loss with 95% confidence |
| **CVaR (95%)** | Average loss when VaR is exceeded |
| **P(Loss > $1M)** | Probability of loss exceeding $1 million |

## Visualizations

### 1. Loss Distribution
- Histogram showing frequency of different loss amounts
- Marked with mean, 90th percentile, and VaR lines

### 2. Cumulative Distribution Function (CDF)
- Probability of loss being less than or equal to a given value
- Useful for determining percentiles

### 3. Risk Components
- Distribution of TEF, Vulnerability, and Loss Magnitude
- Shows uncertainty in input parameters

### 4. Risk Matrix
- Scatter plot of Mean vs VaR for scenario comparison
- Identifies high-risk scenarios

### 5. Exceedance Curve
- Probability of exceeding various loss thresholds
- Critical for understanding tail risk

## Best Practices

### 1. Estimating Parameters
- Use historical data when available
- Consult subject matter experts
- Document assumptions clearly
- Consider using ranges rather than point estimates

### 2. Number of Iterations
- Minimum: 1,000 for quick analysis
- Recommended: 10,000 for standard analysis
- High precision: 50,000-100,000 iterations

### 3. Scenario Development
- Be specific about the threat and asset
- Consider different attack vectors separately
- Include both likely and worst-case scenarios
- Update regularly based on threat landscape

### 4. Interpreting Results
- Focus on ranges, not just averages
- Pay attention to tail risks (95th+ percentiles)
- Compare scenarios to prioritize mitigation
- Consider risk appetite when making decisions

## Comparison with Original Excel

| Feature | Original Excel | Python Tools | Improvement |
|---------|---------------|--------------|-------------|
| Iterations | 1,000 | 10,000-100,000 | 10-100x more accurate |
| Distributions | Basic random | PERT & Uniform | More realistic modeling |
| Visualizations | Basic charts | 6+ chart types | Professional reporting |
| Scenario Management | Manual | Automated | Save hours of work |
| Statistical Analysis | Mean, percentiles | 15+ metrics | Comprehensive insights |
| Export Options | Excel only | Excel, JSON, CSV | Flexible integration |
| User Interface | Spreadsheet | CLI & Web | Modern, intuitive |

## Advanced Use Cases

### 1. Portfolio Risk Assessment
```python
# Analyze multiple scenarios to understand overall risk
scenarios = ["S1", "S2", "S3", "S4"]
total_risk = sum([calculator.simulation_results[s]["statistics"]["mean_loss"] 
                  for s in scenarios])
print(f"Total Portfolio Risk: ${total_risk:,.0f}")
```

### 2. Risk Mitigation Analysis
```python
# Compare before/after mitigation
calculator.add_scenario("S1_before", "Risk without controls", ...)
calculator.add_scenario("S1_after", "Risk with controls", ...)
# Analyze reduction in risk metrics
```

### 3. Sensitivity Analysis
```python
# Test impact of parameter changes
for vuln in [0.1, 0.3, 0.5, 0.7, 0.9]:
    calculator.add_scenario(f"S_vuln_{vuln}", f"Vulnerability {vuln}", 
                          vuln_low=vuln*0.8, vuln_medium=vuln, vuln_high=vuln*1.2, ...)
```

## Troubleshooting

### Common Issues

1. **ImportError**: Install missing packages
   ```bash
   pip install -r requirements.txt
   ```

2. **Streamlit not opening**: Check firewall settings or try:
   ```bash
   streamlit run fair_risk_app.py --server.port 8080
   ```

3. **Memory issues with large iterations**: Reduce iteration count or process in batches

## Contributing

Contributions are welcome! Areas for enhancement:
- Additional distribution types (triangular, lognormal)
- Correlation between risk factors
- Time-series risk analysis
- Integration with threat intelligence feeds
- Machine learning for parameter estimation

## References

- [FAIR Institute](https://www.fairinstitute.org/)
- [Open FAIR™ Standard](https://publications.opengroup.org/standards/fair)
- [Risk Analysis with Python](https://www.oreilly.com/library/view/risk-analysis-with/9781492058526/)

## License

This project is provided as-is for educational and risk assessment purposes.

## Support

For questions or issues:
1. Check the documentation above
2. Review the code comments
3. Test with the demo scenarios first
4. Verify all dependencies are installed

---

**Note**: This tool provides risk estimates based on input parameters. Actual losses may vary. Always combine quantitative analysis with qualitative assessment and professional judgment.
