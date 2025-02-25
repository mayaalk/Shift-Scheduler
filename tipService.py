import zmq
import json
import random

TIPS = [
    "Stay positive and work hard!",
    "Take short breaks to stay productive.",
    "Always communicate clearly with your team.",
    "Organize your tasks to reduce stress.",
    "Don't forget to celebrate small wins!",
    "Believe in yourself and your team!",
    "Success comes from consistent effort!"
]

context = zmq.Context()
socket = context.socket(zmq.REP)  
socket.bind("tcp://*:1234")  

print("Tip of the Day Microservice is running...")

while True:
    message = socket.recv_string()
    print(f"Received request: {message}")

    if message.lower() == "get":
        response = json.dumps({"tip": random.choice(TIPS)})
    else:
        response = json.dumps({"error": "Invalid request"})

    socket.send_string(response)
    

