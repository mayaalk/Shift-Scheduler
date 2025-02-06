from datetime import datetime, timedelta

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