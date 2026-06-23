# AI-Powered College Enquiry Chatbot

A complete web-based chatbot built with **Python, Flask, MySQL, and NLP (TF-IDF)** that answers
student/parent questions about admissions, courses, fees, placements, hostel facilities,
scholarships, and exams — 24/7, without staff intervention.

This matches the architecture: `User → Web Interface → Flask Backend → NLP Engine (TF-IDF) → MySQL Database → Response`

---

## Features

**Student-facing**
- Natural language Q&A chat interface
- Instant responses matched against a MySQL-backed FAQ database
- Confidence score shown per answer
- Falls back gracefully (with contact info) when it doesn't know something
- Quick-question shortcuts in the sidebar

**Admin panel** (`/admin/login`)
- Secure login (hashed passwords)
- Add / edit / delete FAQs, with optional keyword boosting for better matching
- Analytics dashboard: total FAQs, total conversations, unique visitors, most-asked categories
- Full chat history log (paginated)
- "Unanswered queries" report — shows what students asked that the bot couldn't answer, so you know what FAQs to add next

---

## Tech Stack

| Layer        | Technology                          |
|--------------|--------------------------------------|
| Frontend     | HTML, CSS, JavaScript (vanilla)      |
| Backend      | Python 3, Flask                      |
| Database     | MySQL                                |
| NLP / Matching | NLTK (tokenize, lemmatize) + Scikit-learn (TF-IDF + cosine similarity) |

---

## Project Structure

```
college_chatbot/
├── app.py                  # Main Flask app — all routes
├── config.py                # DB credentials & app settings (EDIT THIS)
├── db.py                     # MySQL connection pool wrapper
├── nlp_engine.py             # TF-IDF text preprocessing + matching engine
├── seed_data.py               # One-time script: creates default admin account
├── database.sql                # Full schema + 15 sample FAQs
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html                 # Student chat interface
│   ├── admin_login.html
│   ├── admin_base.html
│   ├── admin_dashboard.html
│   ├── admin_faqs.html
│   ├── admin_chat_history.html
│   └── admin_unanswered.html
└── static/
    ├── css/style.css
    └── js/chat.js
```

---

## Setup Instructions

### 1. Install MySQL
Make sure MySQL Server is installed and running locally (or use a remote instance).

### 2. Create the database
```bash
mysql -u root -p < database.sql
```
This creates the `college_chatbot` database, all 5 tables, and inserts 15 sample FAQs.

### 3. Configure credentials
Open `config.py` and update `DB_CONFIG` with your actual MySQL username/password:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_actual_mysql_password',
    'database': 'college_chatbot',
    'port': 3306,
}
```
(Or set environment variables `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT` instead.)

### 4. Install Python dependencies
```bash
cd college_chatbot
pip install -r requirements.txt
```

### 5. Seed the admin account
```bash
python seed_data.py
```
This creates the default admin login:
- **Email:** `admin@college.edu`
- **Password:** `admin123`

⚠️ Change this password after your first login (you can update it directly in MySQL with a new hash, or extend the admin panel — see "Next steps" below).

### 6. Run the app
```bash
python app.py
```
Visit:
- **Student chat:** http://localhost:5000/
- **Admin panel:** http://localhost:5000/admin/login

---

## How the NLP Matching Works

1. User types a question like *"is hostel facility available?"*
2. `nlp_engine.py` preprocesses it: lowercases, strips punctuation, tokenizes, removes stopwords, lemmatizes → `"hostel facility available"`
3. This is vectorized with the same **TF-IDF vectorizer** that was fit on all FAQ questions + keywords
4. **Cosine similarity** is computed between the query vector and every FAQ vector
5. The highest-scoring FAQ is returned — but only if the score clears `CONFIDENCE_THRESHOLD` (default `0.20`, set in `config.py`)
6. If nothing clears the threshold, the bot gives a polite fallback message and logs the question to `unanswered_queries` so admins can see what's missing

The FAQ index is rebuilt automatically every time an admin adds/edits/deletes an FAQ, so new answers are matchable immediately — no restart needed.

---

## Extending the Project

Ideas that map directly to the "Future Enhancements" on your project poster:
- **Multi-language support** — preprocess with `langdetect`, maintain FAQ translations per language
- **WhatsApp / Messenger integration** — reuse `/api/chat` as the webhook handler for Twilio/Meta APIs
- **Voice-based chatbot** — add Web Speech API on the frontend for speech-to-text input
- **Live chat handoff** — when confidence is low repeatedly, offer a "Talk to staff" button
- **Admin password change form** — small addition to the admin panel using `werkzeug.security`

---

## Notes

- Default confidence threshold is `0.20` — tune this in `config.py` if the bot feels too strict or too loose.
- Add more `keywords` per FAQ (synonyms, common misspellings/phrasings) to noticeably improve match quality without any code changes.
- All passwords are hashed with Werkzeug's `generate_password_hash` / `check_password_hash` — never stored in plain text.
