import pytest
from bloggr.models import Post
from datetime import date
from bloggr.quotes import QUOTES


# Test to see if the index page works.
def test_index(client, create_user, auth):
    auth.login()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Latest Problems" in response.data


# Test to see if the homepage renders the rotating quotes.
def test_index_shows_quote(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"quote-item" in response.data
    assert QUOTES[0][0].encode() in response.data


# Test to see if the app sends the unauthenticated user to the login page.
@pytest.mark.parametrize(("path", "method"), (("/new", "GET"), 
                                              ("/add", "POST"), 
                                              ("/edit/2", "GET"), 
                                              ("/save/2", "POST"), 
                                              ("/delete/2", "GET")))
def test_login_required(client, path, method):
    if method == "GET":
        response = client.get(path)
    else:
        response = client.post(path)
    assert response.headers["Location"].startswith("/login")


# Test to see if only the author of a post can edit it.
def test_author_required(app, db, create_user, create_user2, auth, client):         # Tests that the author_id is required to determine who has permission to edit or delete a post. 
    with app.app_context():
        username, password, user, email, fs_uniquifier = create_user          # Creates User1.
        username2, password2, user2, email2, fs_uniquifier2 = create_user2          # Creates User2.

        post = Post(            # Creates a post from User1
                title = "User1 Blog Post", # type:ignore
                content = "This is actually his first blog post.", # type:ignore
                author_id = user.id, # type:ignore
                date = date.today() # type:ignore
            )
        db.session.add(post)
        db.session.commit()
        retrieved_post = Post.query.filter_by(id=1).first()
        retrieved_post.author_id = user2.id # type: ignore             # Changes the author_id of User1's post(User1's id) to User2's id.
        db.session.commit()

    auth.login()            # Logs in User1
    assert client.get("/edit/1").status_code == 403        # Asserts that if User1 tries to edit the post(whose author_id was reassigned User2's id), User1 will get 403 Forbidden.
    assert client.get("/delete/1").status_code == 403       # Asserts that if User1 tries to delete the post(whose author_id was reassigned User2's id), User1 will get 403 Forbidden.


# To see if the path exists.
@pytest.mark.parametrize(("path"), (("/edit/2"),            # Tests that a path must exist to be accessed.
                                    ("/delete/2")))
def test_exists_required(client, create_user, auth, path):          
    auth.login()
    response = client.get(path)
    assert response.status_code == 404          # Asserts that if the path does not exist, a 404 status code is returned.


# Test to see if adding post works.
def test_add_post(client, create_user, auth, app):
    auth.login()
    response = client.get("/new")
    assert response.status_code == 200

    client.post("/add", data={"post_title" : "The Post title",
                              "post_content" : "The Post content"})
    with app.app_context():
        count = Post.query.count()
        assert count == 1


# Test to see if editing post works.
def test_edit_post(client, create_user, auth, app, db):
    auth.login()
    client.post("/add", data={"post_title" : "The post title",
                              "post_content" : "The post content"})
    response = client.get("/edit/1")
    assert response.status_code == 200

    client.post("/save/1", data={"new_post_title" : "The new post title",
                                 "new_post_content" : "The new post content"})
    with app.app_context():
        edited_post = db.get_or_404(Post, 1)
        assert edited_post.title == "The new post title"


# Test to see if a new post is properly validated before it is added.
@pytest.mark.parametrize(("title", "content", "message"),(("", "", b"Title is required."),
                                                          ("Test post title", "", b"Content is required.")))
def test_add_post_validate(client, create_user, auth, title, content, message):
    auth.login()
    response = client.post("/add", data={"post_title" : title,
                                         "post_content" : content})
    assert message in response.data
    print(response)


# Test to see if a post is properly validated before it is edited.
@pytest.mark.parametrize(("new_title", "new_content", "message"),(("", "", b"Title is required."),
                                                          ("New test post title", "", b"Content is required.")))
def test_edit_post_validate(client, create_user, auth, new_title, new_content, message):
    auth.login()
    client.post("/add", data={"post_title" : "The post title",
                              "post_content" : "The post content"})
    response = client.post("/save/1", data={"new_post_title" : new_title,
                                            "new_post_content" : new_content})
    assert message in response.data
    print(response)


# Test to see if deleting post works.
def test_delete(client, create_user, auth, app):
    auth.login()
    print(auth.login().data)
    client.post("/add", data={"post_title" : "The post title",
                              "post_content" : "The post content"})
    with app.app_context():
        count = Post.query.count()
        assert count == 1
    
    client.get("/delete/1")
    with app.app_context():
        count = Post.query.count()
        assert count == 0


# Profile page tests
def test_profile_page(client, create_user, auth):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    response = client.get(f"/profile/{username}")
    assert response.status_code == 200
    assert username.encode() in response.data
    assert email.encode() in response.data


def test_profile_page_not_found(client, create_user, auth):
    auth.login()
    response = client.get("/profile/nonexistent_user")
    assert response.status_code == 404


def test_profile_edit_requires_auth(client):
    response = client.get("/profile/edit")
    assert response.headers["Location"].startswith("/login")


def test_profile_edit_page(client, create_user, auth):
    auth.login()
    response = client.get("/profile/edit")
    assert response.status_code == 200
    assert b"Edit Profile" in response.data


def test_profile_edit_saves_changes(client, create_user, auth, app):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    response = client.post("/profile/edit", data={"username": "new_username", "email": "new@example.com"},
                          follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        from bloggr.models import User
        updated_user = User.query.filter_by(username="new_username").first()
        assert updated_user is not None
        assert updated_user.email == "new@example.com"


def test_profile_edit_validates_required_fields(client, create_user, auth):
    auth.login()
    response = client.post("/profile/edit", data={"username": "", "email": "test@example.com"})
    assert b"Username is required" in response.data

    response = client.post("/profile/edit", data={"username": "testuser", "email": ""})
    assert b"Email is required" in response.data


# API tests
def test_get_user_api(client, create_user, auth, app):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    response = client.get(f"/api/user/{user.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == username
    assert "joined" in data
    assert "roles" in data
    assert "post_count" in data


def test_get_user_api_not_found(client, create_user, auth):
    auth.login()
    response = client.get("/api/user/99999")
    assert response.status_code == 404


# Draft/Publish tests
def test_add_post_creates_draft_by_default(client, create_user, auth, app):
    auth.login()
    client.post("/add", data={"post_title": "Draft Title", "post_content": "Draft content"})
    with app.app_context():
        post = Post.query.first()
        assert post.is_published is False


def test_add_post_with_publish(client, create_user, auth, app):
    auth.login()
    client.post("/add", data={"post_title": "Published Title", "post_content": "Published content", "publish_now": "on"})
    with app.app_context():
        post = Post.query.first()
        assert post.is_published is True


def test_drafts_not_shown_on_index(client, create_user, auth, app):
    auth.login()
    client.post("/add", data={"post_title": "Draft Post", "post_content": "Draft content"})
    response = client.get("/")
    assert b"Draft Post" not in response.data


def test_published_posts_shown_on_index(client, create_user, auth, app):
    auth.login()
    client.post("/add", data={"post_title": "Published Post", "post_content": "Published content", "publish_now": "on"})
    response = client.get("/")
    assert b"Published Post" in response.data


def test_drafts_not_shown_on_articles(client, create_user, auth, app):
    auth.login()
    client.post("/add", data={"post_title": "Draft Article", "post_content": "Draft content"})
    response = client.get("/articles")
    assert b"Draft Article" not in response.data


def test_drafts_shown_on_author_profile(client, create_user, auth, app):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    client.post("/add", data={"post_title": "My Draft", "post_content": "Draft content"})
    response = client.get(f"/profile/{username}")
    assert b"My Draft" in response.data
    assert b"Draft" in response.data


def test_unpublished_post_returns_404_to_non_author(client, create_user, create_user2, auth, app, db):
    username, password, user, email, fs_uniquifier = create_user
    username2, password2, user2, email2, fs_uniquifier2 = create_user2

    auth.login()
    client.post("/add", data={"post_title": "Draft Post", "post_content": "Draft content"})
    auth.logout()

    auth.login(username2, password2)
    response = client.get("/post/1")
    assert response.status_code == 404


def test_author_can_view_own_draft(client, create_user, auth, app):
    auth.login()
    client.post("/add", data={"post_title": "My Draft", "post_content": "Draft content"})
    response = client.get("/post/1")
    assert response.status_code == 200
    assert b"My Draft" in response.data


def test_edit_post_can_publish_draft(client, create_user, auth, app):
    auth.login()
    client.post("/add", data={"post_title": "Draft to Publish", "post_content": "Content"})
    with app.app_context():
        post = Post.query.first()
        assert post.is_published is False

    client.post("/save/1", data={"new_post_title": "Draft to Publish", "new_post_content": "Content", "publish_now": "on"})
    with app.app_context():
        post = Post.query.first()
        assert post.is_published is True


def test_edit_post_can_unpublish(client, create_user, auth, app):
    auth.login()
    client.post("/add", data={"post_title": "Published Post", "post_content": "Content", "publish_now": "on"})
    with app.app_context():
        post = Post.query.first()
        assert post.is_published is True

    client.post("/save/1", data={"new_post_title": "Published Post", "new_post_content": "Content"})
    with app.app_context():
        post = Post.query.first()
        assert post.is_published is False


def test_search_only_finds_published_posts(client, create_user, auth, app):
    auth.login()
    client.post("/add", data={"post_title": "Secret Draft", "post_content": "Draft content"})
    client.post("/add", data={"post_title": "Public Post", "post_content": "Published content", "publish_now": "on"})

    response = client.get("/search?q=content")
    assert b"Public Post" in response.data
    assert b"Secret Draft" not in response.data


# Message author tests
def test_profile_shows_message_button_for_visitor(client, create_user, create_user2, auth):
    username, password, user, email, fs_uniquifier = create_user
    username2, password2, user2, email2, fs_uniquifier2 = create_user2
    auth.login()
    response = client.get(f"/profile/{username2}")
    assert response.status_code == 200
    assert b">Message</button>" in response.data
    assert b'data-message-modal-open' in response.data


def test_profile_hides_message_button_for_owner(client, create_user, auth):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    response = client.get(f"/profile/{username}")
    assert response.status_code == 200
    assert b">Message</button>" not in response.data


def test_message_route_rejects_get(client, create_user, auth):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    response = client.get(f"/message/{username}")
    assert response.status_code == 405


def test_message_route_unknown_user_404(client, create_user, auth, monkeypatch):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    sent = []
    monkeypatch.setattr("bloggr.blog.email_service.send_email", lambda **kw: sent.append(kw))
    response = client.post("/message/nonexistent_user", data={
        "sender_name": "Jane Doe",
        "sender_email": "jane@example.com",
        "subject": "Hi",
        "message": "Hello",
    })
    assert response.status_code == 404
    assert sent == []


def test_message_sends_email_to_author(client, create_user, auth, monkeypatch):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    sent = []
    monkeypatch.setattr("bloggr.blog.email_service.send_email", lambda **kw: sent.append(kw))
    response = client.post(f"/message/{username}", data={
        "sender_name": "Jane Doe",
        "sender_email": "jane@example.com",
        "subject": "Question about your post",
        "message": "Loved your article!",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Your message has been sent." in response.data
    assert len(sent) == 1
    payload = sent[0]
    assert payload["to"] == [email]
    assert payload["reply_to"] == ["jane@example.com"]
    assert "Question about your post" in payload["subject"]
    assert "Jane Doe" in payload["html"]
    assert "Loved your article!" in payload["html"]


def test_message_requires_name(client, create_user, auth, monkeypatch):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    sent = []
    monkeypatch.setattr("bloggr.blog.email_service.send_email", lambda **kw: sent.append(kw))
    response = client.post(f"/message/{username}", data={
        "sender_name": "",
        "sender_email": "jane@example.com",
        "subject": "Hi",
        "message": "Hello",
    })
    assert response.status_code == 400
    assert b"Your name is required." in response.data
    assert sent == []


def test_message_requires_valid_email(client, create_user, auth, monkeypatch):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    sent = []
    monkeypatch.setattr("bloggr.blog.email_service.send_email", lambda **kw: sent.append(kw))
    response = client.post(f"/message/{username}", data={
        "sender_name": "Jane Doe",
        "sender_email": "not-an-email",
        "subject": "Hi",
        "message": "Hello",
    })
    assert response.status_code == 400
    assert b"Please enter a valid email address." in response.data
    assert sent == []


def test_message_requires_message(client, create_user, auth, monkeypatch):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    sent = []
    monkeypatch.setattr("bloggr.blog.email_service.send_email", lambda **kw: sent.append(kw))
    response = client.post(f"/message/{username}", data={
        "sender_name": "Jane Doe",
        "sender_email": "jane@example.com",
        "subject": "Hi",
        "message": "",
    })
    assert response.status_code == 400
    assert b"Message is required." in response.data
    assert sent == []


def test_message_honeypot_blocks_send(client, create_user, auth, monkeypatch):
    username, password, user, email, fs_uniquifier = create_user
    auth.login()
    sent = []
    monkeypatch.setattr("bloggr.blog.email_service.send_email", lambda **kw: sent.append(kw))
    response = client.post(f"/message/{username}", data={
        "sender_name": "Jane Doe",
        "sender_email": "jane@example.com",
        "subject": "Hi",
        "message": "Hello",
        "website": "spambot-value",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Your message has been sent." in response.data
    assert sent == []