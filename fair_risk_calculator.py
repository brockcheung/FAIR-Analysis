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


def get_user_input(prompt, input_type=str, min_val=None, max_val=None, default=None):
    """
    Get user input with validation
    """
    while True:
        try:
            user_input = input(f"{prompt} {f'[default: {default}]' if default else ''}: ").strip()
            
            if not user_input and default is not None:
                return default
            
            if input_type == float:
                value = float(user_input)
            elif input_type == int:
                value = int(user_input)
            else:
                value = user_input
            
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}")
                continue
            
            return value
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}")


def interactive_scenario_builder():
    """
    Interactive wizard for building risk scenarios
    """
    print("\n" + "="*60)
    print("RISK SCENARIO BUILDER")
    print("="*60)
    print("\nLet's build your risk scenario step by step.")
    print("For each parameter, provide Low, Most Likely, and High estimates.\n")
    
    # Basic Information
    scenario_id = get_user_input("Scenario ID (e.g., S1)", default="S1")
    description = get_user_input("Scenario Description (e.g., 'Data Breach - Customer PII')")
    
    # Threat Event Frequency
    print("\n📊 THREAT EVENT FREQUENCY (TEF)")
    print("How many times per year could this threat occur?")
    print("Examples: Phishing (100-365), Ransomware (1-10), Insider threat (0.5-5)")
    tef_low = get_user_input("  TEF - Low estimate", float, 0, default=1.0)
    tef_medium = get_user_input("  TEF - Most likely", float, 0, default=3.0)
    tef_high = get_user_input("  TEF - High estimate", float, 0, default=6.0)
    
    # Vulnerability
    print("\n🎯 VULNERABILITY")
    print("What's the probability (0-100%) that the threat succeeds if it occurs?")
    print("Examples: With good controls (10-30%), Average controls (30-60%), Poor controls (60-90%)")
    vuln_low = get_user_input("  Vulnerability - Low (0-1)", float, 0, 1, default=0.2)
    vuln_medium = get_user_input("  Vulnerability - Most likely (0-1)", float, 0, 1, default=0.5)
    vuln_high = get_user_input("  Vulnerability - High (0-1)", float, 0, 1, default=0.85)
    
    # Loss Magnitude
    print("\n💰 LOSS MAGNITUDE ($)")
    print("What's the financial impact if the incident occurs?")
    print("Include: Response costs, legal fees, fines, business disruption, reputation damage")
    loss_low = get_user_input("  Loss - Low estimate ($)", float, 0, default=500000)
    loss_medium = get_user_input("  Loss - Most likely ($)", float, 0, default=2080000)
    loss_high = get_user_input("  Loss - High estimate ($)", float, 0, default=3500000)
    
    # Optional Details
    print("\n📝 ADDITIONAL DETAILS (Optional - press Enter to skip)")
    asset = get_user_input("Asset at risk", default="")
    threat_actor = get_user_input("Threat actor", default="")
    loss_effect = get_user_input("Loss effect (Confidentiality/Integrity/Availability)", default="")
    notes = get_user_input("Notes/Assumptions", default="")
    
    return {
        'scenario_id': scenario_id,
        'description': description,
        'tef_low': tef_low,
        'tef_medium': tef_medium,
        'tef_high': tef_high,
        'vuln_low': vuln_low,
        'vuln_medium': vuln_medium,
        'vuln_high': vuln_high,
        'loss_low': loss_low,
        'loss_medium': loss_medium,
        'loss_high': loss_high,
        'asset': asset,
        'threat_actor': threat_actor,
        'loss_effect': loss_effect,
        'notes': notes
    }


def display_results(results):
    """
    Display simulation results in a formatted way
    """
    stats = results['statistics']
    
    print("\n" + "="*60)
    print("RISK ANALYSIS RESULTS")
    print("="*60)
    
    print("\n📊 KEY METRICS")
    print(f"  Mean Annual Loss:        ${stats['mean_loss']:,.0f}")
    print(f"  Median Annual Loss:      ${stats['median_loss']:,.0f}")
    print(f"  Standard Deviation:      ${stats['std_loss']:,.0f}")
    
    print("\n📈 PERCENTILES")
    print(f"  10th Percentile:         ${stats['percentile_10']:,.0f}")
    print(f"  25th Percentile:         ${stats['percentile_25']:,.0f}")
    print(f"  50th Percentile:         ${stats['percentile_50']:,.0f}")
    print(f"  75th Percentile:         ${stats['percentile_75']:,.0f}")
    print(f"  90th Percentile:         ${stats['percentile_90']:,.0f}")
    print(f"  95th Percentile (VaR):   ${stats['var_95']:,.0f}")
    print(f"  99th Percentile:         ${stats['percentile_99']:,.0f}")
    
    print("\n⚠️ RISK INDICATORS")
    print(f"  Value at Risk (95%):     ${stats['var_95']:,.0f}")
    print(f"  Conditional VaR (95%):   ${stats['cvar_95']:,.0f}")
    
    print("\n📊 PROBABILITY ANALYSIS")
    print(f"  P(Loss = $0):            {stats['probability_zero_loss']:.1%}")
    print(f"  P(Loss > $1M):           {stats['probability_over_1m']:.1%}")
    print(f"  P(Loss > $5M):           {stats['probability_over_5m']:.1%}")
    print(f"  P(Loss > $10M):          {stats['probability_over_10m']:.1%}")
    
    print("\n" + "="*60)


def main():
    """
    Main function with interactive mode
    """
    parser = argparse.ArgumentParser(description='FAIR Risk Calculator - Interactive Risk Assessment Tool')
    parser.add_argument('--iterations', type=int, default=10000,
                       help='Number of Monte Carlo iterations (default: 10000)')
    parser.add_argument('--distribution', choices=['pert', 'uniform'], default='pert',
                       help='Distribution type (default: pert)')
    parser.add_argument('--export-excel', type=str, help='Export results to Excel file')
    parser.add_argument('--export-json', type=str, help='Export results to JSON file')
    parser.add_argument('--save-plots', type=str, help='Save plots to specified directory')
    parser.add_argument('--batch', type=str, help='Load scenarios from JSON file for batch processing')
    parser.add_argument('--quick', action='store_true', help='Quick mode - single scenario analysis')
    
    args = parser.parse_args()
    
    # Initialize calculator
    calculator = FAIRRiskCalculator(iterations=args.iterations)
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║           FAIR RISK CALCULATOR - INTERACTIVE MODE          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"\nConfiguration: {args.iterations:,} iterations | {args.distribution.upper()} distribution\n")
    
    if args.batch:
        # Batch mode - load scenarios from JSON file
        try:
            with open(args.batch, 'r') as f:
                batch_data = json.load(f)
                scenarios = batch_data.get('scenarios', [])
                
            print(f"Loading {len(scenarios)} scenarios from {args.batch}...")
            for scenario in scenarios:
                calculator.add_scenario(**scenario)
                print(f"  ✓ Loaded: {scenario['scenario_id']} - {scenario['description']}")
            
        except Exception as e:
            print(f"Error loading batch file: {e}")
            return
    
    elif args.quick:
        # Quick mode - single scenario
        print("QUICK MODE - Single Scenario Analysis\n")
        scenario_data = interactive_scenario_builder()
        
        calculator.add_scenario(**scenario_data)
        
        print("\n🎲 Running simulation...")
        results = calculator.run_simulation(scenario_data['scenario_id'], distribution=args.distribution)
        
        display_results(results)
        
        # Ask if user wants visualization
        if get_user_input("\nGenerate visualization? (y/n)", default="y").lower() == 'y':
            if args.save_plots:
                save_path = f"{args.save_plots}/{scenario_data['scenario_id']}_analysis.png"
            else:
                save_path = None
            calculator.create_visualizations(scenario_data['scenario_id'], save_path)
    
    else:
        # Full interactive mode - multiple scenarios
        scenarios_added = 0
        
        while True:
            print("\n" + "-"*60)
            print("OPTIONS:")
            print("  1. Add new risk scenario")
            print("  2. Run simulations for all scenarios")
            print("  3. View results")
            print("  4. Generate visualizations")
            print("  5. Compare scenarios")
            print("  6. Export results")
            print("  7. Exit")
            print("-"*60)
            
            choice = get_user_input("Select option (1-7)", default="1")
            
            if choice == "1":
                # Add new scenario
                scenario_data = interactive_scenario_builder()
                calculator.add_scenario(**scenario_data)
                scenarios_added += 1
                print(f"\n✓ Scenario '{scenario_data['description']}' added successfully!")
                print(f"Total scenarios: {scenarios_added}")
            
            elif choice == "2":
                # Run simulations
                if not calculator.scenarios:
                    print("\n⚠️ No scenarios to simulate. Please add scenarios first.")
                else:
                    print(f"\n🎲 Running simulations for {len(calculator.scenarios)} scenarios...")
                    for scenario in calculator.scenarios:
                        print(f"  - Simulating: {scenario['id']} - {scenario['description']}")
                        calculator.run_simulation(scenario['id'], distribution=args.distribution)
                    print("\n✓ All simulations completed!")
            
            elif choice == "3":
                # View results
                if not calculator.simulation_results:
                    print("\n⚠️ No results available. Please run simulations first.")
                else:
                    print("\nAvailable results:")
                    for i, (sid, data) in enumerate(calculator.simulation_results.items(), 1):
                        print(f"  {i}. {sid} - {data['description']}")
                    
                    scenario_num = get_user_input("\nSelect scenario number to view", int, 1, len(calculator.simulation_results))
                    selected_id = list(calculator.simulation_results.keys())[scenario_num - 1]
                    display_results(calculator.simulation_results[selected_id])
            
            elif choice == "4":
                # Generate visualizations
                if not calculator.simulation_results:
                    print("\n⚠️ No results to visualize. Please run simulations first.")
                else:
                    print("\nVisualization options:")
                    print("  1. Individual scenario analysis")
                    print("  2. All scenarios")
                    
                    viz_choice = get_user_input("Select option (1-2)", default="1")
                    
                    if viz_choice == "1":
                        print("\nAvailable scenarios:")
                        for i, (sid, data) in enumerate(calculator.simulation_results.items(), 1):
                            print(f"  {i}. {sid} - {data['description']}")
                        
                        scenario_num = get_user_input("\nSelect scenario number", int, 1, len(calculator.simulation_results))
                        selected_id = list(calculator.simulation_results.keys())[scenario_num - 1]
                        
                        if args.save_plots:
                            save_path = f"{args.save_plots}/{selected_id}_analysis.png"
                        else:
                            save_path = None
                        
                        calculator.create_visualizations(selected_id, save_path)
                    
                    else:
                        print("\n📊 Generating visualizations for all scenarios...")
                        for sid in calculator.simulation_results.keys():
                            if args.save_plots:
                                save_path = f"{args.save_plots}/{sid}_analysis.png"
                            else:
                                save_path = None
                            calculator.create_visualizations(sid, save_path)
            
            elif choice == "5":
                # Compare scenarios
                if len(calculator.simulation_results) < 2:
                    print("\n⚠️ Need at least 2 scenarios for comparison. Please add and run more scenarios.")
                else:
                    print("\n📊 Generating scenario comparison...")
                    summary = calculator.run_all_scenarios()
                    print("\n" + "="*80)
                    print("SCENARIO COMPARISON")
                    print("="*80)
                    print(summary.to_string())
                    
                    if args.save_plots:
                        comparison_path = f"{args.save_plots}/scenario_comparison.png"
                    else:
                        comparison_path = None
                    calculator.create_comparison_chart(comparison_path)
            
            elif choice == "6":
                # Export results
                if not calculator.simulation_results:
                    print("\n⚠️ No results to export. Please run simulations first.")
                else:
                    export_choice = get_user_input("\nExport format (excel/json/both)", default="excel")
                    
                    if export_choice in ["excel", "both"]:
                        filename = args.export_excel or f"risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        calculator.export_to_excel(filename)
                        print(f"✓ Exported to Excel: {filename}")
                    
                    if export_choice in ["json", "both"]:
                        filename = args.export_json or f"risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        calculator.export_to_json(filename)
                        print(f"✓ Exported to JSON: {filename}")
            
            elif choice == "7":
                print("\nThank you for using FAIR Risk Calculator!")
                break
            
            else:
                print("\n⚠️ Invalid option. Please select 1-7.")
    
    # Final export if specified
    if calculator.simulation_results:
        if args.export_excel and not args.quick:
            calculator.export_to_excel(args.export_excel)
        if args.export_json and not args.quick:
            calculator.export_to_json(args.export_json)


if __name__ == "__main__":
    main()
