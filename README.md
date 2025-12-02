# ProgrammingAssignment2
Programming Assignment 2
Elliot Warner, William Thomas, Braden Hayes

To run the server:
python server.py

You should see:
Server listening on localhost:9999

In a separate terminal, run:
python client.py

If you would like to run the GUI:
After you have run the server go to the client_gui.py file and run it

You will be prompted: (You can click enter through both to take the default values)
Enter server IP (default: localhost):
Enter server port (default: 9999):

Client Commands:
  Join a message board:
    JOIN|username

    Example:
      JOIN|Tom

  Join a group message Board
    GROUPJOIN|group_id

    Exmaple:
      GROUPJOIN|1
  
  Post to the message board:
    POST|subject|body

    Example:
      POST|Homework|Can someone explain question 3?

  Post to a group message board:
    POST|group_id|subject|body

    Example:
      POST|1|Networks Class|Itsn't this class the best???

  List all users:
    USERS

  List all group users:
    GROUPUSERS|group_id

    Example:
      GROUPUSERS|1

  Get a specific message by ID:
    MESSAGE|message_id

    Example:
      MESSAGE|3
  
  Get a specifiic group message by id:
    GROUPMESSAGE|group_id|message_id

    Example:
      GROUPMESSAGE|1|1

  Leave a message board:
    LEAVE

  Leave a group message board
    GROUPLEAVE|group_id

    Example:
      GROUPLEAVE|1
