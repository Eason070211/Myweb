# My Personal Website

A portfolio/personal website built with Flask, featuring user authentication and responsive design.

## Features

- Home, About, Portfolio, and Contact pages
- User authentication (login/signup)
- Responsive design with Bootstrap 5
- Flash messaging system
- Static file serving (CSS, JS)

## Requirements

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```
   cd Easonswensite
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Set the FLASK_APP environment variable:
   ```
   set FLASK_APP=app.py
   ```
2. Run the Flask development server:
   ```
   flask run
   ```
3. Open your web browser and go to http://127.0.0.1:5000/

## Project Structure

```
Easonswensite/
│
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── about.html         # About page
│   ├── portfolio.html     # Portfolio page
│   ├── contact.html       # Contact page
│   ├── login.html         # Login page
│   └── signup.html        # Sign up page
│
└── static/                # Static assets
    ├── css/
    │   └── style.css      # Custom styles
    └── js/
        └── main.js        # Custom JavaScript
```

## Customization

- Modify the templates in the `templates/` folder to change the content
- Edit `static/css/style.css` to customize the styling
- Update `static/js/main.js` to add custom JavaScript functionality
- Change the secret key in `app.py` for production use
- Modify the database URI in `app.py` if you want to use a different database

## User Authentication

The website includes a simple user authentication system:
- Users can create accounts with username, email, and password
- Passwords are securely hashed using Werkzeug
- Authenticated users can access the portfolio page
- Flash messages provide feedback on login/signup attempts

## Database

The application uses SQLite by default, with the database file `site.db` created automatically in the project directory when the app runs for the first time.

## Deployment

For production deployment, consider:
- Changing the secret key to a secure random value
- Using a production WSGI server like Gunicorn
- Configuring a proper database (PostgreSQL, MySQL, etc.)
- Setting up environment variables for configuration