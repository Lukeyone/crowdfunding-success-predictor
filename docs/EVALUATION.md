# Evaluation and Evidence Status

## Purpose

This document separates what the public repository can verify from historical
model results and from evaluation work that would still be required before any
production use.

The application is a decision-support prototype. Its probability output is not
a guarantee, financial recommendation or validated basis for approving or
rejecting a campaign.

## Evidence levels

| Level | Meaning | Current examples |
|---|---|---|
| Repository-verified | Reproducible from the code and automated tests in this repository | Input validation, feature scaling, coefficient-based inference, route access controls, readiness scoring, result rendering and restart behaviour |
| Historically recorded | Preserved from the original project records but not independently reproducible from this sanitised repository | The strongest recorded classifier reported 88.6% accuracy, 75.0% F1 and 88.5% ROC-AUC |
| Not yet evaluated | Requires the original dataset, a documented split and new analysis | Calibration, threshold performance, subgroup behaviour, temporal robustness, drift and external validation |

The public repository intentionally excludes the original training dataset,
serialized model, scaler files, customer records and service credentials.
Consequently, the historical classification metrics must not be represented as
reproduced or independently verified by this repository.

## What the automated tests verify

The test suite checks:

- numerical stability of the logistic function;
- a fixed reference prediction from the embedded coefficients and scaling
  constants;
- rejection of missing, non-numeric, non-finite and non-positive funding goals;
- rejection of invalid binary selections and campaign dates;
- readiness-band boundaries at every category transition;
- access-control redirects when required session state is missing;
- successful prediction and consent handling;
- all three readiness-assessment stages;
- missing and out-of-range readiness answers;
- the complete campaign-to-result workflow;
- generic handling of unexpected prediction failures; and
- session clearing when an assessment is restarted.

Coverage is measured with branch coverage and enforced at a minimum of 90% for
`app.py`.

## Reference inference case

The suite preserves one deterministic reference case to detect accidental
changes to scaling, date encoding or model coefficients.

| Input | Value |
|---|---:|
| Funding goal | 25,000 |
| Campaign video | Yes |
| Stretch goals | Yes |
| Start date | 1 March 2026 |
| End date | 15 April 2026 |
| Expected probability | 0.40502130149470816 |

This is a software-regression fixture, not evidence that the probability is
well calibrated for real campaigns.

## Model-evaluation work still required

A reproducible model evaluation should begin with a versioned data statement
covering source, collection period, target definition, inclusion rules,
missingness, duplicates, leakage risks and permitted use.

At minimum, a new evaluation should include:

1. **Split design** — preserve a final untouched test set and prefer temporal or
   grouped splitting when campaigns from the same creator, programme or period
   could leak across partitions.
2. **Discrimination** — report ROC-AUC and precision-recall AUC, with uncertainty
   intervals where feasible.
3. **Threshold behaviour** — publish confusion matrices, precision, recall,
   specificity and F1 at explicitly justified thresholds.
4. **Probability quality** — report log loss, Brier score, calibration plots and
   expected calibration error; recalibrate on validation data only when needed.
5. **Baselines** — compare against class prevalence, simple rules and at least
   one regularised baseline trained through a documented pipeline.
6. **Robustness** — test sensitivity to funding-goal scale, campaign duration,
   launch timing, missing features and plausible input extremes.
7. **Subgroup analysis** — examine performance across campaign categories,
   funding-goal bands, geography and other legitimate groups supported by the
   data, while avoiding unsupported fairness claims.
8. **Temporal and external validation** — test later campaigns and, where
   permitted, data from a separate source or programme.
9. **Reproducibility** — record dataset version, code revision, random seeds,
   dependency versions, preprocessing artefacts and model parameters.

## Readiness-score evaluation

The 17-question readiness score is a rule-based planning aid. The category
bands are not presented as a validated psychological, financial or causal
measurement instrument.

Before using the score beyond guided self-reflection, evaluation would need to
address:

- content review by crowdfunding and delivery specialists;
- comprehension and usability testing with intended users;
- internal-consistency analysis where conceptually appropriate;
- test-retest stability;
- relationships between readiness responses and later campaign outcomes;
- sensitivity to response bias and overconfidence; and
- whether the category boundaries have a defensible empirical basis.

## Known limitations

- Training data and the original training pipeline are not included.
- Embedded coefficients can reproduce inference but cannot prove training
  quality, provenance or calibration.
- The model uses a small set of structured features and omits many factors that
  influence crowdfunding outcomes.
- Start-month and end-fortnight coefficients are present only for categories
  selected by the original encoded model; unspecified categories use a zero
  coefficient.
- Readiness answers are self-reported and stored temporarily in a signed Flask
  session cookie.
- No production monitoring, drift detection or model-change governance is
  implemented.
- No claim of fairness, causal effect or financial suitability is supported.

## Running the verification suite

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
pytest --cov=app --cov-report=term-missing
```

GitHub Actions runs the same test and coverage checks on supported Python
versions for pull requests and pushes to `main`.
