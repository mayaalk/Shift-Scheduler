from datetime import datetime, timedelta

shifts = []

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

def main():
    while True:
        print("\nEmployee Shift Scheduler")
        print("========================")
        print("1. Schedule a Shift")
        print("2. View Shifts")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
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
            

if __name__ == "__main__":
    main()