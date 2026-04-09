# My Personal Website

A personal portfolio website built with Flask, featuring the blog-style layout inspired by shiquda and yuhaochen designs.

## Features

- **Layout**: Blog-style with right sidebar for profile/contacts, main content area
- **Navigation**: Top menu with 首页(Home), 标签(Tags), 分类(Categories), 归档(Archives), 登录(Login)
- **Personal Profile**: Avatar, name, description, contact links (GitHub, Twitter, Email, Telegram, RSS)
- **Categories**: Grid display showing article counts
- **Tags**: Cloud style with tag counts
- **Archives**: Timeline-style monthly post listing
- **User Authentication**: Login/Signup system with password hashing
- **Responsive Design**: Works on mobile and desktop
- **Colors**: Light theme matching shiquda style (#eee background)

## Requirements

- Python 3.7+
- pip

## Installation

1. Navigate to project directory:
   ```
   cd Easonswensite
   ```

2. Install dependencies:
   ```
   pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug
   ```

## Running the Website

1. Run the Flask app:
   ```
   python app.py
   ```

2. Open browser: http://127.0.0.1:5000

## Project Structure

```
Easonswensite/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md           # This file
│
├── templates/          # HTML templates
│   ├── base.html       # Base layout with sidebar
│   ├── index.html      # Home page
│   ├── about.html      # About page
│   ├── contact.html    # Contact page
│   ├── login.html      # Login page
│   ├── signup.html     # Signup page
│   ├── tags.html       # Tags page
│   ├── categories.html # Categories page
│   └── archives.html   # Archives page
│
└── static/             # Static assets
    ├── css/
    │   └── style.css   # Custom styles (shiquda-style)
    ├── js/
    │   └── main.js     # Custom JavaScript
    └── images/
        └── avatar.png  # Profile picture
```

## Customization

### Changing Avatar
Replace `static/images/avatar.png` with your own image (recommended size: 200x200px).

### Modifying Contact Links
Edit the links in `templates/base.html` in the "Contact links" section.

### Adding Categories/Tags/Posts
Currently sample data is used. To add real functionality, you would need to:
1. Create database models for posts
2. Update the routes in `app.py` to query from database
3. Add admin interface for creating content

### Colors
The color scheme matches shiquda:
- Background: #eee
- Content: #fff
- Text: #555
- Theme/Brand: #222

## Design Reference

The design is inspired by:
- **shiquda.link** - Blog layout with right sidebar
- **yuhaochen** (www.yuhaoc.net) - Clean personal website style

Key features from these references:
- Fixed right sidebar with profile
- Navigation menu at top
- Card-based content blocks
- Clean typography
- Category/tag/archives pages
- Header with gradient (headband)
- Quote section (hitokoto)

## Pages

1. **首页 (Home)**: Welcome message and introduction
2. **关于 (About)**: Personal information and skills
3. **联系 (Contact)**: Contact form and information
4. **标签 (Tags)**: Cloud display of all tags
5. **分类 (Categories)**: Grid of categories with post counts
6. **归档 (Archives)**: Timeline of posts by month
7. **登录 (Login)**: User login form
8. **注册 (Signup)**: User registration form
