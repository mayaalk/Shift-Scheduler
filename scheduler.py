from datetime import datetime, timedelta

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

# Function to schedule a shift
def schedule_shift(employee_name, date, start_time):
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
    
    # Calculate end time for the shift
    end_time = calculate_end_time(start_time)
    new_shift = {
        "employee_name": employee_name,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
    }

    # Check for overlapping shifts
    if is_overlapping(new_shift):
        return f"Error: Shift overlaps with another shift on {date} from {start_time} to {end_time}."

    # Confirm submission
    while True:
        confirm = input(f"Confirm shift for {employee_name} on {date} from {start_time} to {end_time}? (Y/N): ").strip().lower()
        if confirm == "y":
            shifts.append(new_shift)
            return f"Shift successfully scheduled for {employee_name} on {date} from {start_time} to {end_time}."
        elif confirm == "n":
            return "Shift scheduling canceled."
        else:
            print("Invalid input. Please enter 'Y' to submit or 'N' to cancel.")

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
        print("No shifts scheduled for the selected period.")
    else:
        print("Scheduled Shifts:")
        for shift in scheduled_shifts:
            print(f"- {shift['employee_name']}: {shift['date']} {shift['start_time']} to {shift['end_time']}")

# CLI for interacting with the scheduler
def main():
    while True:
        print("\nEmployee Shift Scheduler")
        print("========================")
        print("1. Schedule a Shift")
        print("2. View Shifts")
        print("3. Exit")
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
                    continue

                result = schedule_shift(employee_name, date, start_time)
                print(result)

                # Ask if the user wants to add another shift
                add_more = input("Do you want to add another shift? (Y/N): ").strip().lower()
                if add_more != "y":
                    break
        elif choice == "2":
            view_shifts()
        elif choice == "3":
            print("Exiting the scheduler. Goodbye!")
            return
        else:
            print("Invalid choice. Please try again.")
            
            
if __name__ == "__main__":
    main()