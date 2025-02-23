import zmq
import json

def request_tip(request_message):
    """ Sends a request to the microservice and returns the response. """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:1234")  
    
    socket.send_string(request_message) 
    response = socket.recv_string()  
    return json.loads(response)  

if __name__ == "__main__":
    print("Running Tests for Tip of the Day Microservice")

    # Test 1: Normal request
    print("\nTEST 1: Requesting a Tip")
    response = request_tip("get")
    print("Received:", response)

    # Test 2: Invalid request
    print("\nTEST 2: Sending an Invalid Request")
    response = request_tip("invalid")
    print("Received:", response)

