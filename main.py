# main.py
from vocabulary_bot import VocabularyBot

def main():
    """
    Main function for the Vocabulary Quiz Bot application.
    Handles the initial login/registration loop.
    """
    bot = VocabularyBot()
    
    while not bot.current_user:
        print("\n# VOCABULARY QUIZ BOT #")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        
        choice = input("Enter choice (1-3): ").strip()
        if choice == '1' and bot.login():
            break
        elif choice == '2' and bot.register():
            break
        elif choice == '3':
            print("Exiting application.")
            return
        else:
            print("Invalid choice.")

    if bot.current_user:
        bot.main_menu()


if __name__ == "__main__":
    main()