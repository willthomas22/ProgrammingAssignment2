# ProgrammingAssignment2
Programming Assignment 2
Elliot Warner, William Thomas, Braden Hayes

To run the server:
python server.py

You should see:
Server listening on localhost:9999

In a separate terminal, run:
python client.py

You will be prompted:
Enter server IP (default: localhost):
Enter server port (default: 9999):

Client Commands:
  Join a message board:
    JOIN|username

    Example:
      JOIN|Tom

  Post to the message board:
    POST|subject|body

    Example:
      POST|Homework|Can someone explain question 3?

  List all users:
    USERS

  Get a specific message by ID:
    MESSAGE|id

    Example:
      MESSAGE|3

  Leave a message board:
    LEAVE
