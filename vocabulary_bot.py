import random
from collections import defaultdict

# Import external modules
from config import QUIZ_OPTIONS
from data_manager import load_common_words, load_users, save_users
from api_client import api_lookup

class VocabularyBot:
    def __init__(self): 
        """Initialize bot and load user data + words."""
        self.users = load_users()
        self.current_user = None
        self.common_words = load_common_words()
        if not self.common_words:
            print("\n⚠ Warning: No words found in 'words.csv'. The quiz may not work until you add words.\n")

    # --- Authentication ---
    def register(self):
        print("\n--- Register New User ---")
        while True:
            username = input("Enter a new username: ").strip()
            if not username:
                print("Username cannot be empty.")
                continue
            if username in self.users:
                print("Username already exists.")
                continue
            password = input("Enter a password: ").strip()
            if not password:
                print("Password cannot be empty.")
                continue
            self.users[username] = {'password': password, 'score': 0, 'incorrect_words': {}}
            save_users(self.users)
            print(f"\n Registration successful! Welcome, {username}.")
            self.current_user = username
            return True

    def login(self):
        print("\n--- User Login ---")
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        if username in self.users and self.users[username]['password'] == password:
            self.current_user = username
            print(f"\n Welcome back, {username}! Current Score: {self.users[username]['score']}")
            return True
        print(" Invalid username or password.")
        return False

    # --- Quiz ---
    def create_quiz(self, num_questions):
        if not self.common_words:
            print("No words found in words.csv.")
            return []
        print(f"\nGenerating a {num_questions}-question quiz...")
        quiz = []
        # Get enough words to try to make the quiz
        random_words = random.sample(self.common_words, k=min(len(self.common_words), num_questions * 2))

        for word in random_words:
            if len(quiz) >= num_questions:
                break
            
            data = api_lookup(word) # Use imported api_lookup
            if not data:
                continue
            
            meanings = data.get('meanings', [])
            synonyms = set(s.lower() for m in meanings for s in m.get('synonyms', []))
            antonyms = set(a.lower() for m in meanings for a in m.get('antonyms', []))
            
            # Check for sufficient content to make a question
            if not synonyms and not antonyms:
                continue

            q_type = random.choice(['SYNONYM', 'ANTONYM'])
            
            # Prioritize the chosen type, but fall back if no options exist
            if q_type == 'SYNONYM' and synonyms:
                correct = random.choice(list(synonyms))
                label = 'synonym'
            elif antonyms: # This covers ANTONYM choice or SYNONYM fallback
                correct = random.choice(list(antonyms))
                label = 'antonym'
            else:
                continue

            # Create options/distractors
            all_opts = list(synonyms.union(antonyms).union(set(self.common_words)))
            distractors = [w for w in all_opts if w.lower() != correct.lower() and w.lower() != word.lower()]
            # Ensure distractors are not duplicates and take up to 3
            distractors = list(set(distractors))
            distractors = random.sample(distractors, min(3, len(distractors)))
            
            options = distractors + [correct]
            random.shuffle(options)
            
            # Only include words that are distinct options (case-insensitive check)
            unique_options = []
            seen = set()
            for opt in options:
                if opt.lower() not in seen:
                    unique_options.append(opt)
                    seen.add(opt.lower())

            # Only proceed if we have a correct answer and enough options
            if correct in unique_options and len(unique_options) >= 2:
                 quiz.append({'word': word, 'label': label, 'correct': correct, 'options': unique_options})
        
        print(f"Quiz generated with {len(quiz)} questions.")
        return quiz

    def run_quiz(self):
        print("\n--- MCQ Quiz ---")
        for i, num in enumerate(QUIZ_OPTIONS):
            print(f"{i+1}. {num} Questions")
        choice = input("Enter choice (1/2/3): ").strip()
        
        try:
            num_q = QUIZ_OPTIONS[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice.")
            return
            
        quiz = self.create_quiz(num_q)
        if not quiz:
            return
            
        score = 0
        wrong = defaultdict(int)
        
        for i, q in enumerate(quiz):
            print(f"\nQ{i+1}: What is the {q['label']} of '{q['word'].upper()}'?")
            opt_map = {}
            # Determine max letter for options dynamically
            max_char = chr(65 + len(q['options']) - 1) 
            
            for j, o in enumerate(q['options']):
                key = chr(65 + j)
                opt_map[key] = o
                print(f"  {key}. {o}")
                
            ans = input(f"Your answer (A-{max_char}): ").strip().upper()
            
            if ans in opt_map and opt_map[ans].lower() == q['correct'].lower():
                print("Correct! +5 points")
                score += 5
            else:
                print(f"Incorrect. The correct answer was: {q['correct']}")
                score -= 1
                wrong[q['word']] += 1
                
        user = self.users[self.current_user]
        user['score'] += score
        
        # Update incorrect word counts
        for w, c in wrong.items():
            user['incorrect_words'][w] = user['incorrect_words'].get(w, 0) + c
            
        save_users(self.users) # Use imported save_users
        print(f"\n🎯 Quiz complete! You scored {score} points. Total: {user['score']}")

    # --- Lookup ---
    def display_lookup_menu(self):
        word = input("\nEnter word to look up: ").strip()
        if not word:
            return
            
        data = api_lookup(word) # Use imported api_lookup
        
        if not data:
            print("Word not found.")
            return
            
        meanings = data.get('meanings', [])
        print(f"\n--- {word.upper()} ---")
        
        for m in meanings:
            pos = m.get('partOfSpeech', '')
            defs = m.get('definitions', [])
            if defs:
                print(f"({pos}) {defs[0]['definition']}")
                
        # Aggregate synonyms and antonyms from all meanings
        syns = set(s for m in meanings for s in m.get('synonyms', []))
        ants = set(a for m in meanings for a in m.get('antonyms', []))
        
        print("\nSynonyms:", ', '.join(list(syns)[:10]) or "None")
        print("Antonyms:", ', '.join(list(ants)[:10]) or "None")

    # --- Feedback & Leaderboard ---
    def display_feedback(self):
        wrong = self.users[self.current_user]['incorrect_words']
        if not wrong:
            print("\nNo challenging words yet!")
            return
            
        print("\n--- Most Missed Words ---")
        # Sort by count, descending, and show top 5
        for w, c in sorted(wrong.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"{w} (missed {c} times)")

    def display_leaderboard(self):
        print("\n--- Leaderboard ---")
        # Create a list of (username, score) tuples and sort by score
        ranks = sorted(((u, d['score']) for u, d in self.users.items()), key=lambda x: x[1], reverse=True)
        
        for i, (u, s) in enumerate(ranks[:10], 1):
            mark = "(YOU)" if u == self.current_user else ""
            print(f"{i}. {u} {mark} - {s} pts")

    # --- Main Menu ---
    def main_menu(self):
        while True:
            print(f"\nWelcome, {self.current_user}! Total Score: {self.users[self.current_user]['score']}")
            print("1. Take Quiz")
            print("2. Look Up a Word")
            print("3. View Feedback")
            print("4. Leaderboard")
            print("5. Exit")
            
            choice = input("Enter choice (1-5): ").strip()
            
            if choice == '1':
                self.run_quiz()
            elif choice == '2':
                self.display_lookup_menu()
            elif choice == '3':
                self.display_feedback()
            elif choice == '4':
                self.display_leaderboard()
            elif choice == '5':
                save_users(self.users) # Use imported save_users
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")