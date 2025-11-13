#!/usr/bin/env python3
"""
Quick Risk Analysis - Simplified FAIR Risk Calculator
Get immediate risk analysis results with minimal setup
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys

class QuickRiskAnalyzer:
    """
    Simplified risk analyzer for quick FAIR assessments

    Implements the FAIR model: Risk = LEF × LM
    Where LEF (Loss Event Frequency) = TEF × Vulnerability
    """

    @staticmethod
    def pert_distribution(low, medium, high, size=10000):
        """
        Generate PERT distribution samples

        PERT distribution is a special case of Beta distribution commonly used in risk analysis.

        Args:
            low: Minimum value
            medium: Most likely value (mode)
            high: Maximum value
            size: Number of samples

        Returns:
            NumPy array of samples

        Raises:
            ValueError: If medium is not between low and high
        """
        # Validate inputs
        if not (low <= medium <= high):
            raise ValueError(
                f"PERT distribution requires low ≤ medium ≤ high. "
                f"Got: low={low}, medium={medium}, high={high}"
            )

        # Handle degenerate case
        if high == low:
            return np.full(size, medium)

        # PERT parameters
        lambda_param = 4  # Shape parameter for moderate confidence
        alpha = 1 + lambda_param * (medium - low) / (high - low)
        beta = 1 + lambda_param * (high - medium) / (high - low)

        # Generate and scale Beta distribution
        samples = np.random.beta(alpha, beta, size)
        return low + samples * (high - low)

    @staticmethod
    def analyze_risk(tef, vuln, loss, iterations=10000, random_seed=None):
        """
        Quick FAIR risk analysis using Monte Carlo simulation

        Implements: ALE = TEF × Vulnerability × Loss Magnitude

        Args:
            tef: dict with 'low', 'medium', 'high' for Threat Event Frequency (events/year)
            vuln: dict with 'low', 'medium', 'high' for Vulnerability (probability 0-1)
            loss: dict with 'low', 'medium', 'high' for Loss Magnitude ($)
            iterations: number of simulation iterations (default: 10000)
            random_seed: optional random seed for reproducibility

        Returns:
            Dictionary with comprehensive risk metrics including:
                - mean, median: central tendency
                - p90, var95, cvar95: tail risk metrics
                - prob_1m, prob_5m: threshold probabilities
                - samples: full ALE distribution
        """
        # Set random seed if provided for reproducibility
        if random_seed is not None:
            np.random.seed(random_seed)

        # Run Monte Carlo simulation using PERT distributions
        tef_samples = QuickRiskAnalyzer.pert_distribution(
            tef['low'], tef['medium'], tef['high'], iterations
        )
        vuln_samples = QuickRiskAnalyzer.pert_distribution(
            vuln['low'], vuln['medium'], vuln['high'], iterations
        )
        loss_samples = QuickRiskAnalyzer.pert_distribution(
            loss['low'], loss['medium'], loss['high'], iterations
        )

        # Calculate Annual Loss Expectancy (FAIR model)
        # ALE = TEF × Vulnerability × Loss Magnitude
        ale_samples = tef_samples * vuln_samples * loss_samples

        # Calculate VaR once to avoid redundant computation
        var95_value = np.percentile(ale_samples, 95)

        # Calculate comprehensive statistics
        return {
            'mean': np.mean(ale_samples),
            'median': np.median(ale_samples),
            'std': np.std(ale_samples, ddof=1),  # Sample std dev
            'p90': np.percentile(ale_samples, 90),
            'var95': var95_value,  # Value at Risk (95%)
            'cvar95': np.mean(ale_samples[ale_samples >= var95_value]),  # Conditional VaR
            'prob_1m': np.sum(ale_samples > 1000000) / len(ale_samples),
            'prob_5m': np.sum(ale_samples > 5000000) / len(ale_samples),
            'samples': ale_samples
        }
    
    @staticmethod
    def create_quick_visualization(results, title="Risk Analysis"):
        """Create a simple 4-panel visualization"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(title, fontsize=14, fontweight='bold')
        
        samples = results['samples']
        
        # 1. Loss Distribution
        ax1.hist(samples, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
        ax1.axvline(results['mean'], color='red', linestyle='--', label=f"Mean: ${results['mean']:,.0f}")
        ax1.axvline(results['p90'], color='orange', linestyle='--', label=f"90th %: ${results['p90']:,.0f}")
        ax1.set_xlabel('Annual Loss ($)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Loss Distribution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Cumulative Distribution
        sorted_losses = np.sort(samples)
        cumulative = np.arange(1, len(sorted_losses) + 1) / len(sorted_losses)
        ax2.plot(sorted_losses, cumulative, linewidth=2, color='darkgreen')
        ax2.axhline(0.9, color='orange', linestyle=':', alpha=0.5)
        ax2.axhline(0.95, color='red', linestyle=':', alpha=0.5)
        ax2.set_xlabel('Annual Loss ($)')
        ax2.set_ylabel('Cumulative Probability')
        ax2.set_title('Cumulative Distribution')
        ax2.grid(True, alpha=0.3)
        
        # 3. Box Plot
        bp = ax3.boxplot(samples, vert=True, patch_artist=True)
        bp['boxes'][0].set_facecolor('lightblue')
        ax3.set_ylabel('Annual Loss ($)')
        ax3.set_title('Loss Distribution Box Plot')
        ax3.grid(True, alpha=0.3)
        
        # 4. Key Metrics
        ax4.axis('off')
        metrics_text = f"""
KEY RISK METRICS

Mean Annual Loss:     ${results['mean']:,.0f}
Median Loss:          ${results['median']:,.0f}

90th Percentile:      ${results['p90']:,.0f}
95th Percentile:      ${results['var95']:,.0f}
CVaR (95%):          ${results['cvar95']:,.0f}

P(Loss > $1M):        {results['prob_1m']:.1%}
P(Loss > $5M):        {results['prob_5m']:.1%}
        """
        ax4.text(0.1, 0.9, metrics_text, transform=ax4.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        return fig


def main():
    """Interactive quick risk assessment"""
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              QUICK RISK ANALYSIS TOOL                      ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print("This tool provides rapid risk assessment using the FAIR methodology.")
    print("Enter your estimates for each parameter (Low, Most Likely, High).\n")
    
    # Get scenario name
    scenario_name = input("Risk Scenario Name: ").strip() or "Risk Scenario"
    
    print("\n" + "="*60)
    print("THREAT EVENT FREQUENCY (TEF)")
    print("How many times per year could this threat occur?")
    print("Examples: Phishing(100-365), Ransomware(1-10), Insider(0.5-5)")
    print("="*60)
    
    tef = {}
    tef['low'] = float(input("TEF - Low estimate [default: 1]: ").strip() or "1")
    tef['medium'] = float(input("TEF - Most likely [default: 3]: ").strip() or "3")
    tef['high'] = float(input("TEF - High estimate [default: 6]: ").strip() or "6")
    
    print("\n" + "="*60)
    print("VULNERABILITY")
    print("Probability (0-100%) that the threat succeeds if it occurs")
    print("Examples: Good controls(0.1-0.3), Average(0.3-0.6), Poor(0.6-0.9)")
    print("="*60)
    
    vuln = {}
    vuln['low'] = float(input("Vulnerability - Low (0-1) [default: 0.2]: ").strip() or "0.2")
    vuln['medium'] = float(input("Vulnerability - Most likely (0-1) [default: 0.5]: ").strip() or "0.5")
    vuln['high'] = float(input("Vulnerability - High (0-1) [default: 0.85]: ").strip() or "0.85")
    
    print("\n" + "="*60)
    print("LOSS MAGNITUDE ($)")
    print("Financial impact when the incident occurs")
    print("Include: Response, legal, fines, business disruption, reputation")
    print("="*60)
    
    loss = {}
    loss['low'] = float(input("Loss - Low estimate ($) [default: 500000]: ").strip() or "500000")
    loss['medium'] = float(input("Loss - Most likely ($) [default: 2080000]: ").strip() or "2080000")
    loss['high'] = float(input("Loss - High estimate ($) [default: 3500000]: ").strip() or "3500000")

    # Validate input values
    print("\n" + "="*60)
    print("VALIDATING INPUTS...")
    print("="*60)

    validation_errors = []

    # Validate TEF (Threat Event Frequency)
    if not (tef['low'] <= tef['medium'] <= tef['high']):
        validation_errors.append(
            f"❌ TEF Error: Values must be in ascending order (Low ≤ Medium ≤ High)\n"
            f"   Got: Low={tef['low']}, Medium={tef['medium']}, High={tef['high']}"
        )

    # Validate Vulnerability
    if not (vuln['low'] <= vuln['medium'] <= vuln['high']):
        validation_errors.append(
            f"❌ Vulnerability Error: Values must be in ascending order (Low ≤ Medium ≤ High)\n"
            f"   Got: Low={vuln['low']:.2f}, Medium={vuln['medium']:.2f}, High={vuln['high']:.2f}"
        )

    # Validate vulnerability range (0-1)
    if not (0 <= vuln['low'] <= 1 and 0 <= vuln['medium'] <= 1 and 0 <= vuln['high'] <= 1):
        validation_errors.append(
            f"❌ Vulnerability Error: Values must be between 0 and 1\n"
            f"   Got: Low={vuln['low']:.2f}, Medium={vuln['medium']:.2f}, High={vuln['high']:.2f}"
        )

    # Validate Loss Magnitude
    if not (loss['low'] <= loss['medium'] <= loss['high']):
        validation_errors.append(
            f"❌ Loss Magnitude Error: Values must be in ascending order (Low ≤ Medium ≤ High)\n"
            f"   Got: Low=${loss['low']:,.0f}, Medium=${loss['medium']:,.0f}, High=${loss['high']:,.0f}"
        )

    # Validate non-negative values
    if tef['low'] < 0 or tef['medium'] < 0 or tef['high'] < 0:
        validation_errors.append("❌ TEF Error: Values cannot be negative")

    if loss['low'] < 0 or loss['medium'] < 0 or loss['high'] < 0:
        validation_errors.append("❌ Loss Magnitude Error: Values cannot be negative")

    # Display validation results
    if validation_errors:
        print("\n⚠️  INPUT VALIDATION FAILED:")
        print("="*60)
        for error in validation_errors:
            print(error)
        print("\n💡 Tip: Ensure that Low ≤ Medium ≤ High for all parameters")
        print("         (TEF, Vulnerability, and Loss Magnitude)")
        print("="*60)
        sys.exit(1)
    else:
        print("✅ All inputs validated successfully!")

    # Ask for iterations
    iterations_input = input("\nNumber of simulations [default: 10000]: ").strip()
    iterations = int(iterations_input) if iterations_input else 10000

    print(f"\n🎲 Running {iterations:,} Monte Carlo simulations...")

    # Run analysis
    analyzer = QuickRiskAnalyzer()
    results = analyzer.analyze_risk(tef, vuln, loss, iterations)
    
    # Display results
    print("\n" + "="*60)
    print("RISK ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n📊 {scenario_name}")
    print(f"   Mean Annual Loss:        ${results['mean']:,.0f}")
    print(f"   Median Annual Loss:      ${results['median']:,.0f}")
    print(f"   90th Percentile:         ${results['p90']:,.0f}")
    print(f"   95th Percentile (VaR):   ${results['var95']:,.0f}")
    print(f"   Conditional VaR (95%):   ${results['cvar95']:,.0f}")
    
    print(f"\n⚠️  Risk Indicators:")
    print(f"   Probability Loss > $1M:   {results['prob_1m']:.1%}")
    print(f"   Probability Loss > $5M:   {results['prob_5m']:.1%}")
    
    print("\n" + "="*60)
    
    # Risk interpretation
    if results['mean'] < 100000:
        risk_level = "LOW"
        color = "🟢"
    elif results['mean'] < 1000000:
        risk_level = "MODERATE"
        color = "🟡"
    elif results['mean'] < 5000000:
        risk_level = "HIGH"
        color = "🟠"
    else:
        risk_level = "CRITICAL"
        color = "🔴"
    
    print(f"\n{color} Overall Risk Level: {risk_level}")
    print(f"   Expected annual loss of ${results['mean']:,.0f}")
    print(f"   10% chance of losses exceeding ${results['p90']:,.0f}")
    print(f"   5% chance of losses exceeding ${results['var95']:,.0f}")
    
    # Recommendations based on risk level
    print("\n💡 Recommendations:")
    if risk_level == "CRITICAL":
        print("   • Immediate action required - implement additional controls")
        print("   • Consider cyber insurance for catastrophic losses")
        print("   • Executive briefing recommended")
    elif risk_level == "HIGH":
        print("   • Prioritize risk mitigation efforts")
        print("   • Review and strengthen existing controls")
        print("   • Consider additional security investments")
    elif risk_level == "MODERATE":
        print("   • Monitor risk closely")
        print("   • Maintain current controls")
        print("   • Plan for control improvements")
    else:
        print("   • Risk is within acceptable range")
        print("   • Continue monitoring")
        print("   • Document for compliance purposes")
    
    # Ask about visualization
    show_viz = input("\n📊 Generate visualization? (y/n) [default: y]: ").strip().lower()
    if show_viz != 'n':
        fig = analyzer.create_quick_visualization(results, title=scenario_name)
        plt.show()
        
        save_viz = input("💾 Save visualization? (y/n) [default: n]: ").strip().lower()
        if save_viz == 'y':
            filename = f"risk_analysis_{scenario_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {filename}")
    
    # Ask about export
    export = input("\n💾 Export detailed results? (excel/csv/json/none) [default: none]: ").strip().lower()
    
    if export == 'excel':
        filename = f"risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df = pd.DataFrame({
            'Scenario': [scenario_name],
            'Mean Loss': [results['mean']],
            'Median Loss': [results['median']],
            '90th Percentile': [results['p90']],
            'VaR 95%': [results['var95']],
            'CVaR 95%': [results['cvar95']],
            'P(Loss > $1M)': [results['prob_1m']],
            'P(Loss > $5M)': [results['prob_5m']]
        })
        df.to_excel(filename, index=False)
        print(f"✓ Exported to {filename}")
    
    elif export == 'csv':
        filename = f"risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df = pd.DataFrame({'Annual_Loss': results['samples']})
        df.to_csv(filename, index=False)
        print(f"✓ Exported to {filename}")
    
    elif export == 'json':
        import json
        filename = f"risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_data = {
            'scenario': scenario_name,
            'inputs': {
                'tef': tef,
                'vulnerability': vuln,
                'loss_magnitude': loss
            },
            'results': {
                'mean': results['mean'],
                'median': results['median'],
                'p90': results['p90'],
                'var95': results['var95'],
                'cvar95': results['cvar95'],
                'prob_1m': results['prob_1m'],
                'prob_5m': results['prob_5m']
            },
            'iterations': iterations,
            'timestamp': datetime.now().isoformat()
        }
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"✓ Exported to {filename}")
    
    print("\n✨ Analysis complete! Thank you for using Quick Risk Analysis.")
    
    # Ask if user wants to run another analysis
    again = input("\nRun another analysis? (y/n) [default: n]: ").strip().lower()
    if again == 'y':
        print("\n" + "="*60 + "\n")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
