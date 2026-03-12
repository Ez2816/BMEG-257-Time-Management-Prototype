
#Checks if user priority matches what they spent most time on
def check_priority(user_priority: str, sorted_activity_data: dict) -> bool:

    if not sorted_activity_data:
        return False
        
    # Isolate the top activity (the first key in the sorted dictionary)
    top_activity = list(sorted_activity_data.keys())[0]
    
    # Returns True if priority matches the top activity, False otherwise
    return user_priority.lower() == top_activity.lower()