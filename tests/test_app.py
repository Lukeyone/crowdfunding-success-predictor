import pytest

import app as app_module


VALID_PREDICTION = {
    "funding_goal": "25000",
    "has_video": "1",
    "has_stretch_goals": "1",
    "start_date": "2026-03-01",
    "end_date": "2026-04-15",
}


@pytest.fixture
def app():
    app_module.app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SESSION_COOKIE_SECURE=False,
    )
    yield app_module.app


@pytest.fixture
def client(app):
    return app.test_client()


def prediction_kwargs(**overrides):
    values = {
        "funding_goal": "25000",
        "has_video": "1",
        "has_stretch_goals": "1",
        "start_date_raw": "2026-03-01",
        "end_date_raw": "2026-04-15",
    }
    values.update(overrides)
    return values


def set_consent(client):
    with client.session_transaction() as session:
        session["consent"] = True


def complete_assessment(client, answer="10"):
    response = client.post("/predict", data=VALID_PREDICTION)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/consent")

    response = client.post("/consent", data={"consent": "yes"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/survey/1")

    response = client.post(
        "/survey/1",
        data={f"q{number}": answer for number in range(6, 9)},
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/survey/2")

    response = client.post(
        "/survey/2",
        data={f"q{number}": answer for number in range(9, 17)},
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/survey/3")

    response = client.post(
        "/survey/3",
        data={f"q{number}": answer for number in range(17, 23)},
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/result")



def test_logistic_is_stable_at_extreme_values():
    assert app_module.logistic(0) == pytest.approx(0.5)
    assert app_module.logistic(1000) == pytest.approx(1.0)
    assert app_module.logistic(-1000) == pytest.approx(0.0, abs=1e-12)


def test_predict_success_probability_matches_known_reference_case():
    probability = app_module.predict_success_probability(**prediction_kwargs())
    assert probability == pytest.approx(0.40502130149470816)


@pytest.mark.parametrize(
    ("goal", "message"),
    [
        (None, "Funding goal must be a valid number."),
        ("", "Funding goal must be a valid number."),
        ("not-a-number", "Funding goal must be a valid number."),
        ("0", "Funding goal must be greater than zero."),
        ("-1", "Funding goal must be greater than zero."),
        ("nan", "Funding goal must be greater than zero."),
        ("inf", "Funding goal must be greater than zero."),
    ],
)
def test_prediction_rejects_invalid_funding_goals(goal, message):
    with pytest.raises(ValueError, match=message):
        app_module.predict_success_probability(
            **prediction_kwargs(funding_goal=goal)
        )


@pytest.mark.parametrize(
    ("has_video", "has_stretch_goals"),
    [("yes", "1"), ("1", ""), ("2", "0")],
)
def test_prediction_requires_binary_feature_selections(
    has_video, has_stretch_goals
):
    with pytest.raises(
        ValueError,
        match="Video and stretch-goal selections are required.",
    ):
        app_module.predict_success_probability(
            **prediction_kwargs(
                has_video=has_video,
                has_stretch_goals=has_stretch_goals,
            )
        )


@pytest.mark.parametrize(
    ("start_date", "end_date", "message"),
    [
        (
            "01-03-2026",
            "2026-04-15",
            "Enter valid campaign start and end dates.",
        ),
        (
            "2026-03-01",
            "15/04/2026",
            "Enter valid campaign start and end dates.",
        ),
        (
            "2026-03-01",
            "2026-03-01",
            "The campaign end date must be after the start date.",
        ),
        (
            "2026-04-15",
            "2026-03-01",
            "The campaign end date must be after the start date.",
        ),
    ],
)
def test_prediction_rejects_invalid_campaign_dates(
    start_date, end_date, message
):
    with pytest.raises(ValueError, match=message):
        app_module.predict_success_probability(
            **prediction_kwargs(
                start_date_raw=start_date,
                end_date_raw=end_date,
            )
        )


def test_video_feature_increases_reference_probability():
    with_video = app_module.predict_success_probability(
        **prediction_kwargs(has_video="1")
    )
    without_video = app_module.predict_success_probability(
        **prediction_kwargs(has_video="0")
    )
    assert with_video > without_video


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (17, "Newcomer"),
        (33, "Newcomer"),
        (34, "Visionary"),
        (84, "Visionary"),
        (85, "Trailblazer"),
        (135, "Trailblazer"),
        (136, "Crowdfunding Rockstar"),
        (170, "Crowdfunding Rockstar"),
    ],
)
def test_readiness_band_boundaries(score, expected):
    assert app_module.readiness_band(score) == expected


def test_index_renders_prediction_form(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Evaluate your crowdfunding campaign before launch" in response.data


@pytest.mark.parametrize(
    ("path", "destination"),
    [
        ("/consent", "/"),
        ("/survey/1", "/consent"),
        ("/result", "/"),
    ],
)
def test_protected_pages_redirect_without_required_session_state(
    client, path, destination
):
    response = client.get(path)
    assert response.status_code == 302
    assert response.headers["Location"].endswith(destination)


def test_valid_prediction_is_saved_in_session(client):
    response = client.post("/predict", data=VALID_PREDICTION)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/consent")

    with client.session_transaction() as session:
        assert session["predicted_probability"] == pytest.approx(
            0.40502130149470816
        )

    consent_page = client.get("/consent")
    assert consent_page.status_code == 200
    assert b"Before you continue" in consent_page.data


def test_invalid_prediction_returns_user_facing_error(client):
    response = client.post(
        "/predict",
        data={**VALID_PREDICTION, "funding_goal": "0"},
    )
    assert response.status_code == 400
    assert b"Funding goal must be greater than zero." in response.data


def test_unexpected_prediction_failure_returns_generic_error(
    client, monkeypatch
):
    def fail_prediction(**_kwargs):
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(
        app_module,
        "predict_success_probability",
        fail_prediction,
    )

    response = client.post("/predict", data=VALID_PREDICTION)
    assert response.status_code == 500
    assert b"The prediction could not be completed" in response.data


def test_consent_must_be_acknowledged(client):
    response = client.post("/consent", data={})
    assert response.status_code == 400
    assert b"You must acknowledge the prototype notice" in response.data


def test_valid_survey_page_renders_questions(client):
    set_consent(client)
    response = client.get("/survey/1")
    assert response.status_code == 200
    assert b"Part 1 of 3" in response.data
    assert b"I can clearly explain the problem" in response.data


def test_complete_assessment_flow_produces_result(client):
    complete_assessment(client)

    response = client.get("/result")
    assert response.status_code == 200
    assert b"40.5%" in response.data
    assert b"170" in response.data
    assert b"Crowdfunding Rockstar" in response.data

    with client.session_transaction() as session:
        assert session["readiness_score"] == 170
        assert session["readiness_band"] == "Crowdfunding Rockstar"


def test_survey_rejects_missing_answers(client):
    set_consent(client)
    response = client.post(
        "/survey/1",
        data={"q6": "5", "q7": "5"},
    )
    assert response.status_code == 400
    assert b"Answer every readiness question." in response.data


def test_survey_rejects_out_of_range_answers(client):
    set_consent(client)
    response = client.post(
        "/survey/1",
        data={"q6": "5", "q7": "11", "q8": "5"},
    )
    assert response.status_code == 400
    assert b"Readiness answers must be between 1 and 10." in response.data


def test_invalid_survey_part_redirects_to_first_part(client):
    set_consent(client)

    get_response = client.get("/survey/99")
    assert get_response.status_code == 302
    assert get_response.headers["Location"].endswith("/survey/1")

    post_response = client.post("/survey/99", data={})
    assert post_response.status_code == 302
    assert post_response.headers["Location"].endswith("/survey/1")


def test_restart_clears_assessment_session(client):
    complete_assessment(client, answer="5")

    response = client.post("/restart")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with client.session_transaction() as session:
        assert dict(session) == {}
