<div align="center">

# Crowdfunding Success Predictor

### Transparent machine-learning decision support for pre-launch campaigns

A Flask application that implements a trained logistic-regression model directly in Python and combines its estimated success probability with a structured 17-question campaign-readiness assessment.

`Python` · `Flask` · `Logistic regression` · `Transparent coefficients` · `HTML/CSS`

</div>

---

## Evidence snapshot

| Area | Current repository |
|---|---|
| Prediction model | Logistic regression |
| Runtime artefact | Explicit intercept, coefficients and training-time scaling values in `app.py` |
| Serialized model | None |
| User assessment | 17 questions, maximum score 170 |
| External persistence | None; temporary signed Flask session only |
| Original context | Sanitised release of a LIFTWOMEN Group campaign-support prototype |

A separate audited notebook experiment recorded approximately **88.57% accuracy**, **75.00% F1** and **88.46% ROC-AUC** on its held-out test split. The original training data and full experiment are not included here, so those figures are historical notebook evidence—not a benchmark that this repository can independently reproduce.

## Why the current public implementation changed

The earlier public release loaded a serialized scikit-learn model. The current version removes that runtime dependency and implements the learned logistic-regression parameters directly in [`app.py`](app.py).

This avoids:

- untrusted pickle execution risk;
- scikit-learn deserialisation compatibility problems;
- an opaque binary artefact in a portfolio demonstration;
- unnecessary pandas and scikit-learn runtime dependencies.

The prediction remains tied to the recorded training-time parameters; rewriting it explicitly does not retrain or improve the model.

## Application flow

```text
Campaign details
      ↓
Input validation
      ↓
Funding-goal and campaign-length scaling
      ↓
Date-derived launch-month and ending-fortnight terms
      ↓
Explicit logistic-regression calculation
      ↓
Prototype notice and consent
      ↓
17-question readiness assessment
      ↓
Combined planning snapshot
```

## Prediction inputs

| Input | Use |
|---|---|
| Funding goal | Standardised numerical feature |
| Campaign length | Derived from start and end dates, then standardised |
| Campaign video | Binary model feature |
| Stretch goals | Binary model feature |
| Start month | Selected encoded month coefficient |
| End fortnight | Selected encoded fortnight coefficient |

The code uses a numerically stable logistic function to convert the linear score to a probability.

## Readiness assessment

The readiness survey covers campaign definition, audience preparation, launch planning, delivery and risk. It produces a score out of 170 and one of four descriptive categories:

| Category | Score |
|---|---:|
| Newcomer | 17–33 |
| Visionary | 34–84 |
| Trailblazer | 85–135 |
| Crowdfunding Rockstar | 136–170 |

These are rule-based planning labels, not independently validated psychological or financial measures.

## Privacy and credentials

The public application:

- does not use Google Sheets;
- does not require Google Cloud credentials;
- does not upload responses to an external service;
- stores progress temporarily in a signed session cookie;
- ignores environment and credential files;
- contains no real campaign/customer records;
- contains no serialized model or scaler file.

A local session key can be configured through `FLASK_SECRET_KEY`.

## Local setup

```bash
git clone https://github.com/Lukeyone/crowdfunding-success-predictor.git
cd crowdfunding-success-predictor
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Repository structure

```text
crowdfunding-success-predictor/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── SECURITY.md
├── static/style.css
└── templates/
```

## Responsible interpretation

The predicted value is an estimate, not a guarantee or financial recommendation. Crowdfunding outcomes also depend on market conditions, audience trust, storytelling, fulfilment, platform dynamics and execution quality.

Known limitations include:

- small historical training data;
- incomplete independent reproducibility from this repository;
- no probability-calibration study included here;
- no evidence that performance transfers across platforms, industries or time periods;
- no automated test suite in the current public repository;
- no production monitoring or model-governance process.

## Relationship to Prediction-App

[`Prediction-App`](https://github.com/Lukeyone/Prediction-App) preserves the original scikit-learn model-serving pattern, including its 41-column schema, scaler and L1 logistic-regression artefact.

This repository is the safer portfolio-facing application: it exposes the learned scoring calculation and includes the wider readiness workflow without loading pickle files.

## Portfolio context

This project demonstrates:

- moving a notebook-trained model into a user-facing workflow;
- preserving training-time scaling and categorical terms;
- explicit logistic-regression inference;
- combining statistical output with structured qualitative assessment;
- sanitising a commercial prototype for public review;
- documenting evidence limits rather than overstating model performance.

## Author

**Lachlan McDonald**  
Applied AI & Machine Learning Engineer · Software Engineer

[Portfolio](https://lukeyone.github.io) · [LinkedIn](https://www.linkedin.com/in/lachlanmcdonaldtech) · [Email](mailto:lachlanmcdonald2000@gmail.com)
