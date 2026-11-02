"""Financial calculation engine for the Bank Loan EMI Calculator."""

from __future__ import annotations

import math
from typing import Any

# Named policy constants (educational assumptions, not actual bank policy).
MAX_EMI_TO_INCOME_RATIO = 0.40
MAX_AGE_AT_LOAN_END = 65
MINIMUM_APPLICANT_AGE = 18
MINIMUM_CREDIT_SCORE = 650
MINIMUM_CREDIT_SCORE_VALID = 300
MAXIMUM_CREDIT_SCORE_VALID = 900

HIGH_CREDIT_SCORE = 750
MEDIUM_CREDIT_SCORE = 700
HIGH_SCORE_DISCOUNT_PERCENT = 1.00
MEDIUM_SCORE_DISCOUNT_PERCENT = 0.50

MINIMUM_BASE_RATE_PERCENT = 0.50
MAXIMUM_BASE_RATE_PERCENT = 50.00
MAXIMUM_TENURE_YEARS = 50
PREPAYMENT_MONTH = 12
SCHEDULE_DISPLAY_MONTHS = 6


def validate_loan_inputs(
    principal: float,
    annual_rate_percent: float,
    tenure_years: float,
    monthly_income: float,
    age: int,
    credit_score: int,
) -> None:
    """Raise ValueError if any customer or loan input is outside allowed bounds."""
    numeric_values = (principal, annual_rate_percent, tenure_years, monthly_income)
    if not all(math.isfinite(value) for value in numeric_values):
        raise ValueError("All monetary, rate and tenure values must be finite.")
    if principal <= 0:
        raise ValueError("Loan amount must be greater than zero.")
    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than zero.")
    if not MINIMUM_BASE_RATE_PERCENT <= annual_rate_percent <= MAXIMUM_BASE_RATE_PERCENT:
        raise ValueError(
            f"Base annual rate must be between {MINIMUM_BASE_RATE_PERCENT}% "
            f"and {MAXIMUM_BASE_RATE_PERCENT}%."
        )
    if not 0 < tenure_years <= MAXIMUM_TENURE_YEARS:
        raise ValueError(f"Tenure must be greater than 0 and at most {MAXIMUM_TENURE_YEARS} years.")
    if not isinstance(age, int) or not MINIMUM_APPLICANT_AGE <= age <= 100:
        raise ValueError("Applicant age must be a whole number from 18 to 100.")
    if not isinstance(credit_score, int) or not (
        MINIMUM_CREDIT_SCORE_VALID <= credit_score <= MAXIMUM_CREDIT_SCORE_VALID
    ):
        raise ValueError("Credit score must be a whole number from 300 to 900.")


def get_discount_percent(credit_score: int) -> float:
    """Return the educational rate discount associated with the credit-score band."""
    if credit_score >= HIGH_CREDIT_SCORE:
        return HIGH_SCORE_DISCOUNT_PERCENT
    elif credit_score >= MEDIUM_CREDIT_SCORE:
        return MEDIUM_SCORE_DISCOUNT_PERCENT
    return 0.0


def calculate_emi(
    principal: float, annual_rate_percent: float, tenure_years: float
) -> dict[str, float | int]:
    """Calculate monthly EMI; fractional years are rounded up to whole months."""
    if principal <= 0 or annual_rate_percent < 0 or tenure_years <= 0:
        raise ValueError("Principal and tenure must be positive; rate cannot be negative.")

    # Convert annual percentage rate to a monthly decimal rate.
    monthly_rate = annual_rate_percent / (12 * 100)

    # math.ceil ensures any fractional month becomes one complete installment.
    number_of_months = math.ceil(tenure_years * 12)

    if monthly_rate == 0:
        emi = principal / number_of_months
    else:
        # Evaluation order: (1 + monthly rate), raise to n, form numerator,
        # then divide by ((1 + monthly rate)^n - 1).
        power_value = math.pow(1 + monthly_rate, number_of_months)
        emi = (
            principal * monthly_rate * power_value
            / (power_value - 1)
        )

    return {
        "emi": emi,
        "months": number_of_months,
        "monthly_rate": monthly_rate,
    }


def calculate_interest_comparison(
    principal: float,
    annual_rate_percent: float,
    tenure_years: float,
    emi: float,
    number_of_months: int,
) -> dict[str, float]:
    """Compare reducing-balance EMI interest with simple and annual compound interest."""
    total_payable = emi * number_of_months
    emi_interest = total_payable - principal

    # Simple interest: P * R * T / 100.
    simple_interest = principal * annual_rate_percent * tenure_years / 100

    # Annual compound interest: P * (1 + R/100)^T - P.
    compound_interest = (
        principal * math.pow(1 + annual_rate_percent / 100, tenure_years)
        - principal
    )

    interest_percentage = (emi_interest / principal) * 100

    return {
        "total_payable": total_payable,
        "emi_interest": emi_interest,
        "interest_percentage": interest_percentage,
        "simple_interest": simple_interest,
        "compound_interest": compound_interest,
    }


def build_amortization_schedule(
    principal: float,
    emi: float,
    monthly_rate: float,
    number_of_months: int,
) -> list[dict[str, float | int]]:
    """Build a full reducing-balance schedule, adjusting the final payment if needed."""
    balance = principal
    rows: list[dict[str, float | int]] = []

    for month in range(1, number_of_months + 1):
        opening_balance = balance
        interest_part = opening_balance * monthly_rate
        scheduled_payment = min(emi, opening_balance + interest_part)
        principal_part = min(scheduled_payment - interest_part, opening_balance)
        closing_balance = max(0.0, opening_balance - principal_part)

        rows.append({
            "month": month,
            "opening_balance": opening_balance,
            "payment": scheduled_payment,
            "interest_part": interest_part,
            "principal_part": principal_part,
            "closing_balance": closing_balance,
        })
        balance = closing_balance

        if balance <= 0.005:
            break

    return rows


def check_eligibility(
    emi: float,
    monthly_income: float,
    age: int,
    number_of_months: int,
    credit_score: int,
) -> dict[str, Any]:
    """Apply age, credit-score and EMI-to-income rules using nested conditions."""
    age_at_loan_end = age + (number_of_months / 12)
    permitted_emi = monthly_income * MAX_EMI_TO_INCOME_RATIO

    if age < MINIMUM_APPLICANT_AGE:
        eligible = False
        reason = "Applicant must be at least 18 years old."
    elif age_at_loan_end > MAX_AGE_AT_LOAN_END:
        eligible = False
        reason = "Age at loan completion exceeds 65."
    elif credit_score < MINIMUM_CREDIT_SCORE:
        eligible = False
        reason = "Credit score is below the minimum eligibility score."
    else:
        # Nested condition: affordability is checked after age and credit checks.
        if emi <= permitted_emi:
            eligible = True
            reason = "All educational eligibility checks are satisfied."
        else:
            eligible = False
            reason = "EMI exceeds 40% of monthly income."

    return {
        "eligible": eligible,
        "reason": reason,
        "permitted_emi": permitted_emi,
        "emi_to_income_percent": (emi / monthly_income) * 100,
        "age_at_loan_end": age_at_loan_end,
    }


def simulate_prepayment(
    principal: float,
    emi: float,
    monthly_rate: float,
    number_of_months: int,
    extra_payment: float,
    prepayment_month: int = PREPAYMENT_MONTH,
) -> dict[str, float | int]:
    """Compare payoff duration and interest with an extra principal payment in month 12."""
    if extra_payment < 0 or not math.isfinite(extra_payment):
        raise ValueError("Extra payment must be a finite, non-negative amount.")
    if prepayment_month < 1 or prepayment_month >= number_of_months:
        raise ValueError("Prepayment month must fall within the loan tenure.")

    original_rows = build_amortization_schedule(
        principal, emi, monthly_rate, number_of_months
    )
    original_interest = sum(float(row["interest_part"]) for row in original_rows)

    balance = principal
    prepayment_interest = 0.0
    prepayment_months_used = 0
    balance_after_extra = 0.0

    for month in range(1, number_of_months + 1):
        interest = balance * monthly_rate
        payment = min(emi, balance + interest)
        principal_paid = min(payment - interest, balance)
        balance = max(0.0, balance - principal_paid)
        prepayment_interest += interest
        prepayment_months_used += 1

        if month == prepayment_month:
            balance_after_extra = balance
            actual_extra = min(extra_payment, balance)
            balance = max(0.0, balance - actual_extra)

        if balance <= 0.005:
            break

    # Continue with unchanged EMI until the reduced balance is repaid.
    while balance > 0.005 and prepayment_months_used < number_of_months:
        interest = balance * monthly_rate
        payment = min(emi, balance + interest)
        principal_paid = min(payment - interest, balance)
        balance = max(0.0, balance - principal_paid)
        prepayment_interest += interest
        prepayment_months_used += 1

    saved_months = len(original_rows) - prepayment_months_used
    return {
        "balance_before_extra": balance_after_extra,
        "actual_extra_payment": min(extra_payment, balance_after_extra),
        "balance_after_extra": max(0.0, balance_after_extra - min(extra_payment, balance_after_extra)),
        "original_months": len(original_rows),
        "new_months": prepayment_months_used,
        "months_saved": max(0, saved_months),
        "original_interest": original_interest,
        "new_interest": prepayment_interest,
        "interest_saved": max(0.0, original_interest - prepayment_interest),
    }


def calculate_loan_report(
    principal: float,
    base_rate_percent: float,
    tenure_years: float,
    monthly_income: float,
    age: int,
    credit_score: int,
    extra_payment: float = 0.0,
) -> dict[str, Any]:
    """Validate inputs and return all calculations needed by the dashboard."""
    validate_loan_inputs(
        principal, base_rate_percent, tenure_years, monthly_income, age, credit_score
    )
    discount = get_discount_percent(credit_score)
    applied_rate = base_rate_percent - discount

    if applied_rate <= 0:
        raise ValueError("Discounted annual interest rate must remain positive.")

    emi_result = calculate_emi(principal, applied_rate, tenure_years)
    emi = float(emi_result["emi"])
    months = int(emi_result["months"])
    monthly_rate = float(emi_result["monthly_rate"])

    comparison = calculate_interest_comparison(
        principal, applied_rate, tenure_years, emi, months
    )
    schedule = build_amortization_schedule(principal, emi, monthly_rate, months)
    eligibility = check_eligibility(emi, monthly_income, age, months, credit_score)

    prepayment = None
    if months > PREPAYMENT_MONTH:
        prepayment = simulate_prepayment(
            principal, emi, monthly_rate, months, extra_payment
        )

    return {
        "principal": principal,
        "base_rate_percent": base_rate_percent,
        "discount_percent": discount,
        "applied_rate_percent": applied_rate,
        "tenure_years": tenure_years,
        "months": months,
        "emi": emi,
        "monthly_rate": monthly_rate,
        "comparison": comparison,
        "schedule": schedule,
        "eligibility": eligibility,
        "prepayment": prepayment,
        "extra_payment": extra_payment,
    }
