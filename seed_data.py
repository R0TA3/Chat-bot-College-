"""
Seed script for AI College Enquiry Chatbot.

Run this ONCE after creating the database (database.sql) to:
  1. Create the default admin account with a securely hashed password.
  2. Verify FAQ table has data (database.sql already inserts samples).

Usage:
    python seed_data.py
"""

from werkzeug.security import generate_password_hash
from db import Database
from config import Config


def seed_admin():
    existing = Database.execute_query(
        "SELECT * FROM admin WHERE email = %s",
        (Config.DEFAULT_ADMIN_EMAIL,),
        fetch_one=True
    )

    if existing:
        print(f"[INFO] Admin account already exists: {Config.DEFAULT_ADMIN_EMAIL}")
        return

    hashed_pw = generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD)
    Database.execute_query(
        "INSERT INTO admin (name, email, password) VALUES (%s, %s, %s)",
        (Config.DEFAULT_ADMIN_NAME, Config.DEFAULT_ADMIN_EMAIL, hashed_pw),
        commit=True
    )
    print("[SUCCESS] Default admin account created.")
    print(f"          Email:    {Config.DEFAULT_ADMIN_EMAIL}")
    print(f"          Password: {Config.DEFAULT_ADMIN_PASSWORD}")
    print("          >>> Please log in and change this password immediately. <<<")


def verify_faqs():
    count = Database.execute_query("SELECT COUNT(*) AS cnt FROM faq", fetch_one=True)['cnt']
    print(f"[INFO] FAQ table currently has {count} entries.")


if __name__ == '__main__':
    Database.init_pool()
    print("=" * 60)
    print("Seeding AI College Enquiry Chatbot database...")
    print("=" * 60)
    seed_admin()
    verify_faqs()
    print("=" * 60)
    print("Done. You can now run: python app.py")
    print("=" * 60)
