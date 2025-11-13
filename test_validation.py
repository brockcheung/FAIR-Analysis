#!/usr/bin/env python3
"""
Test script for FAIR Risk Calculator input validation

This tests the validation logic in fair_risk_calculator.py.
The same validation is implemented in:
- fair_risk_calculator.py (command-line full calculator)
- fair_risk_app.py (Streamlit web application)
- quick_risk_analysis.py (quick command-line tool)

All three tools validate that Low ≤ Medium ≤ High for:
- Threat Event Frequency (TEF)
- Vulnerability (0-1 range)
- Loss Magnitude ($)
"""

from fair_risk_calculator import FAIRRiskCalculator

def test_valid_scenario():
    """Test that valid inputs are accepted"""
    print("Test 1: Valid scenario (should succeed)...")
    calc = FAIRRiskCalculator()
    try:
        calc.add_scenario(
            scenario_id="TEST1",
            description="Valid Test Scenario",
            tef_low=1.0,
            tef_medium=3.0,
            tef_high=6.0,
            vuln_low=0.2,
            vuln_medium=0.5,
            vuln_high=0.85,
            loss_low=500000,
            loss_medium=2080000,
            loss_high=3500000
        )
        print("✓ PASSED: Valid scenario accepted\n")
        return True
    except ValueError as e:
        print(f"✗ FAILED: {e}\n")
        return False


def test_invalid_loss_magnitude():
    """Test that invalid loss magnitude is rejected"""
    print("Test 2: Invalid Loss Magnitude (low > medium, should fail)...")
    calc = FAIRRiskCalculator()
    try:
        calc.add_scenario(
            scenario_id="TEST2",
            description="Invalid Loss Magnitude Test",
            tef_low=1.0,
            tef_medium=3.0,
            tef_high=6.0,
            vuln_low=0.2,
            vuln_medium=0.5,
            vuln_high=0.85,
            loss_low=500000,
            loss_medium=200000,  # Medium is lower than low - INVALID
            loss_high=3500000
        )
        print("✗ FAILED: Invalid scenario was accepted (should have been rejected)\n")
        return False
    except ValueError as e:
        print(f"✓ PASSED: Invalid scenario correctly rejected")
        print(f"   Error message: {str(e)}\n")
        return True


def test_invalid_tef():
    """Test that invalid TEF is rejected"""
    print("Test 3: Invalid TEF (medium > high, should fail)...")
    calc = FAIRRiskCalculator()
    try:
        calc.add_scenario(
            scenario_id="TEST3",
            description="Invalid TEF Test",
            tef_low=1.0,
            tef_medium=10.0,
            tef_high=5.0,  # High is lower than medium - INVALID
            vuln_low=0.2,
            vuln_medium=0.5,
            vuln_high=0.85,
            loss_low=500000,
            loss_medium=2080000,
            loss_high=3500000
        )
        print("✗ FAILED: Invalid scenario was accepted (should have been rejected)\n")
        return False
    except ValueError as e:
        print(f"✓ PASSED: Invalid scenario correctly rejected")
        print(f"   Error message: {str(e)}\n")
        return True


def test_invalid_vulnerability():
    """Test that invalid vulnerability is rejected"""
    print("Test 4: Invalid Vulnerability (low > high, should fail)...")
    calc = FAIRRiskCalculator()
    try:
        calc.add_scenario(
            scenario_id="TEST4",
            description="Invalid Vulnerability Test",
            tef_low=1.0,
            tef_medium=3.0,
            tef_high=6.0,
            vuln_low=0.9,
            vuln_medium=0.5,
            vuln_high=0.3,  # Values in descending order - INVALID
            loss_low=500000,
            loss_medium=2080000,
            loss_high=3500000
        )
        print("✗ FAILED: Invalid scenario was accepted (should have been rejected)\n")
        return False
    except ValueError as e:
        print(f"✓ PASSED: Invalid scenario correctly rejected")
        print(f"   Error message: {str(e)}\n")
        return True


def test_negative_values():
    """Test that negative values are rejected"""
    print("Test 5: Negative TEF values (should fail)...")
    calc = FAIRRiskCalculator()
    try:
        calc.add_scenario(
            scenario_id="TEST5",
            description="Negative Values Test",
            tef_low=-1.0,  # Negative - INVALID
            tef_medium=3.0,
            tef_high=6.0,
            vuln_low=0.2,
            vuln_medium=0.5,
            vuln_high=0.85,
            loss_low=500000,
            loss_medium=2080000,
            loss_high=3500000
        )
        print("✗ FAILED: Invalid scenario was accepted (should have been rejected)\n")
        return False
    except ValueError as e:
        print(f"✓ PASSED: Invalid scenario correctly rejected")
        print(f"   Error message: {str(e)}\n")
        return True


def test_vulnerability_out_of_range():
    """Test that vulnerability values outside 0-1 range are rejected"""
    print("Test 6: Vulnerability > 1 (should fail)...")
    calc = FAIRRiskCalculator()
    try:
        calc.add_scenario(
            scenario_id="TEST6",
            description="Vulnerability Out of Range Test",
            tef_low=1.0,
            tef_medium=3.0,
            tef_high=6.0,
            vuln_low=0.2,
            vuln_medium=0.5,
            vuln_high=1.5,  # Greater than 1 - INVALID
            loss_low=500000,
            loss_medium=2080000,
            loss_high=3500000
        )
        print("✗ FAILED: Invalid scenario was accepted (should have been rejected)\n")
        return False
    except ValueError as e:
        print(f"✓ PASSED: Invalid scenario correctly rejected")
        print(f"   Error message: {str(e)}\n")
        return True


def test_edge_case_equal_values():
    """Test that equal values (low = medium = high) are accepted"""
    print("Test 7: Equal values (low = medium = high, should succeed)...")
    calc = FAIRRiskCalculator()
    try:
        calc.add_scenario(
            scenario_id="TEST7",
            description="Edge Case - Equal Values",
            tef_low=5.0,
            tef_medium=5.0,
            tef_high=5.0,
            vuln_low=0.5,
            vuln_medium=0.5,
            vuln_high=0.5,
            loss_low=1000000,
            loss_medium=1000000,
            loss_high=1000000
        )
        print("✓ PASSED: Equal values accepted (valid edge case)\n")
        return True
    except ValueError as e:
        print(f"✗ FAILED: {e}\n")
        return False


if __name__ == "__main__":
    print("="*70)
    print("FAIR RISK CALCULATOR - INPUT VALIDATION TESTS")
    print("="*70)
    print()

    tests = [
        test_valid_scenario,
        test_invalid_loss_magnitude,
        test_invalid_tef,
        test_invalid_vulnerability,
        test_negative_values,
        test_vulnerability_out_of_range,
        test_edge_case_equal_values
    ]

    results = [test() for test in tests]

    print("="*70)
    print("SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed!")
    else:
        print(f"✗ {total - passed} test(s) failed")

    print()
