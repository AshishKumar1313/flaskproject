from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User
from routes import main
from dotenv import load_dotenv
import markdown
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    # ── Config ────────────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True

    # ── reCAPTCHA Config ──────────────────────────────────────────────────────
    app.config['RECAPTCHA_SITE_KEY']   = os.environ.get('RECAPTCHA_SITE_KEY', '')
    app.config['RECAPTCHA_SECRET_KEY'] = os.environ.get('RECAPTCHA_SECRET_KEY', '')

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)
    CSRFProtect(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Markdown filter ───────────────────────────────────────────────────────
    @app.template_filter('markdown')
    def render_markdown(text):
        return markdown.markdown(text, extensions=[
            'fenced_code',
            'tables',
            'nl2br',
            'sane_lists',
            'toc'
        ])

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(main)

    # ── Create DB tables ──────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    from werkzeug.security import generate_password_hash
    if User.query.count() == 0:
        admin = User(
            username='admin',
            email='admin@blog.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: admin@blog.com / admin123")


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)