import datetime as dt
import math
import os
import secrets

from flask import Flask, redirect, render_template, request, session, url_for

# Standardisation values learned during model training.
FUNDING_GOAL_MEAN = 15639.8203125
FUNDING_GOAL_SCALE = 46138.406823998324
CAMPAIGN_LENGTH_MEAN = 48.953125
CAMPAIGN_LENGTH_SCALE = 24.911988634678988

# Trained logistic-regression parameters.
MODEL_INTERCEPT = -2.194436751841851
MODEL_COEFFICIENTS = {
    "funding_goal": -2.17623576968482,
    "campaign_length": 0.6572091546422656,
    "has_video": 0.9925049209134896,
    "has_stretch_goals": 0.021633895449800527,
}
START_MONTH_COEFFICIENTS = {
    3: 1.3414971090112575,
    8: 0.18505190784075107,
    11: -1.1801947115322244,
}
END_FORTNIGHT_COEFFICIENTS = {
    10: -0.616147376151242,
    16: 0.709521095194844,
    19: 1.3487429326772262,
    20: 0.3402559750271717,
}

READINESS_QUESTIONS = {
    6: "I can clearly explain the problem my campaign solves.",
    7: "I can clearly explain why my solution is different.",
    8: "I have validated demand with potential supporters.",
    9: "I understand who my target audience is.",
    10: "I have an engaged audience or community I can reach.",
    11: "I have a clear communication plan for launch.",
    12: "I have campaign visuals or creative assets ready.",
    13: "I have a compelling campaign video or video plan.",
    14: "I have defined realistic reward tiers.",
    15: "I understand production, delivery and fulfilment costs.",
    16: "I have a contingency plan for delays or cost changes.",
    17: "My funding goal is based on a detailed budget.",
    18: "My campaign timeline is realistic.",
    19: "My team has clear responsibilities.",
    20: "I have identified the major risks to delivery.",
    21: "I have a post-campaign fulfilment plan.",
    22: "I am ready to communicate consistently during the campaign.",
}

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower()
    == "true",
)


def error_response(message: str, status_code: int = 400):
    """Render a consistent user-facing error page."""
    return render_template("error.html", message=message), status_code


def logistic(value: float) -> float:
    """Return a numerically stable logistic probability."""
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1.0 + exp_value)


def predict_success_probability(
    funding_goal: str,
    has_video: str,
    has_stretch_goals: str,
    start_date_raw: str,
    end_date_raw: str,
) -> float:
    """Validate inputs and calculate the trained model probability."""
    try:
        goal = float(funding_goal)
    except (TypeError, ValueError) as exc:
        raise ValueError("Funding goal must be a valid number.") from exc

    if not math.isfinite(goal) or goal <= 0:
        raise ValueError("Funding goal must be greater than zero.")

    if has_video not in {"0", "1"} or has_stretch_goals not in {"0", "1"}:
        raise ValueError("Video and stretch-goal selections are required.")

    try:
        start_date = dt.datetime.strptime(start_date_raw, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end_date_raw, "%Y-%m-%d")
    except (TypeError, ValueError) as exc:
        raise ValueError("Enter valid campaign start and end dates.") from exc

    campaign_length = (end_date - start_date).days
    if campaign_length <= 0:
        raise ValueError("The campaign end date must be after the start date.")

    scaled_goal = (goal - FUNDING_GOAL_MEAN) / FUNDING_GOAL_SCALE
    scaled_length = (
        campaign_length - CAMPAIGN_LENGTH_MEAN
    ) / CAMPAIGN_LENGTH_SCALE
    end_fortnight = ((end_date.timetuple().tm_yday - 1) // 14) + 1

    linear_score = MODEL_INTERCEPT
    linear_score += MODEL_COEFFICIENTS["funding_goal"] * scaled_goal
    linear_score += MODEL_COEFFICIENTS["campaign_length"] * scaled_length
    linear_score += MODEL_COEFFICIENTS["has_video"] * int(has_video)
    linear_score += (
        MODEL_COEFFICIENTS["has_stretch_goals"]
        * int(has_stretch_goals)
    )
    linear_score += START_MONTH_COEFFICIENTS.get(start_date.month, 0.0)
    linear_score += END_FORTNIGHT_COEFFICIENTS.get(end_fortnight, 0.0)

    return logistic(linear_score)


def parse_readiness_answers(question_numbers: range) -> int:
    """Validate a group of 1-10 readiness answers and return its score."""
    score = 0
    for question_number in question_numbers:
        raw_value = request.form.get(f"q{question_number}", "")
        try:
            value = int(raw_value)
        except ValueError as exc:
            raise ValueError("Answer every readiness question.") from exc

        if not 1 <= value <= 10:
            raise ValueError("Readiness answers must be between 1 and 10.")

        session[f"q{question_number}"] = value
        score += value

    return score


def readiness_band(score: int) -> str:
    if score <= 33:
        return "Newcomer"
    if score <= 84:
        return "Visionary"
    if score <= 135:
        return "Trailblazer"
    return "Crowdfunding Rockstar"


@app.get("/")
def index():
    return render_template("predict.html")


@app.post("/predict")
def predict():
    session.clear()

    form_values = {
        "funding_goal": request.form.get("funding_goal", ""),
        "has_video": request.form.get("has_video", ""),
        "has_stretch_goals": request.form.get("has_stretch_goals", ""),
        "start_date_raw": request.form.get("start_date", ""),
        "end_date_raw": request.form.get("end_date", ""),
    }

    try:
        probability = predict_success_probability(**form_values)
    except ValueError as exc:
        return error_response(str(exc))
    except Exception:
        app.logger.exception("Prediction failed")
        return error_response(
            "The prediction could not be completed. Please try again.",
            500,
        )

    session["predicted_probability"] = probability
    return redirect(url_for("consent"))


@app.get("/consent")
def consent():
    if "predicted_probability" not in session:
        return redirect(url_for("index"))
    return render_template("consent.html")


@app.post("/consent")
def consent_submit():
    if request.form.get("consent") != "yes":
        return error_response(
            "You must acknowledge the prototype notice to continue."
        )

    session["consent"] = True
    return redirect(url_for("survey_part", part=1))


@app.get("/survey/<int:part>")
def survey_part(part: int):
    if not session.get("consent"):
        return redirect(url_for("consent"))

    ranges = {
        1: range(6, 9),
        2: range(9, 17),
        3: range(17, 23),
    }
    question_numbers = ranges.get(part)
    if question_numbers is None:
        return redirect(url_for("survey_part", part=1))

    questions = [
        (number, READINESS_QUESTIONS[number]) for number in question_numbers
    ]
    return render_template(
        "survey.html",
        part=part,
        questions=questions,
        existing_answers=session,
    )


@app.post("/survey/<int:part>")
def survey_submit(part: int):
    if not session.get("consent"):
        return redirect(url_for("consent"))

    ranges = {
        1: range(6, 9),
        2: range(9, 17),
        3: range(17, 23),
    }
    question_numbers = ranges.get(part)
    if question_numbers is None:
        return redirect(url_for("survey_part", part=1))

    try:
        session[f"score_part_{part}"] = parse_readiness_answers(
            question_numbers
        )
    except ValueError as exc:
        return error_response(str(exc))

    if part < 3:
        return redirect(url_for("survey_part", part=part + 1))

    total_score = sum(
        int(session.get(f"score_part_{number}", 0))
        for number in range(1, 4)
    )
    session["readiness_score"] = total_score
    session["readiness_band"] = readiness_band(total_score)
    return redirect(url_for("result"))


@app.get("/result")
def result():
    required = {
        "predicted_probability",
        "readiness_score",
        "readiness_band",
    }
    if not required.issubset(session):
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        probability=session["predicted_probability"],
        score=session["readiness_score"],
        band=session["readiness_band"],
    )


@app.post("/restart")
def restart():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    debug_enabled = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_enabled, use_reloader=debug_enabled)
