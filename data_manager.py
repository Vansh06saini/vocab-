# data_manager.py
import csv
import json
from config import USER_DATA_FILE, WORDS_FILE

def load_common_words():
    """Loads quiz words from a CSV file."""
    words = []
    try:
        with open(WORDS_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                word = row.get('word', '').strip()
                if word:
                    words.append(word)
    except FileNotFoundError:
        print(f"[{WORDS_FILE}] not found. Please create it with a column 'word'.")
    except Exception as e:
        print(f"Error loading words: {e}")
    return words

def load_users():
    """Loads user data from a CSV file."""
    users = {}
    try:
        with open(USER_DATA_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)
            if header != ['username', 'password', 'score', 'incorrect_words_json']:
                # Reset file pointer if header is missing/incorrect, for a clean read (or could skip if file is empty)
                file.seek(0)
                next(reader, None) # Try to skip header again if file was not empty
            for row in reader:
                if len(row) == 4:
                    username, password, score, incorrect_words_json = row
                    try:
                        incorrect_words = json.loads(incorrect_words_json)
                    except json.JSONDecodeError:
                        incorrect_words = {}
                    users[username] = {
                        'password': password,
                        'score': int(score),
                        'incorrect_words': incorrect_words
                    }
    except FileNotFoundError:
        print(f"[{USER_DATA_FILE}] not found. Starting fresh.")
    return users

def save_users(users):
    """Saves all user data to a CSV file."""
    try:
        with open(USER_DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password', 'score', 'incorrect_words_json'])
            for username, data in users.items():
                writer.writerow([username, data['password'], data['score'], json.dumps(data['incorrect_words'])])
    except Exception as e:
        print(f"Error saving users: {e}")