# Club33 Canteen Flask App

This project is a Flask-based canteen ordering application for Club33.
It includes:

- a public menu experience for customers
- an admin area for managing categories and menu items
- order tracking with statuses such as pending, confirmed, ready, and collected

## Project structure

- app/ - application package containing models, routes, templates, and static assets
- config.py - configuration settings for development, testing, and production
- run.py - development entry point
- requirements.txt - Python dependencies

## Getting started

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the development server:
   ```bash
   python run.py
   ```

## Notes

The application uses Flask-SQLAlchemy with SQLite by default. The database file is created under the instance directory when the app starts.
