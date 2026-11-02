"""Streamlit interface for the Bank Loan EMI and Amortization Calculator."""

from __future__ import annotations

import io
import csv
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from loan_calculator import (
    SCHEDULE_DISPLAY_MONTHS,
    calculate_loan_report,
)

st.set_page_config(
    page_title="Bank Loan EMI Calculator",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main {background-color: #f5f7fb;}
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    .hero {
        background: linear-gradient(115deg, #102a43, #176b87);
        padding: 1.6rem 1.8rem; border-radius: 16px; color: white;
        margin-bottom: 1rem;
    }
    .hero h1 {color: white; margin-bottom: .2rem;}
    .hero p {color: #e4f1f7; margin-bottom: 0;}
    div[data-testid="stMetric"] {
        background: white; padding: 15px; border-radius: 12px;
        border: 1px solid #e5eaf0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>🏦 Bank Loan EMI Calculator</h1>
      <p>Loan assessment • EMI planning • Amortization • Prepayment analysis</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Customer & loan details")
    st.caption("Enter the customer's information below.")
    loan_amount = st.number_input(
        "Loan amount (₹)", min_value=1_000.0, max_value=100_000_000.0,
        value=500_000.0, step=10_000.0, format="%.2f"
    )
    base_rate = st.number_input(
        "Base annual interest rate (%)", min_value=0.5, max_value=50.0,
        value=10.0, step=0.25, format="%.2f"
    )
    tenure_years = st.number_input(
        "Tenure (years)", min_value=0.1, max_value=50.0,
        value=5.0, step=0.5, format="%.1f"
    )
    monthly_income = st.number_input(
        "Monthly income (₹)", min_value=1_000.0, max_value=10_000_000.0,
        value=40_000.0, step=1_000.0, format="%.2f"
    )
    age = st.number_input("Applicant age", min_value=18, max_value=100, value=25, step=1)
    credit_score = st.number_input(
        "Credit score", min_value=300, max_value=900, value=780, step=1
    )
    extra_payment = st.number_input(
        "Extra payment in month 12 (₹)", min_value=0.0,
        max_value=100_000_000.0, value=25_000.0, step=5_000.0, format="%.2f"
    )
    calculate_button = st.button("Calculate loan", type="primary", use_container_width=True)
    st.caption("Educational model only. This is not a bank approval or lending offer.")

if "report" not in st.session_state:
    st.session_state.report = None

if calculate_button or st.session_state.report is None:
    try:
        st.session_state.report = calculate_loan_report(
            principal=float(loan_amount),
            base_rate_percent=float(base_rate),
            tenure_years=float(tenure_years),
            monthly_income=float(monthly_income),
            age=int(age),
            credit_score=int(credit_score),
            extra_payment=float(extra_payment),
        )
    except ValueError as error:
        st.error(str(error))
        st.session_state.report = None

report = st.session_state.report

if report:
    comparison = report["comparison"]
    eligibility = report["eligibility"]
    schedule = report["schedule"]

    st.subheader("Loan summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Monthly EMI", f"₹{report['emi']:,.2f}")
    c2.metric("Total interest", f"₹{comparison['emi_interest']:,.2f}")
    c3.metric("Total repayment", f"₹{comparison['total_payable']:,.2f}")
    c4.metric("Applied rate", f"{report['applied_rate_percent']:.2f}%")

    if eligibility["eligible"]:
        st.success(f"ELIGIBLE — {eligibility['reason']}")
    else:
        st.error(f"NOT ELIGIBLE — {eligibility['reason']}")

    st.caption(
        f"Credit-score discount: {report['discount_percent']:.2f} percentage points | "
        f"Installments: {report['months']} months | "
        f"EMI / income: {eligibility['emi_to_income_percent']:.2f}% | "
        f"Age at loan end: {eligibility['age_at_loan_end']:.2f}"
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Amortization", "Interest comparison", "Prepayment", "Methodology"]
    )

    with tab1:
        st.subheader("First six months of repayment")
        schedule_df = pd.DataFrame(schedule[:SCHEDULE_DISPLAY_MONTHS])
        display_df = schedule_df.rename(columns={
            "month": "Month",
            "opening_balance": "Opening balance (₹)",
            "payment": "Payment (₹)",
            "interest_part": "Interest part (₹)",
            "principal_part": "Principal part (₹)",
            "closing_balance": "Closing balance (₹)",
        })
        st.dataframe(
            display_df.style.format({
                "Opening balance (₹)": "₹{:,.2f}",
                "Payment (₹)": "₹{:,.2f}",
                "Interest part (₹)": "₹{:,.2f}",
                "Principal part (₹)": "₹{:,.2f}",
                "Closing balance (₹)": "₹{:,.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

        full_df = pd.DataFrame(schedule)
        chart_df = full_df.melt(
            id_vars=["month"],
            value_vars=["principal_part", "interest_part"],
            var_name="Component",
            value_name="Amount (₹)",
        )
        chart_df["Component"] = chart_df["Component"].map({
            "principal_part": "Principal",
            "interest_part": "Interest",
        })
        fig = px.area(
            chart_df, x="month", y="Amount (₹)", color="Component",
            title="Principal and interest components across the loan",
            labels={"month": "Installment month"},
        )
        st.plotly_chart(fig, use_container_width=True)

        csv_buffer = io.StringIO()
        full_df.to_csv(csv_buffer, index=False)
        st.download_button(
            "Download full amortization schedule (CSV)",
            data=csv_buffer.getvalue(),
            file_name="amortization_schedule.csv",
            mime="text/csv",
        )

    with tab2:
        st.subheader("Interest method comparison")
        comparison_df = pd.DataFrame({
            "Method": [
                "Reducing-balance EMI",
                "Simple interest",
                "Annual compound interest",
            ],
            "Interest (₹)": [
                comparison["emi_interest"],
                comparison["simple_interest"],
                comparison["compound_interest"],
            ],
        })
        st.dataframe(
            comparison_df.style.format({"Interest (₹)": "₹{:,.2f}"}),
            use_container_width=True,
            hide_index=True,
        )
        fig = px.bar(
            comparison_df, x="Method", y="Interest (₹)",
            title="Interest amount by calculation method",
            text_auto=".2s",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            "Simple interest and annual compound interest are comparison examples. "
            "They are not equivalent to the reducing-balance monthly EMI method."
        )

    with tab3:
        st.subheader("Month-12 prepayment impact")
        prepayment = report["prepayment"]
        if prepayment is None:
            st.info("A month-12 prepayment comparison requires a tenure longer than 12 months.")
        else:
            p1, p2, p3 = st.columns(3)
            p1.metric("Tenure saved", f"{prepayment['months_saved']} months")
            p2.metric("Interest saved", f"₹{prepayment['interest_saved']:,.2f}")
            p3.metric("Balance after extra payment", f"₹{prepayment['balance_after_extra']:,.2f}")
            st.write(
                f"Extra amount actually applied to principal: "
                f"₹{prepayment['actual_extra_payment']:,.2f}"
            )
            st.write(
                f"Original payoff duration: {prepayment['original_months']} months | "
                f"New payoff duration: {prepayment['new_months']} months"
            )
            st.caption(
                "Assumption: the extra amount is applied immediately after the regular "
                "month-12 installment, with the EMI unchanged and no fees or penalties."
            )

    with tab4:
        st.subheader("Calculation methodology")
        st.latex(
            r"EMI = \\frac{P \\times r \\times (1+r)^n}{(1+r)^n-1}"
        )
        st.write("Monthly rate = annual percentage rate ÷ 12 ÷ 100.")
        st.write("Number of installments = ceiling(tenure in years × 12).")
        st.write("Total interest = (EMI × number of installments) − principal.")
        st.write("Eligibility: EMI must be no more than 40% of monthly income.")
        st.write("Age at loan end must not exceed 65; minimum credit score is 650.")
        st.write("Credit score 750+ receives 1.00 percentage-point discount; 700–749 receives 0.50.")
        st.caption(
            "The credit-score bands and discounts are illustrative project assumptions, "
            "not universal lending rules."
        )

    # Downloadable customer summary.
    summary_lines = [
        "BANK LOAN EMI CALCULATOR — CUSTOMER REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"Loan amount: ₹{report['principal']:,.2f}",
        f"Base annual rate: {report['base_rate_percent']:.2f}%",
        f"Credit discount: {report['discount_percent']:.2f} percentage points",
        f"Applied annual rate: {report['applied_rate_percent']:.2f}%",
        f"Tenure: {report['tenure_years']:.2f} years ({report['months']} months)",
        f"Monthly EMI: ₹{report['emi']:,.2f}",
        f"Total repayment: ₹{comparison['total_payable']:,.2f}",
        f"Total EMI interest: ₹{comparison['emi_interest']:,.2f}",
        f"Eligibility: {'ELIGIBLE' if eligibility['eligible'] else 'NOT ELIGIBLE'}",
        f"Eligibility reason: {eligibility['reason']}",
        "",
        "Educational estimate only; not a sanction letter or lending offer.",
    ]
    st.download_button(
        "Download customer loan summary (TXT)",
        data="\n".join(summary_lines),
        file_name="customer_loan_summary.txt",
        mime="text/plain",
    )

st.divider()
st.caption(
    "Bank Loan EMI & Amortization Calculator | Python 3.10+ | "
    "Academic project — verify lender-specific rules before real-world use."
)
