from flask import Flask, request, jsonify
import os
import webbrowser
import threading

app = Flask(__name__)

# Helper function to save notification as an HTML file
def save_notification_as_html(recipient_name, subject, body):
    try:
        # Create the HTML content for the notification
        html_content = f"""
        <html>
            <head>
                <title>{subject}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        padding: 20px;
                    }}
                    .notification {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    h1 {{
                        color: #333;
                    }}
                    p {{
                        color: #555;
                    }}
                </style>
            </head>
            <body>
                <div class="notification">
                    <h1>{subject}</h1>
                    <p>{body}</p>
                </div>
            </body>
        </html>
        """

        # Save the HTML content to a file
        file_name = f"notification_to_{recipient_name.replace(' ', '_')}.html"
        with open(file_name, "w") as file:
            file.write(html_content)

        print(f"Notification saved as {file_name}.")
        return file_name
    except Exception as e:
        print(f"Error creating notification HTML file: {e}")
        return None

@app.route('/notify', methods=['POST'])
def notify():
    try:
        data = request.json
        event_type = data.get("event_type")

        if not event_type:
            return jsonify({"error": "Event type is required."}), 400

        if event_type == "shift_reminder":
            # Generate shift reminder notification
            recipient_name = data.get("employee_name", "Employee")
            shift_date = data.get("shift_date", "Unknown date")
            shift_time = data.get("shift_time", "Unknown time")

            subject = "Shift Reminder"
            body = f"Hello {recipient_name},\n\nYou have a shift scheduled for {shift_date} at {shift_time}.\n\nThank you!"
            
            # Create and open the notification in a separate thread to avoid blocking
            def open_notification():
                file_name = save_notification_as_html(recipient_name, subject, body)
                if file_name:
                    webbrowser.open('file://' + os.path.realpath(file_name))
            
            threading.Thread(target=open_notification).start()
            
            return jsonify({"message": "Notification sent successfully."}), 200

        elif event_type == "shift_cancellation":
            # Generate shift cancellation notification
            recipient_name = data.get("employee_name", "Employee")
            shift_date = data.get("shift_date", "Unknown date")
            shift_time = data.get("shift_time", "Unknown time")

            subject = "Shift Cancellation"
            body = f"Hello {recipient_name},\n\nYour shift scheduled for {shift_date} at {shift_time} has been canceled.\n\nThank you!"
            
            def open_notification():
                file_name = save_notification_as_html(recipient_name, subject, body)
                if file_name:
                    webbrowser.open('file://' + os.path.realpath(file_name))
            
            threading.Thread(target=open_notification).start()
            
            return jsonify({"message": "Notification sent successfully."}), 200

        elif event_type == "no_show":
            # Generate no-show alert notification
            recipient_name = data.get("manager_name", "Manager")
            employee_name = data.get("employee_name", "Unknown employee")
            shift_date = data.get("shift_date", "Unknown date")
            shift_time = data.get("shift_time", "Unknown time")

            subject = "No-Show Alert"
            body = f"""
            <div style="color: #d32f2f; font-weight: bold;">URGENT: EMPLOYEE NO-SHOW</div>
            <p>Hello {recipient_name},</p>
            <p>{employee_name} did not show up for their scheduled shift on {shift_date} at {shift_time}.</p>
            <p>Please take appropriate action as soon as possible.</p>
            <hr>
            <p style="font-size: 0.9em; color: #666;">
                Recommended actions:
                <ul>
                    <li>Attempt to contact {employee_name}</li>
                    <li>Find a replacement if possible</li>
                    <li>Document the incident</li>
                    <li>Follow up according to company policy</li>
                </ul>
            </p>
            """

            def open_notification():
                file_name = save_notification_as_html(recipient_name, subject, body)
                if file_name:
                    webbrowser.open('file://' + os.path.realpath(file_name))
            
            threading.Thread(target=open_notification).start()
            
            return jsonify({"message": "No-show notification sent successfully."}), 200

        else:
            return jsonify({"error": "Unsupported event type."}), 400

    except Exception as e:
        print(f"Error processing notification: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    print("Starting Notification Microservice on port 5002...")
    print("To exit, press Ctrl+C")
    app.run(host='0.0.0.0', port=5002, debug=True)
