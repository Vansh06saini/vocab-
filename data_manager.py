# data_manager.py
import csv
import json
from config import USER_DATA_FILE, WORDS_FILE

def load_common_words():
    """Loads quiz words from a CSV file (column name: 'word'). Returns a list."""
    words = []
    try:
        with open(WORDS_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # If file has no header or wrong header, try reading as single-column
            if reader.fieldnames and 'word' in reader.fieldnames:
                for row in reader:
                    w = (row.get('word') or '').strip()
                    if w:
                        words.append(w)
            else:
                # fallback: read every non-empty line as a word
                file.seek(0)
                for line in file:
                    line = line.strip()
                    if line and line.lower() != 'word':
                        words.append(line)
    except FileNotFoundError:
        print(f"[{WORDS_FILE}] not found. Please create it with a column 'word'.")
    except Exception as e:
        print(f"Error loading words: {e}")
    return words

def load_users():
    """
    Loads users from USER_DATA_FILE and returns a dict:
    { username: {'password': str, 'score': int, 'incorrect_words': {word: count}} }
    """
    users = {}
    try:
        with open(USER_DATA_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)
            # If header is present and matches, keep going; else try to recover
            expected_header = ['username', 'password', 'score', 'incorrect_words_json']
            if header != expected_header:
                # If file empty or header mismatch, attempt to treat first row as header only if it matches expected header partially
                # Reset to start and continue reading rows assuming they are data rows
                file.seek(0)
                reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                # Skip rows that don't have expected 4 columns
                if len(row) != 4:
                    # Try to tolerate rows where the JSON column contains commas (CSV quoting should protect this)
                    # If length < 4 skip, if >4 try to recombine last columns
                    if len(row) > 4:
                        # recombine extras into last column
                        username = row[0]
                        password = row[1] if len(row) > 1 else ''
                        score = row[2] if len(row) > 2 else '0'
                        incorrect_json = ','.join(row[3:])
                    else:
                        # malformed line: skip
                        continue
                else:
                    username, password, score, incorrect_json = row

                # parse incorrect words json safely
                try:
                    incorrect_words = json.loads(incorrect_json) if incorrect_json else {}
                    if not isinstance(incorrect_words, dict):
                        incorrect_words = {}
                except json.JSONDecodeError:
                    # Try to fix common problems (single quotes)
                    try:
                        incorrect_words = json.loads(incorrect_json.replace("'", '"'))
                        if not isinstance(incorrect_words, dict):
                            incorrect_words = {}
                    except Exception:
                        incorrect_words = {}

                # ensure score is int
                try:
                    score_val = int(score)
                except Exception:
                    # if score can't be parsed, default to 0
                    try:
                        score_val = int(float(score))
                    except Exception:
                        score_val = 0

                users[username] = {
                    'password': password,
                    'score': score_val,
                    'incorrect_words': incorrect_words
                }
    except FileNotFoundError:
        # no users file yet, return empty dict
        pass
    except Exception as e:
        print(f"Error loading users: {e}")
    return users

def save_users(users):
    """
    Writes the users dict back to CSV with header:
    username,password,score,incorrect_words_json
    The incorrect_words column is json.dumps(...) so it's safely quoted for CSV.
    """
    try:
        with open(USER_DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password', 'score', 'incorrect_words_json'])
            for username, data in users.items():
                pw = data.get('password', '')
                score = data.get('score', 0)
                incorrect = data.get('incorrect_words', {}) or {}
                # Ensure it's a dict
                if not isinstance(incorrect, dict):
                    incorrect = {}
                # Dump JSON with double quotes; csv.writer will quote this field as needed
                wrong_json = json.dumps(incorrect, ensure_ascii=False)
                writer.writerow([username, pw, score, wrong_json])
    except Exception as e:
        print(f"Error saving users: {e}")
