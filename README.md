<div align="center">

# Crowdfunding Success Predictor

### Machine-learning decision support for crowdfunding campaigns

A Flask application that estimates crowdfunding success probability and
combines it with a structured campaign-readiness assessment.

`Python` · `Flask` · `scikit-learn` · `Pandas` · `HTML/CSS`

</div>

---

## Overview

The **Crowdfunding Success Predictor** helps founders assess a planned
crowdfunding campaign before launch.

Users enter a small set of campaign attributes, receive an estimated
probability of success, and then complete a 17-question readiness
assessment covering audience, planning, delivery and risk.

The final result combines:

- A model-generated success probability
- A readiness score out of 170
- A readiness category
- Contextual guidance on how to interpret the result

## Application Flow

```text
Campaign details
      ↓
Feature validation and engineering
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
| Start month | One-hot encoded launch month |
| End fortnight | One-hot encoded closing fortnight |

The model artefact is a scikit-learn logistic-regression classifier saved
with scikit-learn 1.6.1.

## Readiness Categories

| Category | Score |
|---|---:|
| Newcomer | 17–33 |
| Visionary | 34–84 |
| Trailblazer | 85–135 |
| Crowdfunding Rockstar | 136–170 |

These categories are rule-based and should be treated as planning guidance,
not as independently validated psychological or financial measures.

## Privacy and Credentials

This clean public version:

- Does not use Google Sheets
- Does not require Google Cloud credentials
- Does not upload form responses to an external service
- Stores progress temporarily in a signed Flask session cookie
- Ignores `.env`, credential JSON and private-key files

Anyone adding an external service must create and configure their **own**
account and credentials. Never commit credentials to this repository.

## Project Structure

```text
crowdfunding-success-predictor/
├── app.py
├── model.pkl
├── requirements.txt
├── .env.example
├── .gitignore
├── SECURITY.md
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── consent.html
    ├── error.html
    ├── predict.html
    ├── result.html
    └── survey.html
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

```bash
pip install -r requirements.txt
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

The output is an estimate, not a guarantee or financial recommendation.
Real crowdfunding outcomes also depend on audience trust, storytelling,
execution, market conditions and fulfilment quality.

The training data, model evaluation methodology and probability calibration
should be documented and independently reviewed before any production use.

## Planned Improvements

- Add automated unit and integration tests
- Document the training dataset and evaluation results
- Add probability-calibration analysis
- Add prediction explanations
- Add Docker and GitHub Actions
- Add structured logging and production deployment configuration

## Background

The original prototype was developed for **LIFTWOMEN Group** to support
founders preparing crowdfunding campaigns. This repository is a sanitised,
portfolio-safe release with no production customer data or shared service
credentials.

## Author

**Lachlan McDonald**  
Applied AI Engineer · Software Engineer · Data Scientist

[LinkedIn](https://www.linkedin.com/in/lachlanmcdonaldtech) ·
[Email](mailto:lachornot@gmail.com)
