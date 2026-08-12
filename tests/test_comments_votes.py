import pytest
from datetime import date

from bloggr.models import Post, Comment, Vote


def _create_published_post(client):
    return client.post(
        "/add",
        data={
            "post_title": "Published Post",
            "post_content": "Published content",
            "publish_now": "on",
        },
        follow_redirects=True,
    )


# Login required tests
@pytest.mark.parametrize(("path", "method"), (("/post/1/comment", "POST"), ("/post/1/vote", "POST")))
def test_comment_vote_login_required(client, path, method):
    if method == "GET":
        response = client.get(path)
    else:
        response = client.post(path)
    assert response.headers["Location"].startswith("/login")


# Comment tests
def test_add_comment(client, create_user, auth, app, db):
    auth.login()
    _create_published_post(client)
    response = client.post(
        "/post/1/comment",
        data={"content": "Great post!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Great post!" in response.data
    with app.app_context():
        comment = Comment.query.first()
        assert comment is not None
        assert comment.content == "Great post!"
        assert comment.post_id == 1
        assert comment.user_id == 1


def test_comment_requires_content(client, create_user, auth, app, db):
    auth.login()
    _create_published_post(client)
    response = client.post(
        "/post/1/comment",
        data={"content": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your comment is required." in response.data
    with app.app_context():
        assert Comment.query.count() == 0


def test_comments_shown_on_post_page(client, create_user, create_user2, auth, app, db):
    username, password, user, email, fs_uniquifier = create_user
    username2, password2, user2, email2, fs_uniquifier2 = create_user2
    auth.login()
    _create_published_post(client)
    client.post("/post/1/comment", data={"content": "Comment from user1"})
    auth.logout()
    auth.login(email2, password2)
    response = client.post(
        "/post/1/comment",
        data={"content": "Comment from user2"},
        follow_redirects=True,
    )
    assert b"Comment from user1" in response.data
    assert b"Comment from user2" in response.data
    with app.app_context():
        assert Comment.query.filter_by(post_id=1).count() == 2


def test_comment_on_draft_returns_404(client, create_user, auth, app, db):
    auth.login()
    client.post("/add", data={"post_title": "Draft", "post_content": "Draft content"})
    response = client.post("/post/1/comment", data={"content": "Hello"})
    assert response.status_code == 404


# Vote tests
def test_like_creates_vote(client, create_user, auth, app, db):
    auth.login()
    _create_published_post(client)
    client.post("/post/1/vote", data={"vote_type": "like"}, follow_redirects=True)
    with app.app_context():
        vote = Vote.query.first()
        assert vote is not None
        assert vote.is_like is True
        assert vote.post_id == 1
        assert vote.user_id == 1
        post = Post.query.first()
        assert post.like_count == 1
        assert post.dislike_count == 0


def test_like_toggles_off(client, create_user, auth, app, db):
    auth.login()
    _create_published_post(client)
    client.post("/post/1/vote", data={"vote_type": "like"})
    client.post("/post/1/vote", data={"vote_type": "like"})
    with app.app_context():
        assert Vote.query.count() == 0
        assert Post.query.first().like_count == 0


def test_vote_switches_from_like_to_dislike(client, create_user, auth, app, db):
    auth.login()
    _create_published_post(client)
    client.post("/post/1/vote", data={"vote_type": "like"})
    client.post("/post/1/vote", data={"vote_type": "dislike"})
    with app.app_context():
        assert Vote.query.count() == 1
        vote = Vote.query.first()
        assert vote.is_like is False
        post = Post.query.first()
        assert post.like_count == 0
        assert post.dislike_count == 1


def test_one_vote_per_user_per_post(client, create_user, auth, app, db):
    auth.login()
    _create_published_post(client)
    client.post("/post/1/vote", data={"vote_type": "like"})
    client.post("/post/1/vote", data={"vote_type": "dislike"})
    client.post("/post/1/vote", data={"vote_type": "dislike"})
    with app.app_context():
        assert Vote.query.count() <= 1


def test_vote_invalid_type_rejected(client, create_user, auth, app, db):
    auth.login()
    _create_published_post(client)
    response = client.post("/post/1/vote", data={"vote_type": "invalid"}, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert Vote.query.count() == 0


def test_vote_on_draft_returns_404(client, create_user, auth, app, db):
    auth.login()
    client.post("/add", data={"post_title": "Draft", "post_content": "Draft content"})
    response = client.post("/post/1/vote", data={"vote_type": "like"})
    assert response.status_code == 404


def test_counts_displayed_on_post_page(client, create_user, auth, app, db):
    auth.login()
    _create_published_post(client)
    client.post("/post/1/vote", data={"vote_type": "like"})
    client.post("/post/1/comment", data={"content": "Nice!"})
    response = client.get("/post/1")
    assert response.status_code == 200
    assert b"Comments" in response.data
    with app.app_context():
        post = db.get_or_404(Post, 1)
        assert f"{post.like_count}".encode() in response.data


# Comment deletion tests
def test_commenter_can_delete_own_comment(client, create_user, auth, app, db):
    auth.login()
    _create_published_post(client)
    client.post("/post/1/comment", data={"content": "My comment"})
    with app.app_context():
        comment_id = Comment.query.first().id
    response = client.post(f"/comment/{comment_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert Comment.query.count() == 0


def test_post_author_can_delete_comment(client, create_user, create_user2, auth, app, db):
    username, password, user, email, fs_uniquifier = create_user
    username2, password2, user2, email2, fs_uniquifier2 = create_user2
    auth.login()
    _create_published_post(client)
    auth.logout()
    auth.login(email2, password2)
    client.post("/post/1/comment", data={"content": "Visitor comment"})
    with app.app_context():
        comment_id = Comment.query.first().id
    auth.logout()
    auth.login()
    response = client.post(f"/comment/{comment_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert Comment.query.count() == 0


def test_unauthorized_comment_delete_returns_403(client, create_user, create_user2, auth, app, db):
    username, password, user, email, fs_uniquifier = create_user
    username2, password2, user2, email2, fs_uniquifier2 = create_user2

    # Third user who is neither the post author nor the commenter.
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

    # Post is authored by user1.
    auth.login()
    _create_published_post(client)

    # user2 comments.
    auth.logout()
    auth.login(email2, password2)
    client.post("/post/1/comment", data={"content": "Comment by user2"})
    with app.app_context():
        comment = Comment.query.filter_by(user_id=user2.id).first()
        comment_id = comment.id

    # user1 (post author) may delete user2's comment -> 200.
    auth.logout()
    auth.login()
    assert client.post(f"/comment/{comment_id}/delete", follow_redirects=True).status_code == 200

    # user2 comments again.
    auth.logout()
    auth.login(email2, password2)
    client.post("/post/1/comment", data={"content": "Comment by user2 again"})
    with app.app_context():
        comment = Comment.query.filter_by(user_id=user2.id).first()
        comment_id = comment.id

    # user3 (neither author nor commenter) -> 403.
    auth.logout()
    auth.login("testmail3@gmail.com", "test_password3")
    assert client.post(f"/comment/{comment_id}/delete").status_code == 403


# Counts on list pages
def test_counts_displayed_on_index(client, create_user, auth, app, db):
    auth.login()
    _create_published_post(client)
    client.post("/post/1/vote", data={"vote_type": "like"})
    client.post("/post/1/comment", data={"content": "First!"})
    response = client.get("/")
    assert response.status_code == 200
    assert b"comments" in response.data


def test_counts_displayed_on_articles(client, create_user, auth, app, db):
    auth.login()
    _create_published_post(client)
    client.post("/post/1/vote", data={"vote_type": "dislike"})
    response = client.get("/articles")
    assert response.status_code == 200
    assert b"comments" in response.data