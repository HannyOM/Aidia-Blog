from datetime import date
import html

from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, jsonify, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional
from flask_security.decorators import auth_required, roles_accepted
from flask_login import current_user

from . import db
from .models import Post
from .email_service import email_service


bp = Blueprint("blog", __name__)


class MessageForm(FlaskForm):
    sender_name = StringField("Your Name", validators=[DataRequired(message="Your name is required.")])
    sender_email = StringField(
        "Your Email",
        validators=[DataRequired(message="Your email is required."), Email(message="Please enter a valid email address.")],
    )
    subject = StringField("Subject", validators=[Optional(), Length(max=100, message="Subject is too long (max 100 characters).")])
    message = TextAreaField("Message", validators=[DataRequired(message="Message is required.")])
    website = StringField("Website")  # Honeypot to deter spam.


@bp.route("/")
def index():
    all_posts = Post.query.filter_by(is_published=True).all()
    return render_template("blog/index.html", all_posts=all_posts, user=current_user)


@bp.route("/post/<int:post_id>")
def post(post_id):
    post = db.get_or_404(Post, post_id)
    if not post.is_published and (not current_user.is_authenticated or post.author_id != current_user.id):
        abort(404)
    return render_template("blog/post.html", post=post, user=current_user)


@bp.route("/articles")
def articles():
    all_posts = Post.query.filter_by(is_published=True).all()
    return render_template("blog/articles.html", all_posts=all_posts, user=current_user)


@bp.route("/search")
def search():
    query = request.args.get("q", "")
    if query:
        all_posts = Post.query.filter(
            Post.is_published == True,
            (Post.title.ilike(f"%{query}%")) | (Post.content.ilike(f"%{query}%"))
        ).all()
    else:
        all_posts = []
    return render_template("blog/search.html", all_posts=all_posts, query=query, user=current_user)


@bp.route("/new", methods=["GET"])
@auth_required()
@roles_accepted("admin", "editor")
def new():
    return render_template("blog/new.html")


@bp.route("/add", methods=["GET", "POST"])
@auth_required()
def add():
    if request.method == "POST":
        title = request.form.get("post_title")
        content = request.form.get("post_content")
        publish_now = request.form.get("publish_now") == "on"
        error = None
        
        if not title:
            error = "Title is required."
        elif not content:
            error = "Content is required."
        
        if error is not None:
            flash(error)
            return render_template("blog/new.html")
        else:
            new_content = Post(
                title=title,
                content=content,
                author_id=current_user.id,
                date=date.today(),
                is_published=publish_now
            )
            db.session.add(new_content)
            db.session.commit()
            return redirect(url_for("blog.index"))
    return render_template("blog/new.html")


@bp.route("/edit/<int:post_id>", methods=["GET", "POST"])
@auth_required()
def edit(post_id):
    editing_post = db.get_or_404(Post, post_id)
    if editing_post.author_id != current_user.id:
        abort(403)
    return render_template("blog/edit.html", editing_post=editing_post)


@bp.route("/save/<int:post_id>", methods=["POST"])
@auth_required()
def save(post_id):
    editing_post = Post.query.filter_by(id=post_id).first()
    if editing_post.author_id != current_user.id:
        abort(403)
    if request.method == "POST":
        new_title = request.form.get("new_post_title")
        new_content = request.form.get("new_post_content")
        publish_now = request.form.get("publish_now") == "on"
        error = None

        if not new_title:
            error = "Title is required."
        elif not new_content:
            error = "Content is required."

        if error is not None:
            flash(error)
            return render_template("blog/edit.html", editing_post=editing_post)
        else:
            editing_post.title = new_title
            editing_post.content = new_content
            editing_post.is_published = publish_now
            db.session.commit()
    return redirect(url_for("blog.index"))


@bp.route("/delete/<int:post_id>", methods=["GET"])
@auth_required()
def delete(post_id):
    deleting_post = db.get_or_404(Post, post_id)
    if deleting_post.author_id != current_user.id:
        abort(403)
    else:    
        db.session.delete(deleting_post)
        db.session.commit()
    return redirect(url_for("blog.index"))


@bp.route("/profile/<username>")
def profile(username):
    context = _get_profile_context(username)
    context["message_form"] = MessageForm()
    return render_template("blog/profile.html", **context)


def _get_profile_context(username):
    from .models import User
    profile_user = User.query.filter_by(username=username).first_or_404()
    published_posts = Post.query.filter_by(author_id=profile_user.id, is_published=True).all()
    is_owner = current_user.is_authenticated and current_user.id == profile_user.id
    if is_owner:
        draft_posts = Post.query.filter_by(author_id=profile_user.id, is_published=False).all()
    else:
        draft_posts = []
    return {
        "profile_user": profile_user,
        "posts": published_posts,
        "drafts": draft_posts,
        "is_owner": is_owner,
    }


@bp.route("/message/<username>", methods=["POST"])
def message(username):
    from .models import User
    author = User.query.filter_by(username=username).first_or_404()
    form = MessageForm()

    if not form.validate_on_submit():
        context = _get_profile_context(username)
        return render_template(
            "blog/profile.html",
            message_form=form,
            show_message_modal=True,
            **context,
        ), 400

    # Honeypot filled -> silently accept without sending an email.
    if form.website.data:
        flash("Your message has been sent.", "success")
        return redirect(url_for("blog.profile", username=username))

    sender_name = form.sender_name.data.strip()
    sender_email = form.sender_email.data.strip()
    subject = form.subject.data.strip() or "New message"
    body = form.message.data.strip()

    html_body = (
        f"<p><strong>From:</strong> {html.escape(sender_name)} "
        f"&lt;<a href=\"mailto:{html.escape(sender_email)}\">{html.escape(sender_email)}</a>&gt;</p>"
        f"<p><strong>Subject:</strong> {html.escape(subject)}</p>"
        f"<hr><p>{html.escape(body).replace(chr(10), '<br>')}</p>"
        f"<p style=\"margin:16px 0 0;color:#8a8a8a;font-size:12px;\">"
        f"Tip: If this email isn't in your inbox, please check your spam folder.</p>"
    )
    text_body = (
        f"From: {sender_name} <{sender_email}>\nSubject: {subject}\n\n{body}\n\n"
        "Tip: If this email isn't in your inbox, please check your spam folder."
    )

    try:
        email_service.send_email(
            to=[author.email],
            subject=f"[AIDIA] {subject} from {sender_name}",
            html=html_body,
            text=text_body,
            reply_to=[sender_email],
        )
        flash("Your message has been sent.", "success")
    except Exception:
        current_app.logger.exception("Failed to send message to %s", author.email)
        flash("Your message could not be sent. Please try again later.", "error")

    return redirect(url_for("blog.profile", username=username))


@bp.route("/profile/edit", methods=["GET", "POST"])
@auth_required()
def edit_profile():
    if request.method == "POST":
        new_username = request.form.get("username")
        new_email = request.form.get("email")
        error = None

        if not new_username:
            error = "Username is required."
        elif not new_email:
            error = "Email is required."

        if error is not None:
            flash(error)
            return render_template("blog/edit_profile.html")

        current_user.username = new_username
        current_user.email = new_email
        db.session.commit()
        flash("Profile updated successfully.")
        return redirect(url_for("blog.profile", username=current_user.username))

    return render_template("blog/edit_profile.html")


@bp.route("/api/user/<int:user_id>")
def get_user(user_id):
    from .models import User
    user = db.get_or_404(User, user_id)
    post_count = Post.query.filter_by(author_id=user.id).count()
    return jsonify({
        "username": user.username,
        "joined": user.confirmed_at.strftime("%B %d, %Y") if user.confirmed_at else "Unknown",
        "roles": [role.name for role in user.roles],
        "post_count": post_count
    })
