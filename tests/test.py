from datetime import datetime
import pytz

def convert_to_eat(datetime_str):
    if datetime_str is None:
        return ""
    
    # Define the original and target time zones
    original_tz = pytz.timezone('UTC')
    target_tz = pytz.timezone('Africa/Nairobi')  # EAT is equivalent to Africa/Nairobi time zone

    try:
        # Parse the input datetime string
        naive_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        
        # Localize the naive datetime to the original timezone (UTC)
        localized_dt = original_tz.localize(naive_dt)
        
        # Convert to the target timezone (EAT)
        eat_dt = localized_dt.astimezone(target_tz)
        
        # Format the datetime to the desired string format
        formatted_dt = eat_dt.strftime("%y/%m/%d %H:%M")
        return formatted_dt
    
    except ValueError:
        # Handle cases where the datetime_str is not in the expected format
        return ""

# Example usage
print(convert_to_eat("2023-01-11 00:00:00"))  # Output should be: 11/1/23 3:00 (since EAT is UTC+3)
print(convert_to_eat(None))