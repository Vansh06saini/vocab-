# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from data_manager import save_users, load_users
from config import QUIZ_OPTIONS
from vocabulary_bot import VocabularyBot
import json
import time

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

    num_questions = request.args.get('num', type=int)
    quiz_data = []
    start_time = time.time()
    if num_questions:
        quiz_data = bot.create_quiz(num_questions)
    print(time.time()-start_time, "=======time")

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

    data = request.get_json(force=True)
    word = data.get('word', '').strip().lower()
    is_correct = data.get('correct', False)
    username = session['username']

    print(f"DEBUG: Received submit for '{word}' (correct={is_correct}) from {username}")

    # Load users from file (ensures we’re using latest data)
    users = load_users()

    # Ensure the current user exists in file data
    user = users.get(username)
    if not user:
        print("DEBUG: user not found in users.csv, creating new entry")
        user = {'password': 'unknown', 'score': 0, 'incorrect_words': {}}

    if 'incorrect_words' not in user:
        user['incorrect_words'] = {}

    # --- Update score and track wrong words ---
    if is_correct:
        user['score'] += 5
        if word in user['incorrect_words']:
            user['incorrect_words'][word] -= 1
            if user['incorrect_words'][word] <= 0:
                del user['incorrect_words'][word]
    else:
        user['score'] -= 1
        user['incorrect_words'][word] = user['incorrect_words'].get(word, 0) + 1

    # --- Update user data ---
    users[username] = user

    # --- Save to users.csv ---
    save_users(users)
    bot.users = users  # ✅ keep VocabularyBot memory synced

    print("DEBUG: Saved users.csv successfully for", username)

    return jsonify({
        'success': True,
        'score': user['score'],
        'incorrect_words': user['incorrect_words']
    })

# --- Lookup Word ---
@app.route('/lookup', methods=['GET', 'POST'])
def lookup():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user_score = bot.users.get(username, {}).get('score', 0)

    if request.method == 'POST':
        word = request.json.get('word', '').strip()
        if not word:
            return jsonify({'error': 'No word provided.'}), 400

        data = bot.display_lookup_menu(word)
        if not data:
            return jsonify({'error': 'Word not found or network error.'}), 404

        # Extract meaning, synonyms, antonyms
        lines = data.split('\n')
        meaning_lines = [l for l in lines if not l.startswith("Synonyms:") and not l.startswith("Antonyms:")]
        meaning = "\n".join(meaning_lines).strip()

        synonyms_line = next((l for l in lines if l.startswith("Synonyms:")), "Synonyms: None")
        antonyms_line = next((l for l in lines if l.startswith("Antonyms:")), "Antonyms: None")

        synonyms = synonyms_line.replace("Synonyms:", "").strip()
        antonyms = antonyms_line.replace("Antonyms:", "").strip()

        return jsonify({
            'word': word,
            'meaning': meaning,
            'synonyms': synonyms,
            'antonyms': antonyms
        })

    return render_template('lookup.html', current_user=username, user_score=user_score)

# --- Feedback ---
@app.route("/feedback")
def feedback():
    if 'username' not in session:
        return redirect(url_for("login"))

    username = session["username"]
    users = load_users()  # Load fresh data from users.csv
    user_data = users.get(username, {})
    wrong_words = user_data.get("incorrect_words", {})

    sorted_words = sorted(wrong_words.items(), key=lambda x: x[1], reverse=True)
    return render_template("feedback.html", username=username, wrong_words=sorted_words)

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
