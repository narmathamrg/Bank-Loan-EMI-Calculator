import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from loan_calculator import (
    calculate_emi,
    calculate_loan_report,
    check_eligibility,
    get_discount_percent,
    simulate_prepayment,
)


@pytest.mark.parametrize(
    "principal, rate, years",
    [
        (500000, 9.0, 5),
        (1000000, 8.5, 10),
        (300000, 10.0, 3),
        (750000, 9.5, 7),
        (200000, 12.0, 2),
    ],
)
def test_emi_is_positive_and_month_count_is_correct(principal, rate, years):
    result = calculate_emi(principal, rate, years)
    assert result["emi"] > 0
    assert result["months"] == math.ceil(years * 12)


def test_credit_score_discounts():
    assert get_discount_percent(780) == 1.0
    assert get_discount_percent(720) == 0.5
    assert get_discount_percent(680) == 0.0


def test_zero_interest_rate():
    result = calculate_emi(120000, 0, 1)
    assert result["emi"] == pytest.approx(10000)


def test_eligibility_affordability():
    result = check_eligibility(10000, 40000, 25, 60, 780)
    assert result["eligible"] is True


def test_ineligible_affordability():
    result = check_eligibility(20000, 40000, 25, 60, 780)
    assert result["eligible"] is False


def test_invalid_loan_input_rejected():
    with pytest.raises(ValueError):
        calculate_loan_report(0, 10, 5, 40000, 25, 780)


def test_prepayment_does_not_increase_interest_or_tenure():
    result = calculate_emi(500000, 9, 5)
    prepay = simulate_prepayment(
        500000, result["emi"], result["monthly_rate"],
        result["months"], 25000
    )
    assert prepay["months_saved"] >= 0
    assert prepay["interest_saved"] >= 0
