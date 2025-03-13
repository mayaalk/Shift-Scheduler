from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory storage for employee availability
availability_db = {}

@app.route('/availability', methods=['POST'])
def set_availability():
    data = request.json
    employee_name = data.get("employee_name")
    date = data.get("date")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    if employee_name not in availability_db:
        availability_db[employee_name] = []
    
    availability_db[employee_name].append({
        "date": date,
        "start_time": start_time,
        "end_time": end_time
    })
    return jsonify({"message": f"Availability set for {employee_name} on {date}."}), 201

@app.route('/availability/check', methods=['POST'])
def check_availability():
    data = request.json
    employee_name = data.get("employee_name")
    date = data.get("date")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    print(f"Checking availability for {employee_name} on {date}:")
    print(f"Requested time slot: {start_time} to {end_time}")
    
    # Convert string times to datetime objects for proper comparison
    req_start = datetime.strptime(start_time, "%I:%M %p")
    req_end = datetime.strptime(end_time, "%I:%M %p")

    if employee_name not in availability_db:
        return jsonify({"available": False, "message": f"{employee_name} has no availability set."})

    for slot in availability_db[employee_name]:
        if slot["date"] == date:
            print(f"Found available slot: {slot['start_time']} to {slot['end_time']}")
            
            # Convert slot times to datetime objects
            slot_start = datetime.strptime(slot["start_time"], "%I:%M %p")
            slot_end = datetime.strptime(slot["end_time"], "%I:%M %p")
            
            # Check if the requested time slot falls entirely within the available slot
            if slot_start <= req_start and req_end <= slot_end:
                print("Time slot matches!")
                return jsonify({"available": True, "message": f"{employee_name} is available on {date}."})
    
    print("No matching time slot found.")
    return jsonify({"available": False, "message": f"{employee_name} is not available on {date}."})

@app.route('/availability/all', methods=['GET'])
def get_all_availabilities():
    """Returns all stored employee availabilities"""
    return jsonify({"availabilities": availability_db}), 200

@app.route('/availability/employees', methods=['POST'])
def get_available_employees():
    """Returns a list of employees available for a given time slot"""
    data = request.json
    date = data.get("date")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    
    if not all([date, start_time, end_time]):
        return jsonify({"available_employees": [], "error": "Missing required parameters"}), 400
        
    # Convert string times to datetime objects for proper comparison
    req_start = datetime.strptime(start_time, "%I:%M %p")
    req_end = datetime.strptime(end_time, "%I:%M %p")
    
    available_employees = []
    
    for employee_name, slots in availability_db.items():
        for slot in slots:
            if slot["date"] == date:
                # Convert slot times to datetime objects
                slot_start = datetime.strptime(slot["start_time"], "%I:%M %p")
                slot_end = datetime.strptime(slot["end_time"], "%I:%M %p")
                
                # Check if the requested time slot falls entirely within the available slot
                if slot_start <= req_start and req_end <= slot_end:
                    available_employees.append(employee_name)
                    break  # Once we find one matching slot for this employee, we can move on
    
    return jsonify({"available_employees": available_employees}), 200

if __name__ == "__main__":
    app.run(port=5001)
