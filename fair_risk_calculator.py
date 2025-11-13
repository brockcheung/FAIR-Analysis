#!/usr/bin/env python3
"""
FAIR Risk Calculator - Automated Risk Assessment Tool
Based on Factor Analysis of Information Risk (FAIR) methodology
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import argparse
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class FAIRRiskCalculator:
    """
    Automated FAIR risk calculation with Monte Carlo simulation
    """
    
    def __init__(self, iterations: int = 10000):
        """
        Initialize the risk calculator
        
        Args:
            iterations: Number of Monte Carlo simulation iterations (default: 10000)
        """
        self.iterations = iterations
        self.scenarios = []
        self.simulation_results = {}
        
    def add_scenario(self, 
                    scenario_id: str,
                    description: str,
                    tef_low: float,
                    tef_medium: float,
                    tef_high: float,
                    vuln_low: float,
                    vuln_medium: float,
                    vuln_high: float,
                    loss_low: float,
                    loss_medium: float,
                    loss_high: float,
                    asset: str = "",
                    threat_actor: str = "",
                    loss_effect: str = "",
                    notes: str = "") -> None:
        """
        Add a risk scenario for analysis
        
        Args:
            scenario_id: Unique identifier for the scenario
            description: Description of the risk scenario
            tef_low: Threat Event Frequency (low estimate)
            tef_medium: Threat Event Frequency (medium estimate)
            tef_high: Threat Event Frequency (high estimate)
            vuln_low: Vulnerability percentage (low estimate, 0-1)
            vuln_medium: Vulnerability percentage (medium estimate, 0-1)
            vuln_high: Vulnerability percentage (high estimate, 0-1)
            loss_low: Loss Magnitude in USD (low estimate)
            loss_medium: Loss Magnitude in USD (medium estimate)
            loss_high: Loss Magnitude in USD (high estimate)
            asset: Asset at risk (optional)
            threat_actor: Threat actor type (optional)
            loss_effect: Type of loss effect (optional)
            notes: Additional notes (optional)
        """
        scenario = {
            'id': scenario_id,
            'description': description,
            'tef': {'low': tef_low, 'medium': tef_medium, 'high': tef_high},
            'vulnerability': {'low': vuln_low, 'medium': vuln_medium, 'high': vuln_high},
            'loss_magnitude': {'low': loss_low, 'medium': loss_medium, 'high': loss_high},
            'asset': asset,
            'threat_actor': threat_actor,
            'loss_effect': loss_effect,
            'notes': notes
        }
        self.scenarios.append(scenario)
        
    def _pert_distribution(self, low: float, medium: float, high: float, size: int) -> np.ndarray:
        """
        Generate PERT distribution values
        PERT (Program Evaluation and Review Technique) distribution is commonly used in risk analysis
        
        Args:
            low: Minimum value
            medium: Most likely value
            high: Maximum value
            size: Number of samples to generate
            
        Returns:
            Array of sampled values
        """
        # PERT uses a modified beta distribution
        # Shape parameter (lambda) typically 4 for moderate confidence
        lambda_param = 4
        
        # Calculate alpha and beta parameters
        mean = (low + lambda_param * medium + high) / (lambda_param + 2)
        
        if high == low:
            return np.full(size, medium)
            
        # Mode-adjusted parameters
        alpha = 1 + lambda_param * (medium - low) / (high - low)
        beta = 1 + lambda_param * (high - medium) / (high - low)
        
        # Generate beta distribution and scale to desired range
        samples = np.random.beta(alpha, beta, size)
        return low + samples * (high - low)
    
    def _uniform_distribution(self, low: float, high: float, size: int) -> np.ndarray:
        """
        Generate uniform distribution values (simpler alternative to PERT)
        
        Args:
            low: Minimum value
            high: Maximum value
            size: Number of samples
            
        Returns:
            Array of sampled values
        """
        return np.random.uniform(low, high, size)
    
    def run_simulation(self, scenario_id: str, distribution: str = 'pert') -> Dict:
        """
        Run Monte Carlo simulation for a specific scenario
        
        Args:
            scenario_id: ID of the scenario to simulate
            distribution: Type of distribution ('pert' or 'uniform')
            
        Returns:
            Dictionary containing simulation results
        """
        # Find the scenario
        scenario = next((s for s in self.scenarios if s['id'] == scenario_id), None)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        # Generate random samples based on distribution type
        if distribution == 'pert':
            tef_samples = self._pert_distribution(
                scenario['tef']['low'],
                scenario['tef']['medium'],
                scenario['tef']['high'],
                self.iterations
            )
            
            vuln_samples = self._pert_distribution(
                scenario['vulnerability']['low'],
                scenario['vulnerability']['medium'],
                scenario['vulnerability']['high'],
                self.iterations
            )
            
            loss_samples = self._pert_distribution(
                scenario['loss_magnitude']['low'],
                scenario['loss_magnitude']['medium'],
                scenario['loss_magnitude']['high'],
                self.iterations
            )
        else:  # uniform distribution
            tef_samples = self._uniform_distribution(
                scenario['tef']['low'],
                scenario['tef']['high'],
                self.iterations
            )
            
            vuln_samples = self._uniform_distribution(
                scenario['vulnerability']['low'],
                scenario['vulnerability']['high'],
                self.iterations
            )
            
            loss_samples = self._uniform_distribution(
                scenario['loss_magnitude']['low'],
                scenario['loss_magnitude']['high'],
                self.iterations
            )
        
        # Calculate Loss Event Frequency (LEF) and Annual Loss Expectancy (ALE)
        lef_samples = tef_samples * vuln_samples
        ale_samples = lef_samples * loss_samples
        
        # Calculate statistics
        results = {
            'scenario_id': scenario_id,
            'description': scenario['description'],
            'iterations': self.iterations,
            'distribution_type': distribution,
            'tef_samples': tef_samples,
            'vuln_samples': vuln_samples,
            'loss_samples': loss_samples,
            'lef_samples': lef_samples,
            'ale_samples': ale_samples,
            'statistics': {
                'mean_loss': np.mean(ale_samples),
                'median_loss': np.median(ale_samples),
                'std_loss': np.std(ale_samples),
                'min_loss': np.min(ale_samples),
                'max_loss': np.max(ale_samples),
                'percentile_10': np.percentile(ale_samples, 10),
                'percentile_25': np.percentile(ale_samples, 25),
                'percentile_50': np.percentile(ale_samples, 50),
                'percentile_75': np.percentile(ale_samples, 75),
                'percentile_90': np.percentile(ale_samples, 90),
                'percentile_95': np.percentile(ale_samples, 95),
                'percentile_99': np.percentile(ale_samples, 99),
                'var_95': np.percentile(ale_samples, 95),  # Value at Risk (95%)
                'cvar_95': np.mean(ale_samples[ale_samples >= np.percentile(ale_samples, 95)]),  # Conditional VaR
                'probability_zero_loss': np.sum(ale_samples == 0) / len(ale_samples),
                'probability_over_1m': np.sum(ale_samples > 1000000) / len(ale_samples),
                'probability_over_5m': np.sum(ale_samples > 5000000) / len(ale_samples),
                'probability_over_10m': np.sum(ale_samples > 10000000) / len(ale_samples),
            }
        }
        
        self.simulation_results[scenario_id] = results
        return results
    
    def run_all_scenarios(self, distribution: str = 'pert') -> pd.DataFrame:
        """
        Run simulation for all added scenarios
        
        Args:
            distribution: Type of distribution ('pert' or 'uniform')
            
        Returns:
            DataFrame with results for all scenarios
        """
        results_list = []
        for scenario in self.scenarios:
            result = self.run_simulation(scenario['id'], distribution)
            results_list.append({
                'Scenario ID': scenario['id'],
                'Description': scenario['description'],
                'Mean Loss': result['statistics']['mean_loss'],
                'Median Loss': result['statistics']['median_loss'],
                'Std Dev': result['statistics']['std_loss'],
                '10th Percentile': result['statistics']['percentile_10'],
                '90th Percentile': result['statistics']['percentile_90'],
                '95th Percentile (VaR)': result['statistics']['var_95'],
                'CVaR 95%': result['statistics']['cvar_95'],
                'P(Loss = 0)': result['statistics']['probability_zero_loss'],
                'P(Loss > $1M)': result['statistics']['probability_over_1m'],
                'P(Loss > $5M)': result['statistics']['probability_over_5m']
            })
        
        return pd.DataFrame(results_list)
    
    def create_visualizations(self, scenario_id: str, save_path: Optional[str] = None) -> None:
        """
        Create comprehensive visualizations for a scenario
        
        Args:
            scenario_id: ID of the scenario to visualize
            save_path: Optional path to save the figure
        """
        if scenario_id not in self.simulation_results:
            raise ValueError(f"No simulation results for scenario {scenario_id}")
        
        results = self.simulation_results[scenario_id]
        ale_samples = results['ale_samples']
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle(f'FAIR Risk Analysis - {results["description"]}', fontsize=16, fontweight='bold')
        
        # 1. Loss Distribution Histogram
        ax1 = plt.subplot(2, 3, 1)
        n, bins, patches = ax1.hist(ale_samples, bins=50, edgecolor='black', alpha=0.7)
        ax1.axvline(results['statistics']['mean_loss'], color='red', linestyle='--', label=f'Mean: ${results["statistics"]["mean_loss"]:,.0f}')
        ax1.axvline(results['statistics']['percentile_90'], color='orange', linestyle='--', label=f'90th %ile: ${results["statistics"]["percentile_90"]:,.0f}')
        ax1.axvline(results['statistics']['var_95'], color='darkred', linestyle='--', label=f'VaR 95%: ${results["statistics"]["var_95"]:,.0f}')
        ax1.set_xlabel('Annual Loss Expectancy ($)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Loss Distribution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Format x-axis
        ax1.ticklabel_format(style='plain', axis='x')
        ax1.set_xticklabels([f'${x/1e6:.1f}M' if x >= 1e6 else f'${x/1e3:.0f}K' for x in ax1.get_xticks()])
        
        # 2. Cumulative Distribution
        ax2 = plt.subplot(2, 3, 2)
        sorted_losses = np.sort(ale_samples)
        cumulative = np.arange(1, len(sorted_losses) + 1) / len(sorted_losses)
        ax2.plot(sorted_losses, cumulative, linewidth=2)
        ax2.axhline(0.5, color='blue', linestyle=':', alpha=0.5, label='Median')
        ax2.axhline(0.9, color='orange', linestyle=':', alpha=0.5, label='90th Percentile')
        ax2.axhline(0.95, color='red', linestyle=':', alpha=0.5, label='95th Percentile')
        ax2.set_xlabel('Annual Loss Expectancy ($)')
        ax2.set_ylabel('Cumulative Probability')
        ax2.set_title('Cumulative Distribution Function')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xticklabels([f'${x/1e6:.1f}M' if x >= 1e6 else f'${x/1e3:.0f}K' for x in ax2.get_xticks()])
        
        # 3. Box Plot with Percentiles
        ax3 = plt.subplot(2, 3, 3)
        box_data = pd.DataFrame({'Annual Loss': ale_samples})
        bp = ax3.boxplot(ale_samples, vert=True, patch_artist=True)
        bp['boxes'][0].set_facecolor('lightblue')
        
        # Add percentile markers
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        for p in percentiles:
            val = np.percentile(ale_samples, p)
            ax3.axhline(val, color='gray', linestyle=':', alpha=0.3)
            ax3.text(1.15, val, f'{p}%: ${val:,.0f}', fontsize=8)
        
        ax3.set_ylabel('Annual Loss Expectancy ($)')
        ax3.set_title('Loss Distribution Box Plot')
        ax3.grid(True, alpha=0.3)
        ax3.set_yticklabels([f'${y/1e6:.1f}M' if y >= 1e6 else f'${y/1e3:.0f}K' for y in ax3.get_yticks()])
        
        # 4. Risk Components Distribution
        ax4 = plt.subplot(2, 3, 4)
        ax4.hist(results['tef_samples'], bins=30, alpha=0.5, label='TEF', color='blue')
        ax4.set_xlabel('Threat Event Frequency')
        ax4.set_ylabel('Frequency')
        ax4.set_title('TEF Distribution')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Vulnerability Distribution
        ax5 = plt.subplot(2, 3, 5)
        ax5.hist(results['vuln_samples'], bins=30, alpha=0.5, label='Vulnerability', color='green')
        ax5.set_xlabel('Vulnerability (%)')
        ax5.set_ylabel('Frequency')
        ax5.set_title('Vulnerability Distribution')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. Risk Statistics Table
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        stats_text = f"""
        Key Risk Metrics:
        
        Mean Annual Loss:        ${results['statistics']['mean_loss']:,.0f}
        Median Annual Loss:      ${results['statistics']['median_loss']:,.0f}
        Standard Deviation:      ${results['statistics']['std_loss']:,.0f}
        
        Percentiles:
        10th Percentile:         ${results['statistics']['percentile_10']:,.0f}
        90th Percentile:         ${results['statistics']['percentile_90']:,.0f}
        95th Percentile (VaR):   ${results['statistics']['var_95']:,.0f}
        99th Percentile:         ${results['statistics']['percentile_99']:,.0f}
        
        Conditional VaR (95%):   ${results['statistics']['cvar_95']:,.0f}
        
        Probabilities:
        P(Loss = $0):            {results['statistics']['probability_zero_loss']:.1%}
        P(Loss > $1M):           {results['statistics']['probability_over_1m']:.1%}
        P(Loss > $5M):           {results['statistics']['probability_over_5m']:.1%}
        
        Simulation Details:
        Iterations:              {results['iterations']:,}
        Distribution:            {results['distribution_type'].upper()}
        """
        
        ax6.text(0.1, 0.9, stats_text, transform=ax6.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")
        
        plt.show()
    
    def create_comparison_chart(self, save_path: Optional[str] = None) -> None:
        """
        Create comparison chart for all scenarios
        
        Args:
            save_path: Optional path to save the figure
        """
        if not self.simulation_results:
            print("No simulation results to compare. Run simulations first.")
            return
        
        # Prepare data for comparison
        scenarios = []
        mean_losses = []
        percentile_90s = []
        percentile_95s = []
        
        for scenario_id, results in self.simulation_results.items():
            scenarios.append(scenario_id)
            mean_losses.append(results['statistics']['mean_loss'])
            percentile_90s.append(results['statistics']['percentile_90'])
            percentile_95s.append(results['statistics']['var_95'])
        
        # Create comparison chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Risk Scenario Comparison', fontsize=14, fontweight='bold')
        
        # Bar chart comparison
        x = np.arange(len(scenarios))
        width = 0.25
        
        bars1 = ax1.bar(x - width, mean_losses, width, label='Mean Loss', color='skyblue')
        bars2 = ax1.bar(x, percentile_90s, width, label='90th Percentile', color='orange')
        bars3 = ax1.bar(x + width, percentile_95s, width, label='95th Percentile (VaR)', color='red')
        
        ax1.set_xlabel('Scenario')
        ax1.set_ylabel('Annual Loss Expectancy ($)')
        ax1.set_title('Risk Metrics by Scenario')
        ax1.set_xticks(x)
        ax1.set_xticklabels(scenarios, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax1.annotate(f'${height/1e6:.1f}M' if height >= 1e6 else f'${height/1e3:.0f}K',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=8, rotation=45)
        
        # Risk matrix scatter plot
        ax2.scatter(mean_losses, percentile_95s, s=200, alpha=0.6)
        for i, txt in enumerate(scenarios):
            ax2.annotate(txt, (mean_losses[i], percentile_95s[i]), fontsize=10)
        
        ax2.set_xlabel('Mean Annual Loss ($)')
        ax2.set_ylabel('95th Percentile Loss (VaR) ($)')
        ax2.set_title('Risk Matrix')
        ax2.grid(True, alpha=0.3)
        
        # Format axes
        ax2.ticklabel_format(style='plain', axis='both')
        ax2.set_xticklabels([f'${x/1e6:.1f}M' if x >= 1e6 else f'${x/1e3:.0f}K' for x in ax2.get_xticks()])
        ax2.set_yticklabels([f'${y/1e6:.1f}M' if y >= 1e6 else f'${y/1e3:.0f}K' for y in ax2.get_yticks()])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Comparison chart saved to {save_path}")
        
        plt.show()
    
    def export_to_excel(self, filename: str) -> None:
        """
        Export all results to an Excel file with multiple sheets
        
        Args:
            filename: Output Excel filename
        """
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = self.run_all_scenarios()
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed results for each scenario
            for scenario_id, results in self.simulation_results.items():
                # Create detailed dataframe
                detailed_df = pd.DataFrame({
                    'Iteration': range(1, len(results['ale_samples']) + 1),
                    'TEF': results['tef_samples'],
                    'Vulnerability': results['vuln_samples'],
                    'Loss Magnitude': results['loss_samples'],
                    'LEF': results['lef_samples'],
                    'Annual Loss': results['ale_samples']
                })
                
                sheet_name = f'Sim_{scenario_id}'[:31]  # Excel sheet name limit
                detailed_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Scenario definitions
            scenarios_df = pd.DataFrame([{
                'Scenario ID': s['id'],
                'Description': s['description'],
                'TEF Low': s['tef']['low'],
                'TEF Medium': s['tef']['medium'],
                'TEF High': s['tef']['high'],
                'Vuln Low': s['vulnerability']['low'],
                'Vuln Medium': s['vulnerability']['medium'],
                'Vuln High': s['vulnerability']['high'],
                'Loss Low': s['loss_magnitude']['low'],
                'Loss Medium': s['loss_magnitude']['medium'],
                'Loss High': s['loss_magnitude']['high'],
                'Asset': s['asset'],
                'Threat Actor': s['threat_actor'],
                'Loss Effect': s['loss_effect'],
                'Notes': s['notes']
            } for s in self.scenarios])
            scenarios_df.to_excel(writer, sheet_name='Scenarios', index=False)
        
        print(f"Results exported to {filename}")
    
    def export_to_json(self, filename: str) -> None:
        """
        Export results to JSON format
        
        Args:
            filename: Output JSON filename
        """
        export_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'iterations': self.iterations,
                'total_scenarios': len(self.scenarios)
            },
            'scenarios': self.scenarios,
            'results': {}
        }
        
        for scenario_id, results in self.simulation_results.items():
            export_data['results'][scenario_id] = {
                'description': results['description'],
                'statistics': results['statistics'],
                'distribution_type': results['distribution_type']
            }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Results exported to {filename}")


def main():
    """
    Main function with example usage
    """
    parser = argparse.ArgumentParser(description='FAIR Risk Calculator')
    parser.add_argument('--iterations', type=int, default=10000,
                       help='Number of Monte Carlo iterations (default: 10000)')
    parser.add_argument('--distribution', choices=['pert', 'uniform'], default='pert',
                       help='Distribution type (default: pert)')
    parser.add_argument('--export-excel', type=str, help='Export results to Excel file')
    parser.add_argument('--export-json', type=str, help='Export results to JSON file')
    parser.add_argument('--save-plots', type=str, help='Save plots to specified directory')
    parser.add_argument('--demo', action='store_true', help='Run demo with sample scenarios')
    
    args = parser.parse_args()
    
    # Initialize calculator
    calculator = FAIRRiskCalculator(iterations=args.iterations)
    
    if args.demo:
        print("Running demo with sample scenarios...")
        
        # Add sample scenarios based on the Excel file
        calculator.add_scenario(
            scenario_id="S1",
            description="Data Breach - Customer PII",
            tef_low=1, tef_medium=3, tef_high=6,
            vuln_low=0.2, vuln_medium=0.5, vuln_high=0.85,
            loss_low=500000, loss_medium=2080000, loss_high=3500000,
            asset="Customer Database",
            threat_actor="External Attacker",
            loss_effect="Confidentiality",
            notes="Based on industry breach statistics"
        )
        
        calculator.add_scenario(
            scenario_id="S2",
            description="Ransomware Attack",
            tef_low=2, tef_medium=5, tef_high=10,
            vuln_low=0.1, vuln_medium=0.3, vuln_high=0.6,
            loss_low=250000, loss_medium=1500000, loss_high=5000000,
            asset="All Systems",
            threat_actor="Ransomware Group",
            loss_effect="Availability",
            notes="Including recovery and downtime costs"
        )
        
        calculator.add_scenario(
            scenario_id="S3",
            description="Insider Threat - Data Theft",
            tef_low=0.5, tef_medium=2, tef_high=4,
            vuln_low=0.3, vuln_medium=0.6, vuln_high=0.9,
            loss_low=100000, loss_medium=750000, loss_high=2000000,
            asset="Intellectual Property",
            threat_actor="Malicious Insider",
            loss_effect="Confidentiality",
            notes="Deliberate data exfiltration scenario"
        )
        
        calculator.add_scenario(
            scenario_id="S4",
            description="DDoS Attack",
            tef_low=5, tef_medium=15, tef_high=30,
            vuln_low=0.2, vuln_medium=0.4, vuln_high=0.7,
            loss_low=10000, loss_medium=50000, loss_high=200000,
            asset="Public Website",
            threat_actor="Hacktivist",
            loss_effect="Availability",
            notes="Service disruption and mitigation costs"
        )
        
        # Run simulations
        print("\nRunning simulations...")
        for scenario in calculator.scenarios:
            print(f"  - Simulating {scenario['id']}: {scenario['description']}")
            calculator.run_simulation(scenario['id'], distribution=args.distribution)
        
        # Display results
        print("\n" + "="*80)
        print("SIMULATION RESULTS SUMMARY")
        print("="*80)
        
        summary = calculator.run_all_scenarios()
        print(summary.to_string())
        
        # Create visualizations
        print("\nGenerating visualizations...")
        for scenario in calculator.scenarios:
            if args.save_plots:
                save_path = f"{args.save_plots}/{scenario['id']}_analysis.png"
            else:
                save_path = None
            calculator.create_visualizations(scenario['id'], save_path)
        
        # Create comparison chart
        if args.save_plots:
            comparison_path = f"{args.save_plots}/scenario_comparison.png"
        else:
            comparison_path = None
        calculator.create_comparison_chart(comparison_path)
        
        # Export results if requested
        if args.export_excel:
            calculator.export_to_excel(args.export_excel)
        
        if args.export_json:
            calculator.export_to_json(args.export_json)
    
    else:
        print("FAIR Risk Calculator initialized.")
        print("\nTo use the calculator:")
        print("1. Add scenarios using calculator.add_scenario()")
        print("2. Run simulations using calculator.run_simulation(scenario_id)")
        print("3. Create visualizations using calculator.create_visualizations(scenario_id)")
        print("4. Export results using calculator.export_to_excel() or export_to_json()")
        print("\nRun with --demo flag to see example usage.")
        
        # Interactive mode
        print("\nEntering interactive mode...")
        print("Example code to get started:")
        print("""
calculator = FAIRRiskCalculator(iterations=10000)

# Add a scenario
calculator.add_scenario(
    scenario_id="S1",
    description="Your Risk Scenario",
    tef_low=1, tef_medium=3, tef_high=6,
    vuln_low=0.2, vuln_medium=0.5, vuln_high=0.85,
    loss_low=500000, loss_medium=2080000, loss_high=3500000
)

# Run simulation
results = calculator.run_simulation("S1")

# Create visualization
calculator.create_visualizations("S1")

# Export to Excel
calculator.export_to_excel("risk_analysis.xlsx")
        """)


if __name__ == "__main__":
    main()
