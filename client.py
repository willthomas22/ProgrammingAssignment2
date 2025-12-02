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
    print("\nCommands:\n" \
    "1. JOIN|<username> - Join the message board\n" \
    "2. POST|<subject>|<body> - Send a message\n" \
    "3. USERS - List users\n" \
    "4. MESSAGE|<message_id> - Get a specific message\n" \
    "5. GROUPS - List Groups\n"  \
    "6. GROUPJOIN|<group_id> - Join a private group\n" \
    "7. GROUPPOST|<group_id>|<subject>|<body> - Post to a private group\n" \
    "8. GROUPUSERS|<group_id> - List private group users\n" \
    "9. GROUPLEAVE|<group_id> - Leave a private group\n" \
    "10. GROUPMESSAGE|<group_id>|<message_id> - List private group messages\n" \
    "11. LEAVE - Leave chat")
    while True:
        command = input("Enter command: ").strip()

        # This sends the command to have a user join
        if command.upper().startswith("JOIN") and not joined:
            client_socket.send(f"{command}\n".encode())
            joined = True

        elif (command.upper().startswith("GROUPJOIN")
            or command.upper().startswith("GROUPPOST")
            or command.upper().startswith("GROUPUSERS")
            or command.upper().startswith("GROUPLEAVE")
            or command.upper().startswith("GROUPMESSAGE")) and not joined:
            print("You Must Join the General Chat First.") 
            continue

        # This Tells the user that they have already joined
        elif command.upper().startswith("JOIN") and joined:
            print("You have already joined the chat.") 
            continue
            
        # This handles the user leaving the chat
        elif command.upper() == "LEAVE":
            client_socket.send("LEAVE\n".encode())
            break

        #This sends all other commands to the server
        client_socket.send(f"{command}\n".encode())  # Send command to server

    # Closes the client socket
    client_socket.close()


if __name__ == "__main__":
    main()