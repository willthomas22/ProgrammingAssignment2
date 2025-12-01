import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode()    # Receive data from server
            if not data:
                print("Disconnected from server.")
                break

            print(data.strip())  # Print received message to console

        except:
            break

def main():
    host = input("Enter server IP (default: localhost): ") or "localhost"
    port = int(input("Enter server port (default: 9999): ") or 9999)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    print("Connected to chat server.")

    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    joined = False
    print("\nCommands:\n1. JOIN|<username> - Join the message board\n2. POST|<subject>|<body> - Send a message\n3. USERS - List users\n4. MESSAGE|<message_id> - Get a specific message\n5. LEAVE - Leave chat")
    while True:
        command = input("Enter command: ").strip()

        if command.upper().startswith("JOIN") and not joined:
            client_socket.send(f"{command}\n".encode())
            joined = True

        elif command.upper().startswith("JOIN") and joined:
            print("You have already joined the chat.") 
            continue
            
        elif command.upper() == "LEAVE":
            client_socket.send("LEAVE\n".encode())
            break

        client_socket.send(f"{command}\n".encode())  # Send command to server

    client_socket.close()


if __name__ == "__main__":
    main()