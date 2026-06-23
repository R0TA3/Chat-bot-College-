"""
AI-Powered College Enquiry Chatbot
Main Flask Application

Routes:
  User-facing:
    GET  /                    -> chat interface
    POST /api/chat            -> process a chat message, return bot reply
    GET  /api/faqs            -> list public FAQs (for FAQ page)

  Admin:
    GET  /admin/login         -> admin login page
    POST /admin/login         -> authenticate
    GET  /admin/logout        -> logout
    GET  /admin/dashboard     -> analytics dashboard
    GET  /admin/faqs          -> manage FAQs page
    POST /admin/faqs/add      -> add FAQ
    POST /admin/faqs/edit/<id>-> edit FAQ
    POST /admin/faqs/delete/<id> -> delete FAQ
    GET  /admin/chat-history  -> view chat history
    GET  /admin/unanswered    -> view unanswered queries
"""

import uuid
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from db import Database
from nlp_engine import NLPEngine, check_greeting

app = Flask(__name__)
app.config.from_object(Config)

nlp_engine = NLPEngine()


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def load_faq_index():
    """(Re)build the in-memory TF-IDF index from the current FAQ table."""
    rows = Database.execute_query(
        "SELECT faq_id, question, answer, category, keywords FROM faq",
        fetch=True
    )
    nlp_engine.build_index(rows or [])


def admin_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_id'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def get_or_create_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


# ----------------------------------------------------------------------------
# User-facing routes
# ----------------------------------------------------------------------------

@app.route('/')
def index():
    get_or_create_session_id()
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get('message') or '').strip()
    session_id = get_or_create_session_id()

    if not user_message:
        return jsonify({'reply': "Please type a question and I'll do my best to help!", 'confidence': 0})

    # 1. Check for greetings/smalltalk first
    canned = check_greeting(user_message)
    if canned:
        _log_chat(session_id, user_message, canned, None, 1.0)
        return jsonify({'reply': canned, 'confidence': 1.0, 'matched': False})

    # 2. NLP match against FAQ database
    match, score = nlp_engine.find_best_match(user_message)

    if match:
        reply = match['answer']
        _log_chat(session_id, user_message, reply, match['faq_id'], score)
        return jsonify({
            'reply': reply,
            'confidence': round(score, 3),
            'matched': True,
            'category': match['category']
        })
    else:
        fallback = ("I'm sorry, I don't have an exact answer for that yet. "
                    "Could you rephrase your question, or contact the admission office at "
                    "admissions@college.edu / +91-9876543211 for direct assistance?")
        _log_chat(session_id, user_message, fallback, None, score)
        Database.execute_query(
            "INSERT INTO unanswered_queries (session_id, message) VALUES (%s, %s)",
            (session_id, user_message), commit=True
        )
        return jsonify({'reply': fallback, 'confidence': round(score, 3), 'matched': False})


def _log_chat(session_id, message, response, matched_faq_id, confidence):
    try:
        Database.execute_query(
            """INSERT INTO chat_history (session_id, message, response, matched_faq_id, confidence_score)
               VALUES (%s, %s, %s, %s, %s)""",
            (session_id, message, response, matched_faq_id, confidence),
            commit=True
        )
    except Exception as e:
        print(f"[WARN] Failed to log chat: {e}")


@app.route('/api/faqs')
def public_faqs():
    rows = Database.execute_query(
        "SELECT question, answer, category FROM faq ORDER BY category, faq_id",
        fetch=True
    )
    return jsonify(rows or [])


# ----------------------------------------------------------------------------
# Admin routes
# ----------------------------------------------------------------------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        admin = Database.execute_query(
            "SELECT * FROM admin WHERE email = %s", (email,), fetch_one=True
        )

        if admin and check_password_hash(admin['password'], password):
            session['admin_id'] = admin['admin_id']
            session['admin_name'] = admin['name']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@admin_login_required
def admin_dashboard():
    total_faqs = Database.execute_query("SELECT COUNT(*) AS cnt FROM faq", fetch_one=True)['cnt']
    total_chats = Database.execute_query("SELECT COUNT(*) AS cnt FROM chat_history", fetch_one=True)['cnt']
    total_unanswered = Database.execute_query(
        "SELECT COUNT(*) AS cnt FROM unanswered_queries WHERE resolved = FALSE", fetch_one=True
    )['cnt']
    unique_sessions = Database.execute_query(
        "SELECT COUNT(DISTINCT session_id) AS cnt FROM chat_history", fetch_one=True
    )['cnt']

    category_stats = Database.execute_query(
        """SELECT f.category, COUNT(c.chat_id) AS hits
           FROM chat_history c JOIN faq f ON c.matched_faq_id = f.faq_id
           GROUP BY f.category ORDER BY hits DESC""",
        fetch=True
    )

    recent_chats = Database.execute_query(
        "SELECT * FROM chat_history ORDER BY timestamp DESC LIMIT 10",
        fetch=True
    )

    return render_template(
        'admin_dashboard.html',
        total_faqs=total_faqs,
        total_chats=total_chats,
        total_unanswered=total_unanswered,
        unique_sessions=unique_sessions,
        category_stats=category_stats or [],
        recent_chats=recent_chats or []
    )


@app.route('/admin/faqs')
@admin_login_required
def admin_faqs():
    faqs = Database.execute_query("SELECT * FROM faq ORDER BY category, faq_id", fetch=True)
    return render_template('admin_faqs.html', faqs=faqs or [])


@app.route('/admin/faqs/add', methods=['POST'])
@admin_login_required
def add_faq():
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    category = request.form.get('category', '').strip()
    keywords = request.form.get('keywords', '').strip()

    if question and answer and category:
        Database.execute_query(
            "INSERT INTO faq (question, answer, category, keywords) VALUES (%s, %s, %s, %s)",
            (question, answer, category, keywords), commit=True
        )
        load_faq_index()
        flash('FAQ added successfully.', 'success')
    else:
        flash('Question, answer, and category are required.', 'error')

    return redirect(url_for('admin_faqs'))


@app.route('/admin/faqs/edit/<int:faq_id>', methods=['POST'])
@admin_login_required
def edit_faq(faq_id):
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    category = request.form.get('category', '').strip()
    keywords = request.form.get('keywords', '').strip()

    Database.execute_query(
        "UPDATE faq SET question=%s, answer=%s, category=%s, keywords=%s WHERE faq_id=%s",
        (question, answer, category, keywords, faq_id), commit=True
    )
    load_faq_index()
    flash('FAQ updated successfully.', 'success')
    return redirect(url_for('admin_faqs'))


@app.route('/admin/faqs/delete/<int:faq_id>', methods=['POST'])
@admin_login_required
def delete_faq(faq_id):
    Database.execute_query("DELETE FROM faq WHERE faq_id = %s", (faq_id,), commit=True)
    load_faq_index()
    flash('FAQ deleted successfully.', 'success')
    return redirect(url_for('admin_faqs'))


@app.route('/admin/chat-history')
@admin_login_required
def admin_chat_history():
    page = int(request.args.get('page', 1))
    per_page = 25
    offset = (page - 1) * per_page

    chats = Database.execute_query(
        "SELECT * FROM chat_history ORDER BY timestamp DESC LIMIT %s OFFSET %s",
        (per_page, offset), fetch=True
    )
    total = Database.execute_query("SELECT COUNT(*) AS cnt FROM chat_history", fetch_one=True)['cnt']
    total_pages = max(1, (total + per_page - 1) // per_page)

    return render_template('admin_chat_history.html', chats=chats or [], page=page, total_pages=total_pages)


@app.route('/admin/unanswered')
@admin_login_required
def admin_unanswered():
    queries = Database.execute_query(
        "SELECT * FROM unanswered_queries ORDER BY timestamp DESC", fetch=True
    )
    return render_template('admin_unanswered.html', queries=queries or [])


@app.route('/admin/unanswered/resolve/<int:query_id>', methods=['POST'])
@admin_login_required
def resolve_unanswered(query_id):
    Database.execute_query(
        "UPDATE unanswered_queries SET resolved = TRUE WHERE query_id = %s",
        (query_id,), commit=True
    )
    flash('Marked as resolved.', 'success')
    return redirect(url_for('admin_unanswered'))


# ----------------------------------------------------------------------------
# App startup
# ----------------------------------------------------------------------------

@app.before_request
def ensure_index_built():
    if not nlp_engine.is_fitted:
        try:
            load_faq_index()
        except Exception as e:
            print(f"[WARN] Could not build FAQ index yet: {e}")


if __name__ == '__main__':
    Database.init_pool()
    load_faq_index()
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
