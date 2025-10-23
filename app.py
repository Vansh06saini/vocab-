# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from data_manager import save_users
from config import QUIZ_OPTIONS

from vocabulary_bot import VocabularyBot
import json

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for sessions

bot = VocabularyBot()  # Initialize VocabularyBot

# --- Home / Index ---
@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user_score = bot.users.get(username, {}).get('score', 0)
    return render_template('index.html', current_user=username, user_score=user_score)

# --- Register ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        confirm = request.form['confirm'].strip()

        if not username or not password or not confirm:
            flash("All fields are required.", "error")
            return redirect(url_for('register'))

        if username in bot.users:
            flash("Username already exists.", "error")
            return redirect(url_for('register'))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for('register'))

        bot.users[username] = {'password': password, 'score': 0, 'incorrect_words': {}}
        save_users(bot.users)
        session['username'] = username
        flash(f"Welcome, {username}! Your account has been created.", "success")
        return redirect(url_for('index'))

    return render_template('register.html')

# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        user = bot.users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

# --- Choose Quiz ---
@app.route('/choose_quiz')
def choose_quiz():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('choose_quiz.html', QUIZ_OPTIONS=QUIZ_OPTIONS)

# --- Quiz Page ---
@app.route('/quiz')
def quiz():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user_score = bot.users.get(username, {}).get('score', 0)

    # Get number of questions from query param
    num_questions = request.args.get('num', type=int)
    quiz_data = []
    if num_questions:
        quiz_data = bot.create_quiz(num_questions)

    return render_template(
        'quiz.html',
        current_user=username,
        user_score=user_score,
        quiz=quiz_data,
        QUIZ_OPTIONS=QUIZ_OPTIONS
    )

# --- Submit Quiz Answer ---
@app.route('/quiz/submit', methods=['POST'])
def submit_quiz():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.json
    username = session['username']
    user = bot.users.get(username)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update score based on correctness
    if data.get('correct'):
        user['score'] += 5
    else:
        user['score'] -= 1

    save_users(bot.users)
    return jsonify({'success': True, 'score': user['score']})

# --- Lookup Word ---
@app.route('/lookup', methods=['GET', 'POST'])
def lookup():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user_score = bot.users.get(username, {}).get('score', 0)
    word = meaning = synonyms = antonyms = None

    if request.method == 'POST':
        word = request.form['word'].strip()
        data = bot.display_lookup_menu(word)  # ✅ Use the refactored method

        # Parse the returned text
        lines = data.split('\n')
        meaning_lines = [l for l in lines if not l.startswith("Synonyms:") and not l.startswith("Antonyms:")]
        meaning = "\n".join(meaning_lines)

        synonyms_line = next((l for l in lines if l.startswith("Synonyms:")), "Synonyms: None")
        antonyms_line = next((l for l in lines if l.startswith("Antonyms:")), "Antonyms: None")

        synonyms = synonyms_line.replace("Synonyms:", "").strip()
        antonyms = antonyms_line.replace("Antonyms:", "").strip()

    return render_template(
        'lookup.html',
        current_user=username,
        user_score=user_score,
        word=word,
        meaning=meaning,
        synonyms=synonyms,
        antonyms=antonyms
    )
# --- Feedback ---
@app.route('/feedback')
def feedback():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user_score = bot.users.get(username, {}).get('score', 0)
    missed_words = bot.users[username]['incorrect_words']
    missed_sorted = sorted(missed_words.items(), key=lambda x: x[1], reverse=True)[:10]

    return render_template('feedback.html', current_user=username, user_score=user_score, missed_words=missed_sorted)

# --- Leaderboard ---
@app.route('/leaderboard')
def leaderboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    ranks = sorted(((u, d['score']) for u, d in bot.users.items()), key=lambda x: x[1], reverse=True)
    return render_template('leaderboard.html', current_user=username, leaderboard=ranks)

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
