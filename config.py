"""
Configuration settings for AI College Enquiry Chatbot
Update DB_CONFIG with your actual MySQL credentials before running.
"""

import os

class Config:
    # ---- MySQL Database Configuration ----
    DB_CONFIG = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', 'your_mysql_password'),
        'database': os.environ.get('DB_NAME', 'college_chatbot'),
        'port': int(os.environ.get('DB_PORT', 3306)),
    }

    # ---- Flask Configuration ----
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-to-a-random-secret-key-in-production')
    DEBUG = True

    # ---- NLP Engine Configuration ----
    CONFIDENCE_THRESHOLD = 0.20   # below this, treated as "no good match"
    TOP_N_MATCHES = 1

    # ---- Admin default seed account (used only by seed_data.py) ----
    DEFAULT_ADMIN_NAME = "Administrator"
    DEFAULT_ADMIN_EMAIL = "admin@college.edu"
    DEFAULT_ADMIN_PASSWORD = "admin123"   # change immediately after first login
