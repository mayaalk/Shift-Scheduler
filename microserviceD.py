from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Federal holidays Database:
FEDERAL_HOLIDAYS = [
    {"name": "New Year's Day", "rule": lambda year: datetime(year, 1, 1)},
    {"name": "Martin Luther King Jr. Day", "rule": lambda year: nth_weekday(year, 1, 3)},  # Third Monday in Jan
    {"name": "Presidents' Day", "rule": lambda year: nth_weekday(year, 2, 3)},  # Third Monday in Feb
    {"name": "Memorial Day", "rule": lambda year: last_monday(year, 5)},  # Last Monday in May
    {"name": "Juneteenth National Independence Day", "rule": lambda year: datetime(year, 6, 19)},
    {"name": "Independence Day", "rule": lambda year: datetime(year, 7, 4)},
    {"name": "Labor Day", "rule": lambda year: nth_weekday(year, 9, 1)},  # First Monday in Sept
    {"name": "Columbus Day", "rule": lambda year: nth_weekday(year, 10, 2)},  # Second Monday in Oct
    {"name": "Veterans Day", "rule": lambda year: datetime(year, 11, 11)},
    {"name": "Thanksgiving Day", "rule": lambda year: nth_weekday(year, 11, 4)},  # Fourth Thursday in Nov
    {"name": "Christmas Day", "rule": lambda year: datetime(year, 12, 25)},
]

# Helper function to calculate the nth weekday of a month
def nth_weekday(year, month, n, weekday=0):
    first_day = datetime(year, month, 1)
    days_ahead = (weekday - first_day.weekday() + 7) % 7
    return first_day + timedelta(days=days_ahead + (n - 1) * 7)

# Helper function to calculate the last Monday of a month
def last_monday(year, month):
    next_month = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
    last_day = next_month - timedelta(days=1)
    days_behind = (last_day.weekday() - 0 + 7) % 7  # Monday=0
    return last_day - timedelta(days=days_behind)

# API endpoint to fetch holidays for a specific year
@app.route('/holidays', methods=['POST'])
def get_holidays():
    data = request.json
    year = data.get("year")

    if not year:
        return jsonify({"error": "Year is required."}), 400

    try:
        year = int(year)
    except ValueError:
        return jsonify({"error": "Invalid year format. Please provide a valid year (e.g., 2023)."}), 400

    # Generate holidays for the specified year
    holidays = {
        holiday["name"]: holiday["rule"](year).strftime("%Y-%m-%d")
        for holiday in FEDERAL_HOLIDAYS
    }

    return jsonify({"year": year, "holidays": holidays})

if __name__ == "__main__":
    print("Starting Holiday Calendar Microservice on port 5004...")
    app.run(host='0.0.0.0', port=5004, debug=True)