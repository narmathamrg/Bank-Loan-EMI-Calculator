# Bank Loan EMI and Amortization Calculator

A Streamlit-based academic banking calculator built with Python 3.10+. It estimates loan EMI, total interest, customer eligibility, repayment schedule, and the effect of a month-12 prepayment.

## Features

- EMI using the standard reducing-balance formula
- Safe input validation and type conversion
- Credit-score interest discounts using named constants
- Total repayment, total interest and interest percentage
- Simple-interest and annual-compound-interest comparison
- Nested eligibility conditions: age, credit score and EMI-to-income ratio
- First six months of the amortization schedule
- Full amortization CSV download
- Month-12 prepayment simulation, tenure saved and interest saved
- Customer summary download
- Automated tests using pytest

## Project structure

```text
Bank_Loan_EMI_Calculator/
├── app.py
├── loan_calculator.py
├── requirements.txt
├── README.md
├── tests/
│   └── test_calculator.py
├── presentation/
│   └── project_presentation.pptx
└── sample_data/
    └── excel_verification.csv
```

## Requirements

- Python 3.10 or later
- Internet connection for installing packages
- VS Code (recommended)

## Setup on macOS

Open Terminal in the project folder.

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the application

```bash
streamlit run app.py
```

Streamlit will show a local URL, usually `http://localhost:8501`. Open it in your browser.

## Run tests

```bash
pytest -v
```

## EMI formula

EMI = P × r × (1+r)^n / ((1+r)^n - 1)

- P = principal amount
- r = monthly decimal interest rate = annual percentage rate / 12 / 100
- n = number of monthly installments = ceiling(tenure years × 12)

For a zero-interest loan, EMI = principal / number of installments.

## Credit-score assumptions

These are example rules for an academic project and are not actual universal bank policies:

- Credit score 750 or above: 1.00 percentage-point discount
- Credit score 700–749: 0.50 percentage-point discount
- Below 700: no discount
- Minimum educational eligibility score: 650

The applied interest rate must remain positive.

## Eligibility assumptions

- Applicant must be at least 18 years old.
- Age at loan end must be at most 65.
- Credit score must be at least 650.
- EMI must not exceed 40% of monthly income.

This is an educational eligibility model, not a real bank underwriting or loan approval system.

## Interest comparison

The application compares:
1. Reducing-balance EMI interest
2. Simple interest over the entered tenure
3. Annual-compounding interest over the entered tenure

Simple and compound interest are illustrative comparisons, not equivalent to the reducing-balance EMI calculation.

## Prepayment assumptions

The extra payment is applied immediately after the regular installment in month 12. It reduces principal. The regular EMI remains unchanged. No prepayment fees, taxes or lender-specific restrictions are included.

## Sample output (illustrative input)

For principal ₹5,00,000, base annual rate 10%, tenure 5 years,
monthly income ₹40,000, age 25 and credit score 780:

- Applied rate after the example discount: 9.00%
- Monthly EMI: ₹10,379.18
- Total repayment: ₹6,22,750.66
- Total EMI interest: ₹1,22,750.66
- EMI-to-income ratio: 25.95%
- Eligibility result: Eligible
- First-month interest: ₹3,750.00
- First-month principal: ₹6,629.18

With an extra ₹25,000 applied after the month-12 regular payment,
the example simulation saves approximately 3 installments and
₹10,453.19 in interest. Actual values depend on the assumptions
and rounding conventions used by a lender.

## Excel PMT verification

In Excel:
- A2 = principal
- B2 = annual rate as a percentage, e.g. 9
- C2 = tenure in years

D2:
```excel
=ROUNDUP(C2*12,0)
```

E2:
```excel
=ABS(PMT(B2/1200,D2,A2))
```

Compare E2 with the Python EMI calculated using the same applied annual rate. The file `sample_data/excel_verification.csv` contains five test cases and the expected formula values. Small floating-point display differences may occur; compare to two decimal places.

## Syllabus mapping

| Syllabus concept | Implementation |
|---|---|
| Operators and expressions | EMI, interest and balance formulas |
| Precedence | Parentheses, exponentiation, multiplication and division |
| Math functions | `math.pow`, `math.ceil`, `math.isfinite` |
| Input/output | Streamlit widgets and downloadable output |
| Type conversion | `float()` and `int()` |
| Conditional statements | Credit discount and eligibility |
| Nested conditions | EMI affordability check |
| Loops | Input handling and amortization schedule |
| Functions | Modular calculation functions |

## PEP 8 and code quality

- Descriptive `snake_case` function and variable names
- Named constants in uppercase
- Docstrings for public functions
- Comments for longer expressions and formula order
- Separate calculation logic from interface code
- Automated tests

## Limitations

This is a classroom demonstration. Real lenders may use different interest-rate conventions, credit policies, fees, insurance, taxes, repayment dates, rounding rules and prepayment conditions. It does not connect to a bank or issue a loan sanction.
