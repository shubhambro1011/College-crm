# College CRM — Real Flask + SQLite Version

This version keeps the existing College CRM UI and moves persistence from browser `localStorage` / unavailable Claude APIs to a real Flask backend with SQLite and user accounts.

## Run on Windows
1. Install Python 3.10+.
2. Open Command Prompt in this folder.
3. Run: `py -m pip install -r requirements.txt`
4. Run: `py app.py`
5. Open: `http://127.0.0.1:5000`
6. Create an account and use the CRM.

The database file `college_crm.db` is created automatically.

## Deploy
For public hosting, deploy the Flask app on a Python host (Render, Railway, PythonAnywhere, VPS, etc.). Set a strong `SECRET_KEY` environment variable. For production, use PostgreSQL instead of SQLite if many users will access it concurrently.
