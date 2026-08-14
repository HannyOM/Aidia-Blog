import pytest
from datetime import date

from bloggr.models import Post, Suggestion, SuggestionVote


def _create_published_problem(client, **overrides):
    data = {
        "post_title": "Published Problem",
        "post_content": "Published content",
        "publish_now": "on",
        "industry": "Law",
        "country": "Nigeria",
    }
    data.update(overrides)
    return client.post("/add", data=data, follow_redirects=True)


# Posting permissions: any registered user may create a problem.
def test_any_registered_user_can_access_new(client, create_user, auth):
    auth.login()
    response = client.get("/new")
    assert response.status_code == 200
    assert b"Describe a Problem" in response.data


def test_add_problem_uses_defaults(client, create_user, auth, app):
    auth.login()
    client.post(
        "/add",
        data={"post_title": "Title", "post_content": "Content", "publish_now": "on"},
    )
    with app.app_context():
        post = Post.query.first()
        assert post.industry == "Other"
        assert post.country == "General"
        assert post.status == "open"


def test_add_problem_with_industry_and_country(client, create_user, auth, app):
    auth.login()
    _create_published_problem(client)
    with app.app_context():
        post = Post.query.first()
        assert post.industry == "Law"
        assert post.country == "Nigeria"


def test_add_problem_rejects_invalid_industry(client, create_user, auth, app):
    auth.login()
    client.post(
        "/add",
        data={
            "post_title": "Title",
            "post_content": "Content",
            "publish_now": "on",
            "industry": "NotARealIndustry",
            "country": "NotARealCountry",
        },
    )
    with app.app_context():
        post = Post.query.first()
        assert post.industry == "Other"
        assert post.country == "General"


def test_problem_badges_shown_on_post_page(client, create_user, auth):
    auth.login()
    _create_published_problem(client)
    response = client.get("/post/1")
    assert response.status_code == 200
    assert b"Law" in response.data
    assert b"Nigeria" in response.data
    assert b"Worth solving" in response.data


# Suggestion tests
def test_add_suggestion(client, create_user, auth, app):
    auth.login()
    _create_published_problem(client)
    response = client.post(
        "/post/1/suggest",
        data={"content": "Build a document automation tool."},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Build a document automation tool." in response.data
    with app.app_context():
        suggestion = Suggestion.query.first()
        assert suggestion is not None
        assert suggestion.content == "Build a document automation tool."
        assert suggestion.problem_id == 1
        assert suggestion.user_id == 1


def test_suggest_requires_content(client, create_user, auth, app):
    auth.login()
    _create_published_problem(client)
    response = client.post("/post/1/suggest", data={"content": ""}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Your solution is required." in response.data
    with app.app_context():
        assert Suggestion.query.count() == 0


def test_suggest_login_required(client):
    response = client.post("/post/1/suggest", data={"content": "A solution"})
    assert response.headers["Location"].startswith("/login")


def test_suggest_on_draft_returns_404(client, create_user, auth):
    auth.login()
    client.post("/add", data={"post_title": "Draft", "post_content": "Draft content"})
    response = client.post("/post/1/suggest", data={"content": "A solution"})
    assert response.status_code == 404


# Suggestion vote tests
def test_suggestion_vote_creates_vote(client, create_user, auth, app):
    auth.login()
    _create_published_problem(client)
    client.post("/post/1/suggest", data={"content": "A solution"})
    client.post("/suggestion/1/vote", data={"vote_value": "good"})
    with app.app_context():
        vote = SuggestionVote.query.first()
        assert vote is not None
        assert vote.is_good is True
        assert vote.suggestion_id == 1
        assert vote.user_id == 1
        suggestion = Suggestion.query.first()
        assert suggestion.good_count == 1
        assert suggestion.not_good_count == 0


def test_suggestion_vote_toggles_off(client, create_user, auth, app):
    auth.login()
    _create_published_problem(client)
    client.post("/post/1/suggest", data={"content": "A solution"})
    client.post("/suggestion/1/vote", data={"vote_value": "good"})
    client.post("/suggestion/1/vote", data={"vote_value": "good"})
    with app.app_context():
        assert SuggestionVote.query.count() == 0
        assert Suggestion.query.first().good_count == 0


def test_suggestion_vote_switches(client, create_user, auth, app):
    auth.login()
    _create_published_problem(client)
    client.post("/post/1/suggest", data={"content": "A solution"})
    client.post("/suggestion/1/vote", data={"vote_value": "good"})
    client.post("/suggestion/1/vote", data={"vote_value": "not_good"})
    with app.app_context():
        assert SuggestionVote.query.count() == 1
        vote = SuggestionVote.query.first()
        assert vote.is_good is False
        suggestion = Suggestion.query.first()
        assert suggestion.good_count == 0
        assert suggestion.not_good_count == 1


def test_suggestion_vote_invalid_value_rejected(client, create_user, auth, app):
    auth.login()
    _create_published_problem(client)
    client.post("/post/1/suggest", data={"content": "A solution"})
    client.post("/suggestion/1/vote", data={"vote_value": "invalid"})
    with app.app_context():
        assert SuggestionVote.query.count() == 0


def test_suggestion_vote_login_required(client):
    response = client.post("/suggestion/1/vote", data={"vote_value": "good"})
    assert response.headers["Location"].startswith("/login")


# Status update tests
def test_author_can_update_status(client, create_user, auth, app):
    auth.login()
    _create_published_problem(client)
    client.post("/post/1/status", data={"status": "in_progress"})
    with app.app_context():
        assert Post.query.first().status == "in_progress"


def test_author_can_update_status_to_solved(client, create_user, auth, app):
    auth.login()
    _create_published_problem(client)
    client.post("/post/1/status", data={"status": "solved"})
    with app.app_context():
        assert Post.query.first().status == "solved"


def test_status_update_invalid_rejected(client, create_user, auth, app):
    auth.login()
    _create_published_problem(client)
    client.post("/post/1/status", data={"status": "not_a_status"})
    with app.app_context():
        assert Post.query.first().status == "open"


def test_stranger_cannot_update_status(client, create_user, create_user2, auth, app):
    username, password, user, email, fs_uniquifier = create_user
    username2, password2, user2, email2, fs_uniquifier2 = create_user2
    auth.login()
    _create_published_problem(client)
    auth.logout()
    auth.login(email2, password2)
    response = client.post("/post/1/status", data={"status": "solved"})
    assert response.status_code == 403
    with app.app_context():
        assert Post.query.first().status == "open"


def test_status_update_login_required(client):
    response = client.post("/post/1/status", data={"status": "solved"})
    assert response.headers["Location"].startswith("/login")


# Suggestion deletion tests
def test_suggester_can_delete_own_suggestion(client, create_user, auth, app):
    auth.login()
    _create_published_problem(client)
    client.post("/post/1/suggest", data={"content": "My solution"})
    with app.app_context():
        suggestion_id = Suggestion.query.first().id
    response = client.post(f"/suggestion/{suggestion_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert Suggestion.query.count() == 0


def test_problem_author_can_delete_suggestion(client, create_user, create_user2, auth, app):
    username, password, user, email, fs_uniquifier = create_user
    username2, password2, user2, email2, fs_uniquifier2 = create_user2
    auth.login()
    _create_published_problem(client)
    auth.logout()
    auth.login(email2, password2)
    client.post("/post/1/suggest", data={"content": "Visitor solution"})
    with app.app_context():
        suggestion_id = Suggestion.query.first().id
    auth.logout()
    auth.login()
    response = client.post(f"/suggestion/{suggestion_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert Suggestion.query.count() == 0


def test_unauthorized_suggestion_delete_returns_403(client, create_user, create_user2, auth, app, db):
    username, password, user, email, fs_uniquifier = create_user
    username2, password2, user2, email2, fs_uniquifier2 = create_user2

    from datetime import datetime
    from flask_security.utils import hash_password
    from bloggr.models import User, Role
    role = Role.query.filter_by(name="editor").first()
    user3 = User(
        username="test_username3",
        password=hash_password("test_password3"),
        email="testmail3@gmail.com",
        fs_uniquifier="scbs7Feafb4E6bc7f2ae6de5e07b2d89",
        confirmed_at=datetime.utcnow(),
    )
    user3.roles.append(role)
    db.session.add(user3)
    db.session.commit()

    auth.login()
    _create_published_problem(client)

    auth.logout()
    auth.login(email2, password2)
    client.post("/post/1/suggest", data={"content": "Solution by user2"})
    with app.app_context():
        suggestion = Suggestion.query.filter_by(user_id=user2.id).first()
        suggestion_id = suggestion.id

    auth.logout()
    auth.login("testmail3@gmail.com", "test_password3")
    assert client.post(f"/suggestion/{suggestion_id}/delete").status_code == 403


def test_solution_counts_displayed_on_post_page(client, create_user, auth):
    auth.login()
    _create_published_problem(client)
    client.post("/post/1/suggest", data={"content": "A solution"})
    client.post("/suggestion/1/vote", data={"vote_value": "good"})
    response = client.get("/post/1")
    assert response.status_code == 200
    assert b"Solutions" in response.data
    assert b"Good" in response.data


def test_solution_count_displayed_on_index(client, create_user, auth):
    auth.login()
    _create_published_problem(client)
    client.post("/post/1/suggest", data={"content": "A solution"})
    response = client.get("/")
    assert response.status_code == 200
    assert b"solutions" in response.data


def test_search_finds_industry_and_country(client, create_user, auth):
    auth.login()
    _create_published_problem(client)
    response = client.get("/search?q=Law")
    assert b"Published Problem" in response.data
    response = client.get("/search?q=Nigeria")
    assert b"Published Problem" in response.data