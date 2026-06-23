"""
NLP Engine for AI College Enquiry Chatbot.

Uses NLTK for text preprocessing (tokenization, stopword removal, lemmatization)
and Scikit-learn's TF-IDF Vectorizer + cosine similarity to match a user's
natural-language question against the FAQ database.

This is the "NLP ENGINE (TF-IDF)" component from the system architecture.
"""

import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import Config


def ensure_nltk_data():
    """Download required NLTK corpora if not already present."""
    packages = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']
    for pkg in packages:
        try:
            nltk.data.find(f'tokenizers/{pkg}') if 'punkt' in pkg else nltk.data.find(f'corpora/{pkg}')
        except LookupError:
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                pass


ensure_nltk_data()

try:
    STOPWORDS = set(stopwords.words('english'))
except Exception:
    STOPWORDS = set()

LEMMATIZER = WordNetLemmatizer()

# Keep a few question-relevant words that default stopword lists often remove
KEEP_WORDS = {'how', 'what', 'when', 'where', 'why', 'which', 'who', 'is', 'are', 'do', 'does'}
STOPWORDS = STOPWORDS - KEEP_WORDS


def preprocess_text(text: str) -> str:
    """Lowercase, strip punctuation/numbers noise, tokenize, remove stopwords, lemmatize."""
    if not text:
        return ""

    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    try:
        tokens = nltk.word_tokenize(text)
    except Exception:
        tokens = text.split()

    cleaned_tokens = []
    for token in tokens:
        if token in string.punctuation:
            continue
        if token in STOPWORDS and token not in KEEP_WORDS:
            continue
        lemma = LEMMATIZER.lemmatize(token)
        cleaned_tokens.append(lemma)

    return " ".join(cleaned_tokens)


class NLPEngine:
    """
    TF-IDF based matching engine.
    Fit once on the current FAQ set (question + keywords), then transform
    incoming user queries and compute cosine similarity to find best match.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.faq_data = []          # list of dicts: faq_id, question, answer, category
        self.tfidf_matrix = None
        self.is_fitted = False

    def build_index(self, faq_rows):
        """
        faq_rows: list of dicts with keys faq_id, question, answer, category, keywords
        Builds the TF-IDF matrix over preprocessed (question + keywords) text.
        """
        self.faq_data = faq_rows
        corpus = []
        for row in faq_rows:
            combined = f"{row.get('question', '')} {row.get('keywords', '') or ''}"
            corpus.append(preprocess_text(combined))

        if not corpus or all(c.strip() == "" for c in corpus):
            self.is_fitted = False
            return

        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self.is_fitted = True

    def find_best_match(self, user_query: str):
        """
        Returns: (faq_dict_or_None, confidence_score)
        confidence_score is cosine similarity in [0, 1].
        """
        if not self.is_fitted or not user_query.strip():
            return None, 0.0

        processed = preprocess_text(user_query)
        if not processed:
            return None, 0.0

        query_vector = self.vectorizer.transform([processed])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        best_idx = similarities.argmax()
        best_score = float(similarities[best_idx])

        if best_score < Config.CONFIDENCE_THRESHOLD:
            return None, best_score

        return self.faq_data[best_idx], best_score

    def get_top_matches(self, user_query: str, top_n=3):
        """Return top N matches with scores — useful for admin debugging / 'did you mean' suggestions."""
        if not self.is_fitted or not user_query.strip():
            return []

        processed = preprocess_text(user_query)
        query_vector = self.vectorizer.transform([processed])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        ranked_indices = similarities.argsort()[::-1][:top_n]
        results = []
        for idx in ranked_indices:
            results.append({
                'faq': self.faq_data[idx],
                'score': float(similarities[idx])
            })
        return results


# Simple intent fallbacks for greetings / smalltalk so the bot doesn't feel dumb
GREETING_PATTERNS = {
    'hi': "Hello! 👋 I'm the College Enquiry Bot. Ask me about admissions, courses, fees, hostel, placements, or scholarships.",
    'hello': "Hi there! How can I help you with college information today?",
    'hey': "Hey! Ask me anything about courses, admissions, fees, or campus facilities.",
    'thanks': "You're welcome! Let me know if you have any other questions.",
    'thank you': "Happy to help! Feel free to ask anything else about the college.",
    'bye': "Goodbye! Have a great day. Come back anytime you have questions.",
}


def check_greeting(user_query: str):
    """Check if the message is a simple greeting/smalltalk and return a canned reply if so."""
    cleaned = user_query.lower().strip().strip(string.punctuation)
    return GREETING_PATTERNS.get(cleaned)
