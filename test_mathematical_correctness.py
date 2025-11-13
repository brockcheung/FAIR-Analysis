#!/usr/bin/env python3
"""
Comprehensive Mathematical Correctness Test Suite
Tests FAIR methodology implementation, distributions, and statistical calculations

This test suite verifies:
1. PERT distribution correctness
2. Triangular distribution correctness
3. FAIR model calculations (ALE = TEF × V × LM)
4. Statistical metrics (VaR, CVaR, percentiles)
5. Input validation
6. Edge cases
7. Numerical stability
"""

import numpy as np
from fair_risk_calculator import FAIRRiskCalculator
import sys

# Set random seed for reproducible tests
np.random.seed(42)

class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record_pass(self, test_name):
        self.passed += 1
        print(f"✅ PASS: {test_name}")

    def record_fail(self, test_name, reason):
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"❌ FAIL: {test_name}")
        print(f"   Reason: {reason}")

    def summary(self):
        total = self.passed + self.failed
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%")

        if self.failed > 0:
            print("\nFailed Tests:")
            for test_name, reason in self.errors:
                print(f"  - {test_name}: {reason}")

        return self.failed == 0


results = TestResults()


def test_pert_distribution_mean():
    """Test that PERT distribution produces correct mean"""
    calc = FAIRRiskCalculator(iterations=100000, random_seed=42)

    # PERT mean formula: (low + 4*medium + high) / 6
    low, medium, high = 10, 50, 100
    expected_mean = (low + 4*medium + high) / 6  # Should be about 51.67

    samples = calc._pert_distribution(low, medium, high, 100000)
    actual_mean = np.mean(samples)

    # Allow 1% tolerance
    if abs(actual_mean - expected_mean) / expected_mean < 0.01:
        results.record_pass("PERT distribution mean correctness")
    else:
        results.record_fail("PERT distribution mean correctness",
                           f"Expected {expected_mean:.2f}, got {actual_mean:.2f}")


def test_pert_distribution_bounds():
    """Test that PERT samples stay within bounds"""
    calc = FAIRRiskCalculator(iterations=10000, random_seed=42)

    low, medium, high = 100, 500, 1000
    samples = calc._pert_distribution(low, medium, high, 10000)

    min_sample = np.min(samples)
    max_sample = np.max(samples)

    if min_sample >= low and max_sample <= high:
        results.record_pass("PERT distribution bounds check")
    else:
        results.record_fail("PERT distribution bounds check",
                           f"Samples outside [{low}, {high}]: [{min_sample:.2f}, {max_sample:.2f}]")


def test_pert_validation():
    """Test PERT distribution input validation"""
    calc = FAIRRiskCalculator(random_seed=42)

    # Test invalid: medium > high
    try:
        calc._pert_distribution(10, 100, 50, 1000)
        results.record_fail("PERT validation (medium > high)",
                           "Should have raised ValueError")
    except ValueError:
        results.record_pass("PERT validation (medium > high)")

    # Test invalid: medium < low
    try:
        calc._pert_distribution(100, 50, 200, 1000)
        results.record_fail("PERT validation (medium < low)",
                           "Should have raised ValueError")
    except ValueError:
        results.record_pass("PERT validation (medium < low)")


def test_triangular_distribution():
    """Test triangular distribution"""
    calc = FAIRRiskCalculator(iterations=100000, random_seed=42)

    low, medium, high = 10, 50, 100
    samples = calc._triangular_distribution(low, medium, high, 100000)

    # Triangular mean formula: (low + medium + high) / 3
    expected_mean = (low + medium + high) / 3  # Should be 53.33
    actual_mean = np.mean(samples)

    # Check bounds
    min_sample = np.min(samples)
    max_sample = np.max(samples)

    bounds_ok = (min_sample >= low and max_sample <= high)
    mean_ok = abs(actual_mean - expected_mean) / expected_mean < 0.01

    if bounds_ok and mean_ok:
        results.record_pass("Triangular distribution correctness")
    else:
        reasons = []
        if not bounds_ok:
            reasons.append(f"Bounds violated: [{min_sample:.2f}, {max_sample:.2f}] not in [{low}, {high}]")
        if not mean_ok:
            reasons.append(f"Mean incorrect: expected {expected_mean:.2f}, got {actual_mean:.2f}")
        results.record_fail("Triangular distribution correctness", "; ".join(reasons))


def test_fair_model_calculation():
    """Test FAIR model: ALE = TEF × V × LM"""
    calc = FAIRRiskCalculator(iterations=10000, random_seed=42)

    # Use deterministic values for precise testing
    calc.add_scenario(
        scenario_id="TEST_FAIR",
        description="FAIR Model Test",
        tef_low=2, tef_medium=2, tef_high=2,  # Constant TEF = 2
        vuln_low=0.5, vuln_medium=0.5, vuln_high=0.5,  # Constant V = 0.5
        loss_low=1000, loss_medium=1000, loss_high=1000  # Constant LM = 1000
    )

    # Expected: ALE = 2 × 0.5 × 1000 = 1000
    result = calc.run_simulation("TEST_FAIR")
    actual_mean = result['statistics']['mean_loss']

    expected = 2 * 0.5 * 1000  # = 1000

    if abs(actual_mean - expected) < 1:  # Allow small numerical error
        results.record_pass("FAIR model calculation (ALE = TEF × V × LM)")
    else:
        results.record_fail("FAIR model calculation",
                           f"Expected {expected}, got {actual_mean:.2f}")


def test_statistical_metrics():
    """Test statistical calculations"""
    calc = FAIRRiskCalculator(iterations=10000, random_seed=42)

    calc.add_scenario(
        scenario_id="TEST_STATS",
        description="Statistics Test",
        tef_low=1, tef_medium=5, tef_high=10,
        vuln_low=0.1, vuln_medium=0.3, vuln_high=0.6,
        loss_low=100000, loss_medium=500000, loss_high=2000000
    )

    result = calc.run_simulation("TEST_STATS")
    stats = result['statistics']

    checks = []

    # 1. Median should be close to 50th percentile
    if abs(stats['median_loss'] - stats['percentile_50']) < 0.01:
        checks.append(("Median = P50", True, ""))
    else:
        checks.append(("Median = P50", False,
                      f"Median {stats['median_loss']:.0f} ≠ P50 {stats['percentile_50']:.0f}"))

    # 2. Percentiles should be ordered
    percentiles = [
        stats['percentile_10'], stats['percentile_25'], stats['percentile_50'],
        stats['percentile_75'], stats['percentile_90'], stats['percentile_95'],
        stats['percentile_99']
    ]
    ordered = all(percentiles[i] <= percentiles[i+1] for i in range(len(percentiles)-1))
    if ordered:
        checks.append(("Percentiles ordered", True, ""))
    else:
        checks.append(("Percentiles ordered", False, "Percentiles not in ascending order"))

    # 3. VaR95 should equal percentile_95
    if abs(stats['var_95'] - stats['percentile_95']) < 0.01:
        checks.append(("VaR95 = P95", True, ""))
    else:
        checks.append(("VaR95 = P95", False,
                      f"VaR95 {stats['var_95']:.0f} ≠ P95 {stats['percentile_95']:.0f}"))

    # 4. CVaR95 should be >= VaR95 (tail loss is higher)
    if stats['cvar_95'] >= stats['var_95']:
        checks.append(("CVaR95 >= VaR95", True, ""))
    else:
        checks.append(("CVaR95 >= VaR95", False,
                      f"CVaR95 {stats['cvar_95']:.0f} < VaR95 {stats['var_95']:.0f}"))

    # 5. Std dev should be positive
    if stats['std_loss'] > 0:
        checks.append(("Std dev > 0", True, ""))
    else:
        checks.append(("Std dev > 0", False, f"Std dev = {stats['std_loss']}"))

    # 6. Mean should be between min and max
    if stats['min_loss'] <= stats['mean_loss'] <= stats['max_loss']:
        checks.append(("Min <= Mean <= Max", True, ""))
    else:
        checks.append(("Min <= Mean <= Max", False,
                      f"Mean {stats['mean_loss']:.0f} not in [{stats['min_loss']:.0f}, {stats['max_loss']:.0f}]"))

    # Report results
    all_passed = all(check[1] for check in checks)
    if all_passed:
        results.record_pass("Statistical metrics correctness")
    else:
        failed_checks = [check[0] + ": " + check[2] for check in checks if not check[1]]
        results.record_fail("Statistical metrics correctness", "; ".join(failed_checks))


def test_input_validation():
    """Test comprehensive input validation"""
    calc = FAIRRiskCalculator()

    # Test 1: Invalid loss magnitude order
    try:
        calc.add_scenario(
            scenario_id="INVALID1",
            description="Invalid Loss",
            tef_low=1, tef_medium=2, tef_high=3,
            vuln_low=0.1, vuln_medium=0.3, vuln_high=0.5,
            loss_low=500000, loss_medium=200000, loss_high=1000000  # medium < low!
        )
        results.record_fail("Input validation (loss order)", "Should have raised ValueError")
    except ValueError as e:
        if "Loss Magnitude" in str(e):
            results.record_pass("Input validation (loss order)")
        else:
            results.record_fail("Input validation (loss order)", f"Wrong error message: {e}")

    # Test 2: Vulnerability out of range
    try:
        calc.add_scenario(
            scenario_id="INVALID2",
            description="Invalid Vuln",
            tef_low=1, tef_medium=2, tef_high=3,
            vuln_low=0.1, vuln_medium=0.5, vuln_high=1.5,  # high > 1!
            loss_low=100000, loss_medium=500000, loss_high=1000000
        )
        results.record_fail("Input validation (vuln range)", "Should have raised ValueError")
    except ValueError as e:
        if "between 0 and 1" in str(e):
            results.record_pass("Input validation (vuln range)")
        else:
            results.record_fail("Input validation (vuln range)", f"Wrong error message: {e}")


def test_random_seed_reproducibility():
    """Test that random seed produces reproducible results"""
    calc1 = FAIRRiskCalculator(iterations=10000, random_seed=123)
    calc1.add_scenario(
        scenario_id="SEED_TEST",
        description="Seed Test",
        tef_low=1, tef_medium=5, tef_high=10,
        vuln_low=0.2, vuln_medium=0.5, vuln_high=0.8,
        loss_low=100000, loss_medium=500000, loss_high=2000000
    )
    result1 = calc1.run_simulation("SEED_TEST")

    calc2 = FAIRRiskCalculator(iterations=10000, random_seed=123)
    calc2.add_scenario(
        scenario_id="SEED_TEST",
        description="Seed Test",
        tef_low=1, tef_medium=5, tef_high=10,
        vuln_low=0.2, vuln_medium=0.5, vuln_high=0.8,
        loss_low=100000, loss_medium=500000, loss_high=2000000
    )
    result2 = calc2.run_simulation("SEED_TEST")

    # Results should be identical
    if result1['statistics']['mean_loss'] == result2['statistics']['mean_loss']:
        results.record_pass("Random seed reproducibility")
    else:
        results.record_fail("Random seed reproducibility",
                           f"Results differ: {result1['statistics']['mean_loss']} vs {result2['statistics']['mean_loss']}")


def test_edge_case_zero_vulnerability():
    """Test edge case: zero vulnerability means zero loss"""
    calc = FAIRRiskCalculator(iterations=1000, random_seed=42)

    calc.add_scenario(
        scenario_id="ZERO_VULN",
        description="Zero Vulnerability Test",
        tef_low=10, tef_medium=20, tef_high=30,
        vuln_low=0, vuln_medium=0, vuln_high=0,  # Zero vulnerability
        loss_low=1000000, loss_medium=5000000, loss_high=10000000
    )

    result = calc.run_simulation("ZERO_VULN")

    # With zero vulnerability, all losses should be zero
    if result['statistics']['mean_loss'] == 0 and result['statistics']['max_loss'] == 0:
        results.record_pass("Edge case: zero vulnerability")
    else:
        results.record_fail("Edge case: zero vulnerability",
                           f"Expected zero losses, got mean={result['statistics']['mean_loss']}")


def test_edge_case_identical_values():
    """Test edge case: all values identical (degenerate distribution)"""
    calc = FAIRRiskCalculator(iterations=1000, random_seed=42)

    calc.add_scenario(
        scenario_id="IDENTICAL",
        description="Identical Values Test",
        tef_low=5, tef_medium=5, tef_high=5,  # All same
        vuln_low=0.5, vuln_medium=0.5, vuln_high=0.5,  # All same
        loss_low=1000000, loss_medium=1000000, loss_high=1000000  # All same
    )

    result = calc.run_simulation("IDENTICAL")

    # Expected: 5 × 0.5 × 1000000 = 2,500,000
    expected = 2500000
    mean = result['statistics']['mean_loss']
    std = result['statistics']['std_loss']

    # All values should be identical, so std dev should be 0
    if abs(mean - expected) < 1 and std == 0:
        results.record_pass("Edge case: identical values")
    else:
        results.record_fail("Edge case: identical values",
                           f"Expected mean={expected}, std=0; got mean={mean:.0f}, std={std:.2f}")


def test_distribution_type_validation():
    """Test that invalid distribution types are rejected"""
    calc = FAIRRiskCalculator()

    calc.add_scenario(
        scenario_id="DIST_TEST",
        description="Distribution Type Test",
        tef_low=1, tef_medium=2, tef_high=3,
        vuln_low=0.1, vuln_medium=0.3, vuln_high=0.5,
        loss_low=100000, loss_medium=500000, loss_high=1000000
    )

    # Test invalid distribution type
    try:
        calc.run_simulation("DIST_TEST", distribution='invalid_type')
        results.record_fail("Distribution type validation", "Should have raised ValueError")
    except ValueError as e:
        if "Invalid distribution type" in str(e):
            results.record_pass("Distribution type validation")
        else:
            results.record_fail("Distribution type validation", f"Wrong error: {e}")


def test_triangular_vs_pert():
    """Test that both triangular and pert distributions work"""
    calc = FAIRRiskCalculator(iterations=10000, random_seed=42)

    calc.add_scenario(
        scenario_id="DIST_COMPARE",
        description="Distribution Comparison",
        tef_low=1, tef_medium=5, tef_high=10,
        vuln_low=0.2, vuln_medium=0.5, vuln_high=0.8,
        loss_low=100000, loss_medium=500000, loss_high=2000000
    )

    result_pert = calc.run_simulation("DIST_COMPARE", distribution='pert')
    result_tri = calc.run_simulation("DIST_COMPARE", distribution='triangular')

    # Both should produce valid results
    pert_ok = result_pert['statistics']['mean_loss'] > 0
    tri_ok = result_tri['statistics']['mean_loss'] > 0

    # Results should be different but in same ballpark (within 3x)
    ratio = result_pert['statistics']['mean_loss'] / result_tri['statistics']['mean_loss']
    reasonable_diff = 0.33 < ratio < 3.0

    if pert_ok and tri_ok and reasonable_diff:
        results.record_pass("Triangular vs PERT comparison")
    else:
        reasons = []
        if not pert_ok:
            reasons.append("PERT failed")
        if not tri_ok:
            reasons.append("Triangular failed")
        if not reasonable_diff:
            reasons.append(f"Results too different (ratio={ratio:.2f})")
        results.record_fail("Triangular vs PERT comparison", "; ".join(reasons))


# Run all tests
if __name__ == "__main__":
    print("="*70)
    print("FAIR RISK CALCULATOR - MATHEMATICAL CORRECTNESS TEST SUITE")
    print("="*70)
    print()

    tests = [
        ("PERT Distribution Mean", test_pert_distribution_mean),
        ("PERT Distribution Bounds", test_pert_distribution_bounds),
        ("PERT Validation", test_pert_validation),
        ("Triangular Distribution", test_triangular_distribution),
        ("FAIR Model Calculation", test_fair_model_calculation),
        ("Statistical Metrics", test_statistical_metrics),
        ("Input Validation", test_input_validation),
        ("Random Seed Reproducibility", test_random_seed_reproducibility),
        ("Edge Case: Zero Vulnerability", test_edge_case_zero_vulnerability),
        ("Edge Case: Identical Values", test_edge_case_identical_values),
        ("Distribution Type Validation", test_distribution_type_validation),
        ("Triangular vs PERT", test_triangular_vs_pert),
    ]

    for i, (name, test_func) in enumerate(tests, 1):
        print(f"\n[Test {i}/{len(tests)}] {name}")
        print("-" * 70)
        try:
            test_func()
        except Exception as e:
            results.record_fail(name, f"Exception: {e}")
            import traceback
            traceback.print_exc()

    # Print summary
    success = results.summary()

    print("\n" + "="*70)
    if success:
        print("✅ ALL TESTS PASSED - Mathematical implementation is correct!")
        print("="*70)
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
        print("="*70)
        sys.exit(1)
