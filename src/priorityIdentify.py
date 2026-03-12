# Import timeParser functions
from timeParser import parseFileToDictionary

def main_menu():
    user_priority = None
    
    while True:
        print("\n=== Main Menu ===")
        print("1. Set your #1 Priority for today")
        print("2. Check if you followed your priority")
        print("3. Exit")
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == '1':
            user_priority = input("What is your #1 priority? (e.g., coding, studying): ").strip().lower()
            print(f"--> Priority successfully set to: '{user_priority}'.")
            
        elif choice == '2':
            # To make sure users sets a priority first
            if not user_priority:
                print("--> Please set your priority first (Option 1)!")
                continue
                
            file_path = "src/tests/file1.txt" 
            
            try:
                sorted_data = parseFileToDictionary(file_path)
            except FileNotFoundError:
                print("Error: Could not find the data file.")
                continue
                
            if not sorted_data:
                print("No activity data found.")
                continue
                
            # Identify the top activity
            top_activity = list(sorted_data.keys())[0]
            top_time = list(sorted_data.values())[0]
            
            print("\n--- Priority Feedback ---")
            if user_priority == top_activity:
                print(f"Success! You followed your priority. You spent the most time ({top_time} mins) on {user_priority}.")
            elif user_priority in sorted_data:
                actual_time = sorted_data[user_priority]
                print(f"Feedback: Your priority was '{user_priority}' ({actual_time} mins), but you spent more time on '{top_activity}' ({top_time} mins). Let's adjust tomorrow!")
            else:
                print(f"Feedback: You didn't track any time for '{user_priority}' today. Make sure to schedule it in!")
                
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the app
if __name__ == "__main__":
    main_menu()