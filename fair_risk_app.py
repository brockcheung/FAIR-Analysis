#!/usr/bin/env python3
"""
FAIR Risk Calculator - Streamlit Web Interface
Interactive web application for FAIR risk assessment
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
from io import BytesIO
import xlsxwriter

# Auto-integrity protection (optional - auto-generates on first run)
AUTO_INTEGRITY_AVAILABLE = False
try:
    # Only import if auto_integrity.py exists
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'auto_integrity.py')):
        from auto_integrity import ensure_integrity
        AUTO_INTEGRITY_AVAILABLE = True
except ImportError:
    pass

# Page configuration
st.set_page_config(
    page_title="FAIR Risk Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-integrity check (runs once per session)
if AUTO_INTEGRITY_AVAILABLE:
    if 'integrity_checked' not in st.session_state:
        st.session_state.integrity_checked = False

    if not st.session_state.integrity_checked:
        # Run integrity check
        integrity_result = ensure_integrity(auto_generate=True, strict=False, silent=True)
        st.session_state.integrity_checked = True
        st.session_state.integrity_status = integrity_result

        # Show result in sidebar
        if not integrity_result:
            # Tampering detected
            with st.sidebar:
                st.error("🚨 SECURITY ALERT")
                st.error("Code Tampering Detected!")
                st.warning("⚠️ The FAIR Risk Calculator code has been modified since the security baseline was established.")
                with st.expander("⚠️ See Details & Recommended Actions"):
                    st.markdown("""
**This could indicate:**
- Malicious tampering by an adversary
- Accidental modification
- Legitimate update without regenerating baseline

**Recommended actions:**

1. **If you made legitimate changes**, regenerate the baseline:
   ```bash
   python generate_integrity_manifest.py
   ```

2. **If you did NOT make changes**, restore from backup and investigate immediately

3. **For detailed information**:
   ```bash
   python verify_integrity.py --verbose
   ```

**⚠️ WARNING: Results may not be trustworthy!**
""")
        else:
            # Integrity verified
            with st.sidebar:
                st.success("🔒 Code Integrity: Verified")
else:
    # Integrity system not available
    if 'integrity_checked' not in st.session_state:
        st.session_state.integrity_checked = True
        st.session_state.integrity_status = True

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #cccccc;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

class FAIRCalculator:
    """
    Streamlit-compatible FAIR risk calculator

    Implements the FAIR model: Risk = LEF × LM
    Where LEF (Loss Event Frequency) = TEF × Vulnerability
    """

    @staticmethod
    def pert_distribution(low, medium, high, size=10000):
        """
        Generate PERT distribution samples

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
    def triangular_distribution(low, medium, high, size=10000):
        """
        Generate triangular distribution samples (simpler alternative to PERT)

        Args:
            low: Minimum value
            medium: Most likely value (mode/peak)
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
                f"Triangular distribution requires low ≤ medium ≤ high. "
                f"Got: low={low}, medium={medium}, high={high}"
            )

        return np.random.triangular(low, medium, high, size)

    @staticmethod
    def run_simulation(tef_params, vuln_params, loss_params, iterations=10000, dist_type='pert'):
        """
        Run Monte Carlo simulation for FAIR risk analysis

        Implements: ALE = TEF × Vulnerability × Loss Magnitude

        Args:
            tef_params: dict with 'low', 'medium', 'high' for TEF
            vuln_params: dict with 'low', 'medium', 'high' for Vulnerability
            loss_params: dict with 'low', 'medium', 'high' for Loss Magnitude
            iterations: number of Monte Carlo iterations
            dist_type: 'pert' or 'triangular'

        Returns:
            Dictionary with simulation results and comprehensive statistics
        """

        if dist_type == 'pert':
            tef_samples = FAIRCalculator.pert_distribution(
                tef_params['low'], tef_params['medium'], tef_params['high'], iterations
            )
            vuln_samples = FAIRCalculator.pert_distribution(
                vuln_params['low'], vuln_params['medium'], vuln_params['high'], iterations
            )
            loss_samples = FAIRCalculator.pert_distribution(
                loss_params['low'], loss_params['medium'], loss_params['high'], iterations
            )
        else:  # triangular
            tef_samples = FAIRCalculator.triangular_distribution(
                tef_params['low'], tef_params['medium'], tef_params['high'], iterations
            )
            vuln_samples = FAIRCalculator.triangular_distribution(
                vuln_params['low'], vuln_params['medium'], vuln_params['high'], iterations
            )
            loss_samples = FAIRCalculator.triangular_distribution(
                loss_params['low'], loss_params['medium'], loss_params['high'], iterations
            )

        # FAIR Model: Calculate LEF and ALE
        lef_samples = tef_samples * vuln_samples
        ale_samples = lef_samples * loss_samples

        # Calculate VaR once to avoid redundant computation
        var95_value = np.percentile(ale_samples, 95)

        return {
            'tef': tef_samples,
            'vuln': vuln_samples,
            'loss': loss_samples,
            'lef': lef_samples,
            'ale': ale_samples,
            'stats': {
                'mean': np.mean(ale_samples),
                'median': np.median(ale_samples),
                'std': np.std(ale_samples, ddof=1),  # Sample std dev
                'min': np.min(ale_samples),
                'max': np.max(ale_samples),
                'p10': np.percentile(ale_samples, 10),
                'p25': np.percentile(ale_samples, 25),
                'p50': np.percentile(ale_samples, 50),
                'p75': np.percentile(ale_samples, 75),
                'p90': np.percentile(ale_samples, 90),
                'p95': np.percentile(ale_samples, 95),
                'p99': np.percentile(ale_samples, 99),
                'var95': var95_value,  # Value at Risk (95%)
                'cvar95': np.mean(ale_samples[ale_samples >= var95_value]),  # Conditional VaR
                'prob_zero': np.sum(ale_samples == 0) / len(ale_samples),
                'prob_1m': np.sum(ale_samples > 1000000) / len(ale_samples),
                'prob_5m': np.sum(ale_samples > 5000000) / len(ale_samples),
                'prob_10m': np.sum(ale_samples > 10000000) / len(ale_samples)
            }
        }

def init_session_state():
    """Initialize session state variables"""
    if 'scenarios' not in st.session_state:
        st.session_state.scenarios = []
    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = {}
    if 'current_scenario_id' not in st.session_state:
        st.session_state.current_scenario_id = 1

def main():
    """Main Streamlit application"""
    
    init_session_state()
    
    # Header
    st.title("🛡️ FAIR Risk Calculator")
    st.markdown("**Factor Analysis of Information Risk (FAIR)** - Quantitative Cyber Risk Assessment Tool")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        iterations = st.number_input(
            "Monte Carlo Iterations",
            min_value=1000,
            max_value=100000,
            value=10000,
            step=1000,
            help="Number of simulation iterations. Higher values give more accurate results but take longer."
        )
        
        dist_type = st.selectbox(
            "Distribution Type",
            options=['pert', 'triangular'],
            format_func=lambda x: 'PERT (Recommended)' if x == 'pert' else 'Triangular',
            help="PERT uses Beta distribution (recommended). Triangular is simpler but uses all three parameters."
        )
        
        st.divider()
        
        # Quick load sample data
        if st.button("📥 Load Sample Scenarios", type="secondary"):
            sample_scenarios = [
                {
                    'id': 'S1',
                    'name': 'Data Breach - Customer PII',
                    'tef': {'low': 1, 'medium': 3, 'high': 6},
                    'vuln': {'low': 0.2, 'medium': 0.5, 'high': 0.85},
                    'loss': {'low': 500000, 'medium': 2080000, 'high': 3500000},
                    'asset': 'Customer Database',
                    'threat': 'External Attacker',
                    'effect': 'Confidentiality'
                },
                {
                    'id': 'S2',
                    'name': 'Ransomware Attack',
                    'tef': {'low': 2, 'medium': 5, 'high': 10},
                    'vuln': {'low': 0.1, 'medium': 0.3, 'high': 0.6},
                    'loss': {'low': 250000, 'medium': 1500000, 'high': 5000000},
                    'asset': 'All Systems',
                    'threat': 'Ransomware Group',
                    'effect': 'Availability'
                },
                {
                    'id': 'S3',
                    'name': 'Insider Threat',
                    'tef': {'low': 0.5, 'medium': 2, 'high': 4},
                    'vuln': {'low': 0.3, 'medium': 0.6, 'high': 0.9},
                    'loss': {'low': 100000, 'medium': 750000, 'high': 2000000},
                    'asset': 'Intellectual Property',
                    'threat': 'Malicious Insider',
                    'effect': 'Confidentiality'
                }
            ]
            st.session_state.scenarios = sample_scenarios
            st.success("Sample scenarios loaded!")
            st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Scenario Input", 
        "🎲 Run Simulations", 
        "📊 Analysis Results",
        "🔄 Scenario Comparison",
        "💾 Export Data"
    ])
    
    # Tab 1: Scenario Input
    with tab1:
        st.header("Define Risk Scenarios")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Add New Scenario")
            
            with st.form("scenario_form"):
                scenario_id = st.text_input("Scenario ID", value=f"S{st.session_state.current_scenario_id}")
                scenario_name = st.text_input("Scenario Name", placeholder="e.g., Data Breach - Customer PII")
                
                st.markdown("### Threat Event Frequency (TEF)")
                st.caption("Expected number of threat events per year")
                tef_cols = st.columns(3)
                tef_low = tef_cols[0].number_input("Low", min_value=0.0, value=1.0, step=0.1)
                tef_medium = tef_cols[1].number_input("Most Likely", min_value=0.0, value=3.0, step=0.1)
                tef_high = tef_cols[2].number_input("High", min_value=0.0, value=6.0, step=0.1)
                
                st.markdown("### Vulnerability (%)")
                st.caption("Probability that a threat event results in a loss (0-1)")
                vuln_cols = st.columns(3)
                vuln_low = vuln_cols[0].number_input("Low", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
                vuln_medium = vuln_cols[1].number_input("Most Likely ", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
                vuln_high = vuln_cols[2].number_input("High ", min_value=0.0, max_value=1.0, value=0.85, step=0.05)
                
                st.markdown("### Loss Magnitude ($)")
                st.caption("Financial impact when a loss event occurs")
                loss_cols = st.columns(3)
                loss_low = loss_cols[0].number_input("Low ($)", min_value=0, value=500000, step=10000)
                loss_medium = loss_cols[1].number_input("Most Likely ($)", min_value=0, value=2080000, step=10000)
                loss_high = loss_cols[2].number_input("High ($)", min_value=0, value=3500000, step=10000)
                
                st.markdown("### Additional Information (Optional)")
                info_cols = st.columns(3)
                asset = info_cols[0].text_input("Asset at Risk", placeholder="e.g., Customer Database")
                threat = info_cols[1].text_input("Threat Actor", placeholder="e.g., External Attacker")
                effect = info_cols[2].text_input("Loss Effect", placeholder="e.g., Confidentiality")
                
                notes = st.text_area("Notes/Assumptions", placeholder="Any additional context or assumptions...")
                
                submitted = st.form_submit_button("Add Scenario", type="primary")
                
                if submitted:
                    if not scenario_name:
                        st.error("Please provide a scenario name")
                    else:
                        # Validate input values
                        validation_errors = []

                        # Validate TEF (Threat Event Frequency)
                        if not (tef_low <= tef_medium <= tef_high):
                            validation_errors.append(
                                f"⚠️ **TEF Error:** Values must be in ascending order (Low ≤ Medium ≤ High). "
                                f"Got: Low={tef_low}, Medium={tef_medium}, High={tef_high}"
                            )

                        # Validate Vulnerability
                        if not (vuln_low <= vuln_medium <= vuln_high):
                            validation_errors.append(
                                f"⚠️ **Vulnerability Error:** Values must be in ascending order (Low ≤ Medium ≤ High). "
                                f"Got: Low={vuln_low:.2f}, Medium={vuln_medium:.2f}, High={vuln_high:.2f}"
                            )

                        # Validate Loss Magnitude
                        if not (loss_low <= loss_medium <= loss_high):
                            validation_errors.append(
                                f"⚠️ **Loss Magnitude Error:** Values must be in ascending order (Low ≤ Medium ≤ High). "
                                f"Got: Low=${loss_low:,.0f}, Medium=${loss_medium:,.0f}, High=${loss_high:,.0f}"
                            )

                        # Display validation errors or add scenario
                        if validation_errors:
                            st.error("**Input Validation Failed:**")
                            for error in validation_errors:
                                st.markdown(error)
                            st.info("💡 **Tip:** Ensure that Low ≤ Medium ≤ High for all three parameters (TEF, Vulnerability, Loss Magnitude)")
                        else:
                            new_scenario = {
                                'id': scenario_id,
                                'name': scenario_name,
                                'tef': {'low': tef_low, 'medium': tef_medium, 'high': tef_high},
                                'vuln': {'low': vuln_low, 'medium': vuln_medium, 'high': vuln_high},
                                'loss': {'low': loss_low, 'medium': loss_medium, 'high': loss_high},
                                'asset': asset,
                                'threat': threat,
                                'effect': effect,
                                'notes': notes
                            }
                            st.session_state.scenarios.append(new_scenario)
                            st.session_state.current_scenario_id += 1
                            st.success(f"✅ Scenario '{scenario_name}' added successfully!")
                            st.rerun()
        
        with col2:
            st.subheader("Current Scenarios")
            if st.session_state.scenarios:
                for i, scenario in enumerate(st.session_state.scenarios):
                    with st.expander(f"{scenario['id']}: {scenario['name']}"):
                        st.write(f"**TEF:** {scenario['tef']['low']}-{scenario['tef']['medium']}-{scenario['tef']['high']}")
                        st.write(f"**Vuln:** {scenario['vuln']['low']:.0%}-{scenario['vuln']['medium']:.0%}-{scenario['vuln']['high']:.0%}")
                        st.write(f"**Loss:** ${scenario['loss']['low']:,.0f}-${scenario['loss']['medium']:,.0f}-${scenario['loss']['high']:,.0f}")
                        if st.button(f"Remove", key=f"remove_{i}"):
                            st.session_state.scenarios.pop(i)
                            st.rerun()
            else:
                st.info("No scenarios added yet. Add a scenario or load samples from the sidebar.")
    
    # Tab 2: Run Simulations
    with tab2:
        st.header("Run Monte Carlo Simulations")
        
        if not st.session_state.scenarios:
            st.warning("Please add at least one scenario in the Scenario Input tab first.")
        else:
            st.info(f"Ready to run simulations for {len(st.session_state.scenarios)} scenario(s) with {iterations:,} iterations each.")
            
            if st.button("🚀 Run All Simulations", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, scenario in enumerate(st.session_state.scenarios):
                    status_text.text(f"Running simulation for {scenario['name']}...")
                    progress_bar.progress((i + 1) / len(st.session_state.scenarios))
                    
                    results = FAIRCalculator.run_simulation(
                        scenario['tef'],
                        scenario['vuln'],
                        scenario['loss'],
                        iterations,
                        dist_type
                    )
                    
                    st.session_state.simulation_results[scenario['id']] = {
                        'scenario': scenario,
                        'results': results
                    }
                
                status_text.text("All simulations completed!")
                st.success(f"✅ Successfully ran {len(st.session_state.scenarios)} simulations!")
                
                # Display quick summary
                st.subheader("Quick Summary")
                summary_data = []
                for scenario in st.session_state.scenarios:
                    if scenario['id'] in st.session_state.simulation_results:
                        stats = st.session_state.simulation_results[scenario['id']]['results']['stats']
                        summary_data.append({
                            'Scenario': scenario['name'],
                            'Mean Loss': f"${stats['mean']:,.0f}",
                            '90th Percentile': f"${stats['p90']:,.0f}",
                            'VaR (95%)': f"${stats['var95']:,.0f}",
                            'P(Loss > $1M)': f"{stats['prob_1m']:.1%}"
                        })
                
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
    
    # Tab 3: Analysis Results
    with tab3:
        st.header("Detailed Risk Analysis")
        
        if not st.session_state.simulation_results:
            st.warning("No simulation results available. Please run simulations first.")
        else:
            scenario_names = [s['name'] for s in st.session_state.scenarios if s['id'] in st.session_state.simulation_results]
            selected_scenario_name = st.selectbox("Select Scenario for Analysis", scenario_names)
            
            if selected_scenario_name:
                # Find the selected scenario
                selected_scenario = next(s for s in st.session_state.scenarios if s['name'] == selected_scenario_name)
                sim_data = st.session_state.simulation_results[selected_scenario['id']]
                results = sim_data['results']
                stats = results['stats']
                
                # Key metrics
                st.subheader("Key Risk Metrics")
                metric_cols = st.columns(4)
                metric_cols[0].metric("Mean Annual Loss", f"${stats['mean']:,.0f}")
                metric_cols[1].metric("90th Percentile", f"${stats['p90']:,.0f}")
                metric_cols[2].metric("Value at Risk (95%)", f"${stats['var95']:,.0f}")
                metric_cols[3].metric("P(Loss > $1M)", f"{stats['prob_1m']:.1%}")
                
                # Visualizations
                st.subheader("Risk Visualizations")
                
                # Create subplot figure
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Loss Distribution', 'Cumulative Distribution',
                                  'Risk Components', 'Loss Exceedance Curve'),
                    specs=[[{'type': 'histogram'}, {'type': 'scatter'}],
                          [{'type': 'box'}, {'type': 'scatter'}]]
                )
                
                # 1. Loss Distribution Histogram
                fig.add_trace(
                    go.Histogram(x=results['ale'], nbinsx=50, name='Annual Loss', showlegend=False),
                    row=1, col=1
                )
                fig.add_vline(x=stats['mean'], line_dash="dash", line_color="red", row=1, col=1)
                fig.add_vline(x=stats['p90'], line_dash="dash", line_color="orange", row=1, col=1)
                
                # 2. Cumulative Distribution
                sorted_losses = np.sort(results['ale'])
                cumulative = np.arange(1, len(sorted_losses) + 1) / len(sorted_losses)
                fig.add_trace(
                    go.Scatter(x=sorted_losses, y=cumulative, mode='lines', name='CDF', showlegend=False),
                    row=1, col=2
                )
                
                # 3. Risk Components Box Plot
                fig.add_trace(
                    go.Box(y=results['tef'], name='TEF', showlegend=False),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Box(y=results['vuln']*100, name='Vuln %', showlegend=False),
                    row=2, col=1
                )
                
                # 4. Loss Exceedance Curve
                exceedance = 1 - cumulative
                fig.add_trace(
                    go.Scatter(x=sorted_losses, y=exceedance, mode='lines', name='Exceedance', showlegend=False),
                    row=2, col=2
                )
                
                # Update layout
                fig.update_layout(height=700, showlegend=False)
                fig.update_xaxes(title_text="Annual Loss ($)", row=1, col=1)
                fig.update_xaxes(title_text="Annual Loss ($)", row=1, col=2)
                fig.update_xaxes(title_text="Component", row=2, col=1)
                fig.update_xaxes(title_text="Annual Loss ($)", row=2, col=2)
                fig.update_yaxes(title_text="Frequency", row=1, col=1)
                fig.update_yaxes(title_text="Cumulative Probability", row=1, col=2)
                fig.update_yaxes(title_text="Value", row=2, col=1)
                fig.update_yaxes(title_text="Exceedance Probability", row=2, col=2)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed statistics table
                st.subheader("Statistical Summary")
                stats_df = pd.DataFrame({
                    'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 
                              '10th %ile', '25th %ile', '75th %ile', '90th %ile', 
                              '95th %ile (VaR)', '99th %ile', 'CVaR (95%)',
                              'P(Loss = $0)', 'P(Loss > $1M)', 'P(Loss > $5M)'],
                    'Value': [
                        f"${stats['mean']:,.0f}",
                        f"${stats['median']:,.0f}",
                        f"${stats['std']:,.0f}",
                        f"${stats['min']:,.0f}",
                        f"${stats['max']:,.0f}",
                        f"${stats['p10']:,.0f}",
                        f"${stats['p25']:,.0f}",
                        f"${stats['p75']:,.0f}",
                        f"${stats['p90']:,.0f}",
                        f"${stats['var95']:,.0f}",
                        f"${stats['p99']:,.0f}",
                        f"${stats['cvar95']:,.0f}",
                        f"{stats['prob_zero']:.2%}",
                        f"{stats['prob_1m']:.2%}",
                        f"{stats['prob_5m']:.2%}"
                    ]
                })
                
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(stats_df.iloc[:8], use_container_width=True, hide_index=True)
                with col2:
                    st.dataframe(stats_df.iloc[8:], use_container_width=True, hide_index=True)
    
    # Tab 4: Scenario Comparison
    with tab4:
        st.header("Compare Risk Scenarios")
        
        if len(st.session_state.simulation_results) < 2:
            st.warning("Please run simulations for at least 2 scenarios to enable comparison.")
        else:
            # Prepare comparison data
            comparison_data = []
            for scenario in st.session_state.scenarios:
                if scenario['id'] in st.session_state.simulation_results:
                    stats = st.session_state.simulation_results[scenario['id']]['results']['stats']
                    comparison_data.append({
                        'Scenario': scenario['name'],
                        'Mean': stats['mean'],
                        '90th %ile': stats['p90'],
                        'VaR 95%': stats['var95'],
                        'CVaR 95%': stats['cvar95']
                    })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Bar chart comparison
            fig_bar = go.Figure()
            
            metrics = ['Mean', '90th %ile', 'VaR 95%', 'CVaR 95%']
            for metric in metrics:
                fig_bar.add_trace(go.Bar(
                    name=metric,
                    x=comparison_df['Scenario'],
                    y=comparison_df[metric],
                    text=[f'${v:,.0f}' for v in comparison_df[metric]],
                    textposition='auto',
                ))
            
            fig_bar.update_layout(
                title='Risk Metrics Comparison',
                xaxis_title='Scenario',
                yaxis_title='Annual Loss ($)',
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Risk matrix scatter plot
            fig_scatter = px.scatter(
                comparison_df,
                x='Mean',
                y='VaR 95%',
                size='CVaR 95%',
                hover_name='Scenario',
                labels={'Mean': 'Mean Annual Loss ($)', 'VaR 95%': 'Value at Risk 95% ($)'},
                title='Risk Matrix: Mean Loss vs VaR',
                size_max=50
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Comparison table
            st.subheader("Detailed Comparison")
            formatted_df = comparison_df.copy()
            for col in ['Mean', '90th %ile', 'VaR 95%', 'CVaR 95%']:
                formatted_df[col] = formatted_df[col].apply(lambda x: f'${x:,.0f}')
            st.dataframe(formatted_df, use_container_width=True, hide_index=True)
    
    # Tab 5: Export Data
    with tab5:
        st.header("Export Results")
        
        if not st.session_state.simulation_results:
            st.warning("No results to export. Please run simulations first.")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("📊 Export to Excel")
                if st.button("Generate Excel Report", type="primary"):
                    # Create Excel file in memory
                    output = BytesIO()
                    
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        # Summary sheet
                        summary_data = []
                        for scenario in st.session_state.scenarios:
                            if scenario['id'] in st.session_state.simulation_results:
                                stats = st.session_state.simulation_results[scenario['id']]['results']['stats']
                                summary_data.append({
                                    'Scenario ID': scenario['id'],
                                    'Scenario Name': scenario['name'],
                                    'Mean Loss': stats['mean'],
                                    'Median Loss': stats['median'],
                                    '90th Percentile': stats['p90'],
                                    'VaR 95%': stats['var95'],
                                    'CVaR 95%': stats['cvar95'],
                                    'P(Loss > $1M)': stats['prob_1m']
                                })
                        
                        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                        
                        # Scenario definitions
                        scenarios_data = []
                        for scenario in st.session_state.scenarios:
                            scenarios_data.append({
                                'ID': scenario['id'],
                                'Name': scenario['name'],
                                'TEF Low': scenario['tef']['low'],
                                'TEF Medium': scenario['tef']['medium'],
                                'TEF High': scenario['tef']['high'],
                                'Vuln Low': scenario['vuln']['low'],
                                'Vuln Medium': scenario['vuln']['medium'],
                                'Vuln High': scenario['vuln']['high'],
                                'Loss Low': scenario['loss']['low'],
                                'Loss Medium': scenario['loss']['medium'],
                                'Loss High': scenario['loss']['high']
                            })
                        
                        pd.DataFrame(scenarios_data).to_excel(writer, sheet_name='Scenarios', index=False)
                    
                    output.seek(0)
                    
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=output,
                        file_name=f"fair_risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col2:
                st.subheader("📄 Export to JSON")
                if st.button("Generate JSON Report"):
                    export_data = {
                        'metadata': {
                            'generated_at': datetime.now().isoformat(),
                            'iterations': iterations,
                            'distribution': dist_type,
                            'total_scenarios': len(st.session_state.scenarios)
                        },
                        'scenarios': st.session_state.scenarios,
                        'results': {}
                    }
                    
                    for scenario_id, sim_data in st.session_state.simulation_results.items():
                        export_data['results'][scenario_id] = {
                            'statistics': sim_data['results']['stats']
                        }
                    
                    json_str = json.dumps(export_data, indent=2, default=str)
                    
                    st.download_button(
                        label="📥 Download JSON Report",
                        data=json_str,
                        file_name=f"fair_risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col3:
                st.subheader("📊 Export to CSV")
                if st.button("Generate CSV Report"):
                    # Create detailed CSV
                    csv_data = []
                    for scenario in st.session_state.scenarios:
                        if scenario['id'] in st.session_state.simulation_results:
                            results = st.session_state.simulation_results[scenario['id']]['results']
                            for i in range(len(results['ale'])):
                                csv_data.append({
                                    'Scenario': scenario['name'],
                                    'Iteration': i + 1,
                                    'TEF': results['tef'][i],
                                    'Vulnerability': results['vuln'][i],
                                    'Loss Magnitude': results['loss'][i],
                                    'LEF': results['lef'][i],
                                    'Annual Loss': results['ale'][i]
                                })
                    
                    df = pd.DataFrame(csv_data)
                    csv = df.to_csv(index=False)
                    
                    st.download_button(
                        label="📥 Download CSV Data",
                        data=csv,
                        file_name=f"fair_risk_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )

if __name__ == "__main__":
    main()
