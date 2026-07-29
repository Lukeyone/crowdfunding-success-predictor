<div align="center">

# Crowdfunding Success Predictor

### Machine-learning decision support for crowdfunding campaigns

A Flask application that estimates crowdfunding success probability and
combines it with a structured campaign-readiness assessment.

[![CI](https://github.com/Lukeyone/crowdfunding-success-predictor/actions/workflows/ci.yml/badge.svg)](https://github.com/Lukeyone/crowdfunding-success-predictor/actions/workflows/ci.yml)

`Python` · `Flask` · `Logistic Regression` · `Pytest` · `GitHub Actions`

</div>

---

## Overview

The **Crowdfunding Success Predictor** helps founders assess a planned
crowdfunding campaign before launch.

Users enter a small set of campaign attributes, receive an estimated
probability of success, and then complete a 17-question readiness assessment
covering audience, planning, delivery and risk.

The final result combines:

- A model-generated success probability
- A readiness score out of 170
- A readiness category
- Contextual guidance on how to interpret the result

## Application Flow

```text
Campaign details
      ↓
Input validation and feature scaling
      ↓
Logistic-regression probability
      ↓
Prototype notice
      ↓
Three-part readiness assessment
      ↓
Combined campaign snapshot
```

## Prediction Inputs

| Feature | Description |
|---|---|
| Funding goal | Target funding amount |
| Campaign length | Days between the planned start and end dates |
| Campaign video | Whether the campaign includes a video |
| Stretch goals | Whether additional milestones are defined |
| Start month | Encoded launch month |
| End fortnight | Encoded closing fortnight |

The original classifier was trained as a scikit-learn logistic-regression
model. The clean public application implements the trained coefficients
directly in `app.py`, avoiding unsafe or version-sensitive pickle loading at
runtime.

## Readiness Categories

| Category | Score |
|---|---:|
| Newcomer | 17–33 |
| Visionary | 34–84 |
| Trailblazer | 85–135 |
| Crowdfunding Rockstar | 136–170 |

These categories are rule-based and should be treated as planning guidance,
not as independently validated psychological or financial measures.

## Testing and Continuous Integration

The automated suite covers:

- logistic-function stability and a fixed reference prediction;
- funding-goal, feature-selection and date validation;
- every readiness-category boundary;
- session-dependent route access and redirects;
- consent and all three survey stages;
- incomplete and out-of-range survey answers;
- the complete prediction-to-result workflow;
- unexpected inference failures; and
- assessment restart and session clearing.

Branch coverage for `app.py` is enforced at a minimum of 90%. GitHub Actions
runs the suite on Python 3.11 and 3.12 for pull requests, pushes to `main` and
manual workflow runs.

Run the same checks locally:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
pytest --cov=app --cov-branch --cov-report=term-missing
```

## Evaluation Status

The public repository can reproduce application behaviour and the embedded
coefficient-based inference calculation. It cannot independently reproduce the
original model training because the private training dataset, split artefacts
and serialized model are intentionally excluded.

The evaluation documentation distinguishes:

- behaviour verified by the repository and automated tests;
- historically recorded model results that are not independently reproducible
  from this sanitised release; and
- calibration, subgroup, robustness and external-validation work still needed
  before production use.

See **[Evaluation and Evidence Status](docs/EVALUATION.md)** for the full test
matrix, reference inference case, historical-evidence boundary, known
limitations and recommended model-evaluation protocol.

## Privacy and Credentials

This clean public version:

- Does not use Google Sheets
- Does not require Google Cloud credentials
- Does not upload form responses to an external service
- Stores progress temporarily in a signed Flask session cookie
- Ignores `.env`, credential JSON and private-key files
- Contains no serialized model or scaler files

Anyone adding an external service must create and configure their **own**
account and credentials. Never commit credentials to this repository.

## Project Structure

```text
crowdfunding-success-predictor/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── EVALUATION.md
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── consent.html
│   ├── error.html
│   ├── predict.html
│   ├── result.html
│   └── survey.html
├── tests/
│   └── test_app.py
├── app.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── SECURITY.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Lukeyone/crowdfunding-success-predictor.git
cd crowdfunding-success-predictor
```

### 2. Create a virtual environment

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS or Linux**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Application only:

```bash
python -m pip install -r requirements.txt
```

Application and test tools:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
```

### 4. Configure the Flask session key

Generate a local value:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Windows PowerShell**

```powershell
$env:FLASK_SECRET_KEY="paste-the-generated-value-here"
```

**macOS or Linux**

```bash
export FLASK_SECRET_KEY="paste-the-generated-value-here"
```

A temporary random secret is generated when this variable is omitted, but
sessions will reset each time the process restarts.

### 5. Run the application

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

## Responsible Use

The output is an estimate, not a guarantee or financial recommendation. Real
crowdfunding outcomes also depend on audience trust, storytelling, execution,
market conditions and fulfilment quality.

The historical model results are not independently reproducible from this
sanitised repository. Probability calibration, threshold selection, subgroup
performance and external validation remain open evaluation requirements.

## Planned Improvements

- Add probability-calibration analysis when an approved evaluation dataset is
  available
- Add prediction explanations that remain faithful to the linear model
- Add Docker and production deployment configuration
- Add structured logging and operational monitoring
- Add versioned model and preprocessing metadata

## Background

The original prototype was developed for **LIFTWOMEN Group** to support
founders preparing crowdfunding campaigns. This repository is a sanitised,
portfolio-safe release with no production customer data or shared service
credentials.

## Author

**Lachlan McDonald**  
Applied AI & Software Engineer

[LinkedIn](https://www.linkedin.com/in/lachlanmcdonaldtech) ·
[Portfolio](https://lukeyone.github.io/) ·
[Email](mailto:lachlanmcdonald2000@gmail.com)
