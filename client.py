import os
import socket

# Set the server's host
HOST = "127.0.0.1"  # localhost

def setup_client(port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, port))
    print(f"Connected to the server on port {port}...")
    return client_socket

def send_message(client_socket, message):
    client_socket.send(message.encode())
    if message != "SHUTDOWN_SERVER":
        response = client_socket.recv(1024).decode()
        return response

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu():
    print("=== Element Card Game ===")
    print("      Main Menu       ")
    print("----------------------")
    print("1: Play")
    print("2: Cards")
    print("3: Stats")
    print("4: Quit")
    print("5: Shutdown Server")
    print("----------------------")

def main():
    port = int(input("Enter the port number to connect to: "))
    client_socket = setup_client(port)
    response = send_message(client_socket, "GET_CARDS")  # Request current cards from the server

    while True:
        clear_screen()
        display_menu()

        # Process user input
        choice = input("Enter your choice (1, 2, 3, 4, or 5): ")
        if choice == "1":
            clear_screen()
            print(response)  # Display current cards
            # Prompt the user to input two cards to combine
            card1 = input("Enter the first card: ")
            card2 = input("Enter the second card: ")
            combine_request = f"COMBINE {card1} {card2}"
            response = send_message(client_socket, combine_request)
            print(response)
            input("Press Enter to continue... ")
            response = send_message(client_socket, "GET_CARDS")  # Request current cards from the server
            if response.startswith("New card unlocked"):
                print(response)
                input("Press Enter to continue... ")
                # Refresh the response to display current cards
                response = send_message(client_socket, "GET_CARDS")
        elif choice == "2":
            clear_screen()
            # Request current unlocked cards from the server
            response = send_message(client_socket, "GET_CARDS")
            if response.startswith("Current Cards:"):
                print(response)
                input("Press Enter to continue... ")
            else:
                print("Unexpected server response. Exiting...")
                client_socket.close()
                break
        elif choice == "3":
            clear_screen()
            # Request stats from the server
            response = send_message(client_socket, "GET_STATS")
            print(response)
            input("Press Enter to continue... ")
            # Request current unlocked cards from the server
            response = send_message(client_socket, "GET_CARDS")
        elif choice == "4":
            print("Exiting game")
            send_message(client_socket, "QUIT_GAME")
            break
        elif choice == "5":
            print("Requesting server shutdown...")
            send_message(client_socket, "SHUTDOWN_SERVER")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

    # Close the client socket
    client_socket.close()

if __name__ == "__main__":
    main()
