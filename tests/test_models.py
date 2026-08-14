from bloggr.models import User, Post
from flask_security.utils import verify_password
from datetime import date


# Test if user is created. 
def test_create_user(app, create_user):          # Ensures a user can be created and added to the database.
    with app.app_context():         
        # Create a user and add to the database.
        username, password, user, email, fs_uniquifier = create_user

        # Retreive the user and create assertions on the details.
        existing_user = User.query.filter_by(username=username).first()
        assert existing_user is not None
        assert existing_user.id is not None
        assert verify_password("test_password", existing_user.password) == True 


# Test if post is created.
def test_create_post(app, db, create_user):         # Ensures a post can be created, added to a database and linked to a user.
    with app.app_context():
        # Create a user and add to the database.
        username, password, user, email, fs_uniquifier = create_user

        # Create a post and add to the database.
        post = Post(
            title = "My First Blog Post",           # type:ignore
            content = "Jokes aside, this just might actually be my first blog post.",          # type:ignore
            author_id = user.id,            # type:ignore
            date = date.today()         # type:ignore
        )
        db.session.add(post)
        db.session.commit()
        
        # Retrieve the post and make assertions on the post details.
        existing_post = Post.query.filter_by(title="My First Blog Post").first()
        assert existing_post is not None
        assert existing_post.id is not None
        assert existing_post.content == "Jokes aside, this just might actually be my first blog post."
        assert existing_post.author_id == user.id
        assert existing_post.date == date.today()


# Test if the author(editor role) of a post can be accessed from the post.  
def test_post_author_relationship(app, db, create_user):         # Ensures existing_post.author returns the User instance (backref works).
    with app.app_context():
        # Create a user and add to the database.
        username, password, user, email, fs_uniquifier = create_user

        # Create a post and add to the database.
        post = Post(
            title = "My Second Blog Post",           # type:ignore
            content = "Really, this is actually my second blog post.",          # type:ignore
            author_id = user.id,            # type:ignore
            date = date.today()         # type:ignore
        )
        db.session.add(post)
        db.session.commit()
        
        # Retrieve the post and make assertions on the post_author relationship.
        existing_post = Post.query.filter_by(title="My Second Blog Post").first()
        assert existing_post.author == user         # type: ignore
        assert existing_post.author.username == username            # type: ignore


# Test if the posts of an editor can be accessed through the editor.  
def test_editor_posts_relationship(app, db, create_user):         # Ensures existing_user.posts returns all posts authored by the user.
    with app.app_context():
        # Create a user and add to the database.
        username, password, user, email, fs_uniquifier = create_user

        # Create multiple posts and add to the database.
        post_one = Post(
            title = "My First Blog Post",           # type:ignore
            content = "Really, this is actually my first blog post.",          # type:ignore
            author_id = user.id,            # type:ignore
            date = date.today()         # type:ignore
        )
        post_two = Post(
            title = "My Second Blog Post",           # type:ignore
            content = "Really, this is actually my second blog post.",          # type:ignore
            author_id = user.id,            # type:ignore
            date = date.today()         # type:ignore
        )
        post_three = Post(
            title = "My Third Blog Post",           # type:ignore
            content = "Really, this is actually my third blog post.",          # type:ignore
            author_id = user.id,            # type:ignore
            date = date.today()         # type:ignore
        )
        db.session.add_all([post_one, post_two, post_three])
        db.session.commit()

        # Retrieve the user details and make assertions on the user_posts relationship.
        existing_user = User.query.filter_by(username=username).first()
        assert len(existing_user.posts) == 3            # type:ignore
        assert [each_post.title for each_post in existing_user.posts] == ["My First Blog Post",         # type:ignore           # Asserts that the titles of all the user's posts are what we defined.
                                                                 "My Second Blog Post",
                                                                 "My Third Blog Post"]


# Test if problem defaults are applied.
def test_post_problem_defaults(app, db, create_user):
    with app.app_context():
        username, password, user, email, fs_uniquifier = create_user
        post = Post(
            title="A Problem",
            content="Pain point content",
            author_id=user.id,
            date=date.today(),
        )
        db.session.add(post)
        db.session.commit()
        existing_post = Post.query.filter_by(title="A Problem").first()
        assert existing_post.industry == "Other"
        assert existing_post.country == "General"
        assert existing_post.status == "open"


# Test if a suggestion can be created and linked to a problem.
def test_suggestion_relationship(app, db, create_user):
    from bloggr.models import Suggestion
    with app.app_context():
        username, password, user, email, fs_uniquifier = create_user
        post = Post(
            title="A Problem",
            content="Pain point content",
            author_id=user.id,
            date=date.today(),
        )
        db.session.add(post)
        db.session.commit()
        suggestion = Suggestion(content="A proposed solution", problem_id=post.id, user_id=user.id)
        db.session.add(suggestion)
        db.session.commit()

        existing_post = Post.query.filter_by(title="A Problem").first()
        assert len(existing_post.suggestions) == 1
        assert existing_post.suggestions[0].content == "A proposed solution"
        assert existing_post.suggestions[0].user_id == user.id


# Test if a suggestion vote can be created and counted.
def test_suggestion_vote_counts(app, db, create_user, create_user2):
    from bloggr.models import Suggestion, SuggestionVote
    with app.app_context():
        username, password, user, email, fs_uniquifier = create_user
        username2, password2, user2, email2, fs_uniquifier2 = create_user2
        post = Post(
            title="A Problem",
            content="Pain point content",
            author_id=user.id,
            date=date.today(),
        )
        db.session.add(post)
        db.session.commit()
        suggestion = Suggestion(content="A proposed solution", problem_id=post.id, user_id=user.id)
        db.session.add(suggestion)
        db.session.commit()
        db.session.add(SuggestionVote(suggestion_id=suggestion.id, user_id=user.id, is_good=True))
        db.session.add(SuggestionVote(suggestion_id=suggestion.id, user_id=user2.id, is_good=False))
        db.session.commit()

        existing_suggestion = Suggestion.query.first()
        assert existing_suggestion.good_count == 1
        assert existing_suggestion.not_good_count == 1

