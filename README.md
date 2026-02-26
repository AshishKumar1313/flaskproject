# 📝 FlaskBlog — A Full-Featured Blogging Platform

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-OAuth-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)

> A production-ready blogging web application built with **Flask**, featuring role-based access control, Google OAuth authentication, Markdown post editing, CAPTCHA protection, and a fully responsive UI.

---

## 📸 Screenshots

| Page | Description |
|------|-------------|
| 🏠 Home | Post feed with category filtering and pagination |
| 🔐 Login/Register | Tabbed auth page with Google Sign-In and reCAPTCHA |
| ✍️ Post Editor | Live Markdown editor with split-screen preview |
| 👤 Dashboard | User profile with comment history |
| 🛡️ Admin Panel | Full user and post management |

---

## ✨ Features

### 🔐 Authentication & Security
- Email/password registration and login with hashed passwords (Werkzeug)
- **Google OAuth** login via Firebase Authentication
- **Google reCAPTCHA v2** on Login and Register to prevent bots
- CSRF protection on all forms (Flask-WTF)
- Secure session management with Flask-Login

### 👥 Role-Based Access Control
| Role | Permissions |
|------|-------------|
| `user` | Browse posts, leave comments, manage own comments |
| `author` | All user permissions + create, edit, delete own posts |
| `admin` | Full access — manage all users, posts, and roles |

### 📝 Post Management
- Create and edit posts with a rich **Markdown editor**
- Live **split-screen preview** while writing
- Markdown toolbar (Bold, Italic, Headings, Code, Tables, Links, etc.)
- Category tagging and short excerpt support
- Draft / Published toggle
- Full Markdown rendering on the frontend

### 💬 Comments
- Authenticated users can comment on posts
- Comment owners and admins can delete comments
- Comment count shown on post cards

### 🛡️ Admin Panel
- View all users with roles and auth type (Email / Google)
- Change user roles inline with a dropdown
- Delete users (with self-deletion protection)
- View and manage all posts with status indicators

### 🎨 UI & Design
- Fully **responsive** design with Bootstrap 5
- Gradient navbar and hero section
- Flash messages with auto-dismiss
- Category sidebar with tag cloud
- Pagination on the home feed
- Custom 403 / 404 error pages

---

## 🗂️ Project Structure

```
flaskblog/
│
├── app.py                  # App factory, extensions, config
├── models.py               # SQLAlchemy models (User, Post, Comment)
├── routes.py               # All route handlers and logic
├── forms.py                # WTForms form classes with validation
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── .gitignore
│
└── templates/
    ├── base.html           # Master layout (navbar, flash, footer)
    ├── index.html          # Home page with post grid + sidebar
    ├── login.html          # Login / Register (tabbed) + Google OAuth
    ├── post_detail.html    # Full post with Markdown + comments
    ├── create_post.html    # Markdown editor with live preview
    ├── author_dashboard.html  # Author's post management table
    ├── user_dashboard.html    # User profile + comment history
    ├── admin.html          # Admin control panel
    └── error.html          # 403 / 404 error pages
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.1 |
| Database | SQLite (via Flask-SQLAlchemy) |
| Auth | Flask-Login, Firebase Google OAuth |
| Forms | Flask-WTF, WTForms |
| Security | CSRF Protection, reCAPTCHA v2, Werkzeug password hashing |
| Frontend | Bootstrap 5.3, Font Awesome 6, Marked.js |
| Markdown | Python-Markdown (server-side), Marked.js (live preview) |
| Environment | python-dotenv |

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip
- Git

### 1. Clone the repository
```bash
git clone https://github.com/AshishKumar1313/flaskproject.git
cd flaskproject
```

### 2. Create a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///blog.db
RECAPTCHA_SITE_KEY=your_recaptcha_site_key
RECAPTCHA_SECRET_KEY=your_recaptcha_secret_key
```

### 5. Run the application
```bash
python app.py
```

Open your browser and visit:
```
http://127.0.0.1:5000
```

---

## 🔑 Default Admin Account

On first run, a default admin account is automatically created:

| Field | Value |
|-------|-------|
| Email | `admin@blog.com` |
| Password | `admin123` |

> ⚠️ Change these credentials immediately after first login in a production environment.

---

## 🔒 Setting Up Google reCAPTCHA

1. Visit [https://www.google.com/recaptcha/admin](https://www.google.com/recaptcha/admin)
2. Register a new site → choose **reCAPTCHA v2 ("I'm not a robot")**
3. Add `localhost` and `127.0.0.1` as allowed domains
4. Copy the **Site Key** and **Secret Key** into your `.env` file

---

## 🔥 Setting Up Firebase Google OAuth

1. Go to [https://console.firebase.google.com](https://console.firebase.google.com)
2. Create a new project → enable **Authentication → Google provider**
3. Add your domain to the authorized domains list
4. Copy your Firebase config into `login.html`

---

## 🗃️ Database Models

```
User
├── id, username, email, password_hash
├── role (user / author / admin)
├── firebase_uid, profile_pic
└── created_at

Post
├── id, title, content, excerpt, category
├── is_published, created_at, updated_at
└── user_id (FK → User)

Comment
├── id, content, created_at
├── user_id (FK → User)
└── post_id (FK → Post)
```

---

## 🚀 Key Implementation Highlights

- **App Factory Pattern** — `create_app()` in `app.py` for clean, scalable initialization
- **Blueprint Architecture** — All routes organized under a single `main` Blueprint
- **Role Decorators** — Custom `@admin_required` and `@author_required` decorators
- **reCAPTCHA Verification** — Server-side token verification via Google's API
- **Markdown Pipeline** — Written in Markdown, stored as text, rendered server-side with `python-markdown` and previewed client-side with `Marked.js`
- **Cascade Deletes** — Deleting a user automatically removes their posts and comments

---

## 📦 Dependencies

```
Flask==3.1.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
Markdown==3.10.2
Werkzeug==3.1.6
python-dotenv==1.2.1
email-validator==2.2.0
requests==2.32.3
WTForms==3.2.1
SQLAlchemy==2.0.46
```

---

## 👨‍💻 Author

**Ashish Kumar**
- GitHub: [@AshishKumar1313](https://github.com/AshishKumar1313)

---

## 📄 License

This project is intended for educational purposes.

---

> *Built with Flask, Bootstrap, and a lot of ☕*