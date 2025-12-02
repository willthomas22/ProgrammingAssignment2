import socket
import threading    
import datetime

clients = []
client_groups = {}
messages = []
client_names = {}
message_id = 0
rooms = [1,2,3,4,5]

lock = threading.Lock()
message_id_lock = threading.Lock()

# Broadcast message to all connected clients
def broadcast_message(message):
    for client in clients:  
        try:
            client.send(message)
        except:
            pass

# This will check if a client is in a that private room and send them the message
def group_message(message, room):
    for client in clients:
        try:
            if room in client_groups.get(client, []):
                client.send(message)
        except:
            pass

def handle_client(client_socket):
    global message_id
    username = None

    while True:
        try:
            data = client_socket.recv(1024).decode().strip()    # Receive data from client
            if not data:
                break

            split = data.split('|') # Split command and arguments
            command = split[0].upper()

            if command == "JOIN":   # Command to join the chat
                username = split[1]

                if username in client_names.values():   # Check for unique username
                    client_socket.send("ERROR | Username already taken.\n".encode())
                    continue

                with lock:
                    client_names[client_socket] = username  # Register username
                    client_groups[client_socket] = [] # Making a blank list of groups for client
                    
                welcome_message = f"SERVER | {username} has joined the chat.\n"
                broadcast_message(welcome_message.encode()) # Notify all clients

                last_messages = messages[-2:] # Send last 2 messages to the new client
                for msg in last_messages:
                    client_socket.send(f"MESSAGE | {msg['id']} | {msg['sender']} | {msg['date']} | {msg['subject']} | {msg['body']}\n".encode())

            elif command == "POST":  # Command to post a message
                if username is None:    # Ensure user has joined
                    client_socket.send("ERROR | You must join first.\n".encode())
                    continue

                subject = split[1]  # Extract subject and body
                body = split[2]
                group_id = None # General chat has no group ID

                with message_id_lock:
                    message_id += 1 # Increment message ID
                    msg = {"id": message_id, "sender": username, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "subject": subject, "body": body, "group_id": group_id}    # Create message dictionary
                    
                    with lock:
                        messages.append(msg)    # Store post

                    broadcast_message(f"MESSAGE | {msg['id']} | {msg['sender']} | {msg['date']} | {msg['subject']} | {msg['body']} | {msg['group_id']}\n".encode())   # Broadcast message to all clients
            
            elif command == "MESSAGE":  # Command to get a specific message
                if username is None:    # Ensure user has joined
                    client_socket.send("ERROR | You must join first.\n".encode())
                    continue
                
                msg_id = int(split[1])   # Extract message ID
                with lock:
                    msg = next((m for m in messages if m["id"] == msg_id), None)  # Find message by ID

                if msg:
                    client_socket.send(f"MESSAGE | {msg['id']} | {msg['sender']} | {msg['date']} | {msg['subject']} | {msg['body']}\n".encode()) # Send message to client
                else:
                    client_socket.send("ERROR | Message not found.\n".encode())

            elif command == "USERS":    # Command to list users
                with lock:
                    user_list = ",".join(client_names.values())
                client_socket.send(f"USERS | {user_list}\n".encode()) # Send user list to client
    
            elif command == "LEAVE": # Command to leave chat
                break
            
            elif command == "GROUPS":
                client_socket.send(f"GROUPS | {' '.join(map(str, rooms))}\n".encode())
            
            elif command == "GROUPJOIN":
                client_groups[client_socket].append(int(split[1]))
                client_socket.send(f"{client_names[client_socket]} Has Joined group {split[1]}\n".encode())

            elif command == "GROUPPOST":
                if int(split[1]) not in client_groups[client_socket]:
                    client_socket.send("ERROR | You are not in this group.\n".encode())
                else:
                    group_id = int(split[1]) # Get group ID and convert it to int
                    subject = split[2]  # Extract subject and body
                    body = split[3] # Get body of text

                    with message_id_lock:
                        message_id += 1 # Increment message ID
                        msg = {"id": message_id, "sender": client_names[client_socket], "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "subject": subject, "body": body, "group_id": group_id}    # Create message dictionary
                        
                        with lock:
                            messages.append(msg)    # Store post

                        group_message(f"MESSAGE | {msg['id']} | {msg['sender']} | {msg['date']} | {msg['subject']} | {msg['body']} | {msg['group_id']}\n".encode(), group_id)   # Broadcast message to all clients
            
            elif command == "GROUPUSERS":
                group_id = int(split[1]) # Get the group ID for the user check
                with lock:
                    group_user_list = ",".join(
                        [client_names[client] for client in clients if group_id in client_groups.get(client, [])])
                client_socket.send(f"USERS | {group_user_list}\n".encode())

            elif command == "GROUPLEAVE":
                group_id = int(split[1]) # Get the group ID to leave
                if group_id in client_groups[client_socket]:
                    client_groups[client_socket].remove(group_id)
                    client_socket.send(f"{client_names[client_socket]} Has Left group {split[1]}\n".encode())
                else:
                    client_socket.send("ERROR | You are not in this group.\n".encode())

            elif command == "GROUPMESSAGE":
                group_id = int(split[1]) # Get the group ID for message listing
                msg_id = int(split[2])   # Extract message ID
                with lock:
                    group_msg = next((m for m in messages if m.get("group_id") == group_id and m["id"] == msg_id), None) # Find the message
                if group_msg:
                    client_socket.send(f"MESSAGE | {msg['id']} | {msg['sender']} | {msg['date']} | {msg['subject']} | {msg['body']} {msg['group_id']}\n".encode())
                else:
                    client_socket.send("ERROR | Message not found.\n".encode())

            else:   # Unknown command
                client_socket.send("ERROR | Unknown command.\n".encode())
        
        except Exception as e:  
            print(f"Error: {e}")    
            break

    if username:    # Handle client disconnection
        with lock:
            del client_names[client_socket]

        leave_message = f"SERVER | {username} has left the chat.\n"
        broadcast_message(leave_message.encode())

    with lock:
        if client_socket in clients:
            clients.remove(client_socket)

    client_socket.close()


def main():
    host = 'localhost'  # Server host
    port = 9999 # Server port

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket
    server.bind((host, port))   # Bind socket to address
    server.listen() # Listen for incoming connections

    print(f"Server listening on {host}:{port}") 

    while True: # Accept new client connections
        client_socket, addr = server.accept()
        print(f"New connection: {addr}")

        with lock:
            clients.append(client_socket)

        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()
    

if __name__ == "__main__":
    main()