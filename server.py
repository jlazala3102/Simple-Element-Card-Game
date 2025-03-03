import socket
import os
import threading
import random
import signal
import sys  # To exit the program
from card import Card
from game_rules import combination_rules  # Import combination rules
import time

HOST = "127.0.0.1"

# Constants for timeout and shutdown duration
TIMEOUT_DURATION = 2000  #  minutes in seconds
SHUTDOWN_DURATION = 5  # 5 seconds for shutdown delay

# Shared variables for server shutdown and active client count
shutdown_requested = False
active_clients = 0
shutdown_lock = threading.Lock()

# Function to handle the timeout
def timeout_handler(signum, frame):
    print("Server timed out. Shutting down...")
    sys.exit()

# Function to handle the shutdown alarm
def shutdown_alarm_handler():
    print("Server shutdown alarm triggered. Shutting down...")
    # Trigger KeyboardInterrupt
    os.kill(os.getpid(), signal.SIGINT)
    sys.exit()
    

def setup_server():
    # Choose a random port number from the range 1024-65535
    port = random.randint(1024, 65535)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, port))
    server_socket.listen(5)  # Allow up to 5 pending connections
    print(f"Server is listening for incoming connections on port {port}...")  # Print the chosen port number
    return server_socket, port

def combine_elements(element1, element2, unlocked_cards, locked_cards):
    # Check if the combination of element1 and element2 is valid
    combination = combination_rules.get((element1, element2)) or combination_rules.get((element2, element1))
    if combination:
        new_card = Card(combination)
        if str(new_card) in unlocked_cards or str(new_card) in locked_cards:
            return f"{element1} + {element2} has already been combined to create {combination}."
        else:
            unlocked_cards.append(str(new_card))
            return f"New card unlocked: {combination}"
    else:
        return "Invalid combination."

def handle_client(client_socket, initial_cards):
    global shutdown_requested, active_clients
    print("Connected to client:", client_socket.getpeername())
    active_clients += 1

    # List to keep track of unlocked cards
    unlocked_cards = initial_cards.copy()
    
    # Set to keep track of locked cards
    locked_cards = set(initial_cards)

    # Calculate the total number of available cards
    total_cards = len(combination_rules) + len(initial_cards)

    while True:
        # Receive data from the client
        data = client_socket.recv(1024).decode()
        print("Received:", data)

        # Check if client wants to quit
        if data == "QUIT_GAME":
            print("Client requested to quit. Exiting...")
            break

        # Check if client wants to shut down the server
        if data == "SHUTDOWN_SERVER":
            print("Client requested server shutdown. Setting shutdown alarm...")
            with shutdown_lock:
                shutdown_requested = True
            # Set a timer for shutdown duration
            threading.Timer(SHUTDOWN_DURATION, shutdown_alarm_handler).start()
            client_socket.close()
            break

        # Check if client wants to combine elements
        if data.startswith("COMBINE"):
            elements = data.split()[1:]  # Extract elements to be combined
            if len(elements) == 2:
                result = combine_elements(elements[0], elements[1], unlocked_cards, locked_cards)
                client_socket.send(result.encode())
            else:
                client_socket.send("Invalid combination request.".encode())

        # Calculate the score and round it to the nearest hundredth
        score = round(len(unlocked_cards) / total_cards * 100)

        # Send current unlocked cards, score, total card count, and current card number
        # when requested or after successful combination
        if data == "GET_CARDS" or data.startswith("New card unlocked"):
            current_cards = ", ".join(unlocked_cards)
            client_socket.send(f"Current Cards: {current_cards}".encode())
        if data == "GET_STATS":
            client_socket.send(f"Collection Percentage: {score}%\nUnlocked Cards: {len(unlocked_cards)}/{total_cards}".encode())

    # Close the connection
    client_socket.close()
    active_clients -= 1

def main():
    global shutdown_requested, active_clients  # Declare global variables
    # Set up signal handler for timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(TIMEOUT_DURATION)  # Set the initial alarm

    server_socket, port = setup_server()

    # Create initial four cards
    cards = [Card("Water"), Card("Fire"), Card("Earth"), Card("Air")]
    card_types = [str(card) for card in cards]

    while not shutdown_requested or active_clients > 0:
        try:
            client_socket, _ = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, card_types.copy()))
            client_handler.start()  # Start handling the client in a new thread
        except KeyboardInterrupt:
            print("KeyboardInterrupt received. Shutting down...")
            with shutdown_lock:
                shutdown_requested = True
            break  # Exit the loop if KeyboardInterrupt occurs
    server_socket.close()  # Close the server socket

if __name__ == "__main__":
    main()
