from datetime import datetime, timedelta
import zmq
import json
import requests
import requests
    
#---------------------------------------------------------------------------#

# Function for Microservice A
def get_tip_of_the_day():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  
    socket.connect("tcp://localhost:1234")  # Connect to the microservice
    socket.send_string("get") 
    response = socket.recv_string()  
    tip_data = json.loads(response)  
    if "tip" in tip_data:
        return tip_data["tip"]
    elif "error" in tip_data:
        return f"Error fetching tip: {tip_data['error']}"
    else:
        return "Unknown error occurred while fetching the tip."
    
# Display the Tip of the Day at the start of the program
tip = get_tip_of_the_day()
print(f"🌟 Tip of the Day: {tip} 🌟\n")

def format_time(time_str):
    try:
        return datetime.strptime(time_str, "%I:%M %p").strftime("%I:%M %p")
    except ValueError:
        return "Invalid time format. Please use HH:MM AM/PM."
    
#---------------------------------------------------------------------------#

# Functions for Microservice B
def set_employee_availability(employee_name, date, start_time, end_time):
    url = "http://localhost:5001/availability"
    payload = {
        "employee_name": employee_name,
        "date": date,
        "start_time": start_time,
        "end_time": end_time
    }
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        return response.json().get("message")
    else:
        return f"Error setting availability: {response.text}"

def check_employee_availability(employee_name, date, start_time, end_time):
    url = "http://localhost:5001/availability/check"
    payload = {
        "employee_name": employee_name,
        "date": date,
        "start_time": start_time,
        "end_time": end_time
    }
    response = requests.post(url, json=payload)
    return response.json()

# Set availabilities
def test_microservice_b():
    
    result = set_employee_availability("John", "2025-03-20", format_time("9:00 AM"), format_time("5:00 PM"))
    print(result)  
    result = set_employee_availability("Alice", "2025-03-21", format_time("9:00 AM"), format_time("5:00 PM"))
    print(result)
    result = set_employee_availability("Casey", "2025-03-22", format_time("9:00 AM"), format_time("5:00 PM"))
    print(result)
test_microservice_b()

#---------------------------------------------------------------------------#

# Functions for Microservice C
def send_notification(event_type, data):
    url = "http://localhost:5002/notify"
    payload = {"event_type": event_type, **data}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return True, response.json().get("message", "Notification sent successfully.")
        else:
            print(f"HTTP Error: Status Code {response.status_code}")  
            return False, f"Error sending notification: {response.text}"
    except Exception as e:
        print(f"Exception during notification: {str(e)}")  
        return False, f"Error connecting to notification service: {str(e)}"
    
def notify_no_show(employee_name, date, shift_time, manager_name="Manager"):
    """
    Report an employee as a no-show for their scheduled shift.
    """
    notification_data = {
        "event_type": "no_show",
        "manager_name": manager_name,
        "employee_name": employee_name,
        "shift_date": date,
        "shift_time": shift_time
    }
    try:
        success, message = send_notification(event_type="no_show", data=notification_data)
        if success:
            return f"No-show notification for {employee_name} on {date} at {shift_time} sent to {manager_name}."
        else:
            return f"Warning: Could not send no-show notification: {message}"
    except Exception as e:
        return f"Error: Failed to report no-show: {str(e)}"
    
#---------------------------------------------------------------------------#

# Function for Microservice D
def fetch_holidays():
    print("========================")
    print("View Holidays")
    print("========================")
    year = input("Enter year (YYYY): ")

    try:
        year = int(year)
    except ValueError:
        print("Error: Invalid year format. Please enter a valid year (e.g., 2023).")
        return

    url = "http://localhost:5004/holidays"
    payload = {"year": year}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            holidays_data = response.json()
            print(f"Holidays for {holidays_data['year']}:")
            for name, date in holidays_data["holidays"].items():
                print(f"- {name}: {date}")
        else:
            print(f"Error fetching holidays: {response.text}")
    except Exception as e:
        print(f"Error connecting to holiday service: {str(e)}")

#---------------------------------------------------------------------------#

# In-memory database for storing shifts
shifts = []

# Helper function to check for overlapping shifts
def is_overlapping(new_shift):
    new_start = datetime.strptime(new_shift["start_time"], "%I:%M %p")
    new_end = datetime.strptime(new_shift["end_time"], "%I:%M %p")

    for shift in shifts:
        if shift["date"] == new_shift["date"]:
            existing_start = datetime.strptime(shift["start_time"], "%I:%M %p")
            existing_end = datetime.strptime(shift["end_time"], "%I:%M %p")
            
            # Check if new shift overlaps with any existing shift
            if new_start < existing_end and new_end > existing_start:
                return True
    return False

# Helper function to check shift count for a given date
def shift_count(date):
    return sum(1 for shift in shifts if shift["date"] == date)

# Helper function to calculate end time based on start time
def calculate_end_time(start_time):
    start = datetime.strptime(start_time, "%I:%M %p")
    end = start + timedelta(hours=8)  # Fixed duration of 8 hours
    return end.strftime("%I:%M %p")

def schedule_shift(employee_name, date, start_time):
    # Format start time for consistency
    formatted_start = format_time(start_time)
    
    # Calculate end time for the shift
    end_time = calculate_end_time(formatted_start)
    
    # Check employee availability using Microservice B
    availability_response = check_employee_availability(employee_name, date, formatted_start, end_time)
    if not availability_response.get("available", False):
        return f"Error: {employee_name} is not available for the requested shift on {date} from {formatted_start} to {end_time}."

    # Ensure the maximum of 3 shifts per day
    if shift_count(date) >= 3:
        return f"Error: Maximum shift limit (3 shifts) reached for {date}."
    
    # Count shifts for the employee in the given week
    start_date = datetime.strptime(date, "%Y-%m-%d")
    week_start = start_date - timedelta(days=start_date.weekday())
    week_end = week_start + timedelta(days=6)
    employee_shifts = [shift for shift in shifts if shift["employee_name"] == employee_name and week_start.strftime("%Y-%m-%d") <= shift["date"] <= week_end.strftime("%Y-%m-%d")]
    
    if len(employee_shifts) >= 5:
        return f"Error: {employee_name} has already worked 5 shifts this week ({week_start.strftime('%Y-%m-%d')} - {week_end.strftime('%Y-%m-%d')}). Please schedule a shift for next week."
    
    new_shift = {
        "employee_name": employee_name,
        "date": date,
        "start_time": formatted_start,
        "end_time": end_time,
    }

    # Check for overlapping shifts
    if is_overlapping(new_shift):
        return f"Error: Shift overlaps with another shift on {date} from {formatted_start} to {end_time}."

    # Confirm submission
    while True:
        confirm = input(f"Confirm shift for {employee_name} on {date} from {formatted_start} to {end_time}? (Y/N): ").strip().lower()
        if confirm == "y":
            shifts.append(new_shift)

            # Using Microservice C here:
            notification_data = {
                "event_type": "shift_reminder",
                "employee_name": employee_name,
                "shift_date": date,
                "shift_time": formatted_start
            }
            success, message = send_notification(event_type="shift_reminder", data=notification_data)
            if success:
                print("Notification sent successfully.")
            else:
                print(f"Warning: {message}")
    
            return f"Shift successfully scheduled for {employee_name} on {date} from {formatted_start} to {end_time}."
        elif confirm == "n":
            return "Shift scheduling canceled."
        else:
            print("Invalid input. Please enter 'Y' to submit or 'N' to cancel.")
            
# Helper function to find the closest available shift
def find_closest_shift(date):
    all_dates = sorted(set(shift["date"] for shift in shifts))
    
    if not all_dates:
        return "No shifts available."
    
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    closest_date = min(all_dates, key=lambda d: abs(datetime.strptime(d, "%Y-%m-%d") - date_obj))
    closest_shifts = [shift for shift in shifts if shift["date"] == closest_date]
    
    return f"No shifts found for {date}. Closest available shift(s) on {closest_date}:\n" + "\n".join(
        [f"- {shift['employee_name']}: {shift['start_time']} to {shift['end_time']}" for shift in closest_shifts]
    )

# Function to view shifts
def view_shifts():
    print("========================")
    print("View Employee Schedule")
    print("========================")
    print("1. View schedule for a specific date")
    print("2. View schedule for multiple dates")
    print("3. View schedule for a full month")
    choice = input("Enter your choice: ")
    
    if choice == "1":
        date = input("Enter date (YYYY-MM-DD): ")
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD.")
            return
        scheduled_shifts = [shift for shift in shifts if shift["date"] == date]
    
    elif choice == "2":
        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD.")
            return
        scheduled_shifts = [shift for shift in shifts if start_date <= shift["date"] <= end_date]
    
    elif choice == "3":
        month = input("Enter month (YYYY-MM): ")
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            print("Error: Invalid month format. Please use YYYY-MM.")
            return
        scheduled_shifts = [shift for shift in shifts if shift["date"].startswith(month)]
    
    else:
        print("Invalid choice. Please try again.")
        return
    
    if not scheduled_shifts:
        print(find_closest_shift(date))
    else:
        print("Scheduled Shifts:")
        for shift in scheduled_shifts:
            print(f"- {shift['employee_name']}: {shift['start_time']} to {shift['end_time']}")

# CLI for interacting with the scheduler
def main():
    while True:
        print("\nEmployee Shift Scheduler - Simple, Accurate, and Efficient Shift Scheduling at Your Fingertips!")
        print("========================")
        print("1. Schedule a Shift")
        print("2. View Shifts")
        print("3. Report No-Show")
        print("4. Holidays Calendar")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            while True:
                print("========================")
                print("Schedule a New Shift")
                print("========================")
                employee_name = input("Enter employee name: ")
                date = input("Enter date (YYYY-MM-DD): ")
                start_time = input("Enter start time (HH:MM AM/PM): ")
                
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                    datetime.strptime(start_time, "%I:%M %p")
                except ValueError:
                    print("Error: Invalid date or time format. Please use YYYY-MM-DD and HH:MM AM/PM.")
                    break

                result = schedule_shift(employee_name, date, start_time)
                print(result)

                # Ask if the user wants to add another shift
                add_more = input("Do you want to add another shift? (Y/N): ").strip().lower()
                if add_more != "y":
                    break
                    
        elif choice == "2":
            view_shifts()
            
        elif choice == "3":
            print("========================")
            print("Report No-Show Employee")
            print("========================")
            employee_name = input("Enter employee name who didn't show up: ")
            date = input("Enter shift date (YYYY-MM-DD): ")
            shift_time = input("Enter shift start time (HH:MM AM/PM): ")
            manager_name = input("Enter manager name to notify (or press Enter for default): ")
            
            try:
                datetime.strptime(date, "%Y-%m-%d")
                datetime.strptime(shift_time, "%I:%M %p")
            except ValueError:
                print("Error: Invalid date or time format. Please use YYYY-MM-DD and HH:MM AM/PM.")
                continue
                
            if not manager_name:
                manager_name = "Manager"  # Default value
                
            # Verify if the employee was actually scheduled for this shift
            employee_scheduled = False
            for shift in shifts:
                if (shift["employee_name"] == employee_name and 
                    shift["date"] == date and 
                    shift["start_time"] == format_time(shift_time)):
                    employee_scheduled = True
                    break
                    
            if not employee_scheduled:
                print(f"Warning: {employee_name} was not scheduled for a shift on {date} at {shift_time}.")
                confirm = input("Do you still want to report this as a no-show? (Y/N): ").strip().lower()
                if confirm != "y":
                    continue
            
            result = notify_no_show(employee_name, date, shift_time, manager_name)
            print(result)

        elif choice == "4":
            fetch_holidays()

        elif choice == "5":
            print("Exiting the scheduler. Goodbye!")
            return
            
        else:
            print("Invalid choice. Please try again.")       
            
if __name__ == "__main__":
    main()
