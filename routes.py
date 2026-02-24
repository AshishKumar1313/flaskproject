from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from models import db, User, Post, Comment
from forms import RegisterForm, LoginForm, PostForm, CommentForm
from functools import wraps
import os

main = Blueprint('main', __name__)

# ── Role decorators ───────────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated

def author_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_author():
            abort(403)
        return f(*args, **kwargs)
    return decorated

# ── Public Routes ─────────────────────────────────────────────────────────────
@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    query = Post.query.filter_by(is_published=True)
    if category:
        query = query.filter_by(category=category)
    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=6)
    categories = db.session.query(Post.category).filter(
        Post.is_published==True, Post.category!=None).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    return render_template('index.html', posts=posts, categories=categories, selected_category=category)

@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if not post.is_published and (not current_user.is_authenticated or
        (current_user.id != post.user_id and not current_user.is_admin())):
        abort(404)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must be logged in to comment.', 'warning')
            return redirect(url_for('main.login'))
        comment = Comment(content=form.content.data, user_id=current_user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted!', 'success')
        return redirect(url_for('main.post_detail', post_id=post_id))
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
    return render_template('post_detail.html', post=post, form=form, comments=comments)

# ── Auth Routes ───────────────────────────────────────────────────────────────
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('login.html', form=form, mode='register')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password_hash and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form, mode='login')

@main.route('/google-login', methods=['POST'])
def google_login():
    id_token = request.form.get('id_token')
    email = request.form.get('email')
    name = request.form.get('name')
    photo = request.form.get('photo')
    uid = request.form.get('uid')
    if not all([id_token, email, uid]):
        flash('Google login failed.', 'danger')
        return redirect(url_for('main.login'))
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.firebase_uid = uid
            user.profile_pic = photo
        else:
            username = name.replace(' ', '_').lower() if name else email.split('@')[0]
            existing = User.query.filter_by(username=username).first()
            if existing:
                username = username + '_' + uid[:5]
            user = User(username=username, email=email, firebase_uid=uid, profile_pic=photo)
            db.session.add(user)
    db.session.commit()
    login_user(user)
    flash(f'Welcome, {user.username}!', 'success')
    return redirect(url_for('main.index'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

# ── Author Dashboard ──────────────────────────────────────────────────────────
@main.route('/author/dashboard')
@login_required
@author_required
def author_dashboard():
    form = FlaskForm()
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    return render_template('author_dashboard.html', posts=posts, form=form)

@main.route('/post/create', methods=['GET', 'POST'])
@login_required
@author_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            excerpt=form.excerpt.data,
            category=form.category.data,
            is_published=form.is_published.data,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created!', 'success')
        return redirect(url_for('main.author_dashboard'))
    return render_template('create_post.html', form=form, title='Create Post')

@main.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@author_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.category = form.category.data
        post.is_published = form.is_published.data
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('main.author_dashboard'))
    return render_template('create_post.html', form=form, title='Edit Post', post=post)

@main.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
@author_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('main.author_dashboard'))

# ── User Dashboard ────────────────────────────────────────────────────────────
@main.route('/dashboard')
@login_required
def user_dashboard():
    form = FlaskForm()
    comments = Comment.query.filter_by(user_id=current_user.id).order_by(Comment.created_at.desc()).all()
    return render_template('user_dashboard.html', comments=comments, form=form)

@main.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'info')
    return redirect(request.referrer or url_for('main.user_dashboard'))

# ── Admin Routes ──────────────────────────────────────────────────────────────
@main.route('/admin')
@login_required
@admin_required
def admin():
    form = FlaskForm()
    users = User.query.order_by(User.created_at.desc()).all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin.html', users=users, posts=posts, form=form)

@main.route('/admin/user/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def update_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role in ['user', 'author', 'admin']:
        user.role = new_role
        db.session.commit()
        flash(f'{user.username} is now {new_role}.', 'success')
    return redirect(url_for('main.admin'))

@main.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't delete yourself.", 'danger')
        return redirect(url_for('main.admin'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'info')
    return redirect(url_for('main.admin'))

# ── Error Handlers ────────────────────────────────────────────────────────────
@main.app_errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message="Access Forbidden"), 403

@main.app_errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message="Page Not Found"), 404