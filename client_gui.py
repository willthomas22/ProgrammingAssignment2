import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import datetime

class BulletinBoardClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulletin Board Client")
        self.root.geometry("1000x700")

        self.client_socket = None
        self.username = None
        self.is_connected = False
        self.receive_thread = None
        
        self.available_groups = []
        self.joined_groups = []
        self.current_view_group = None # None means Main Board

        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.create_login_screen()

    def create_login_screen(self):
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(self.login_frame, text="Server Host:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.host_entry = ttk.Entry(self.login_frame)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.login_frame, text="Server Port:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.port_entry = ttk.Entry(self.login_frame)
        self.port_entry.insert(0, "9999")
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.login_frame, text="Username:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=2, column=1, padx=5, pady=5)

        self.join_button = ttk.Button(self.login_frame, text="Join", command=self.connect_and_join)
        self.join_button.grid(row=3, column=0, columnspan=2, pady=20)

    def create_main_screen(self):
        self.login_frame.destroy()

        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Left Sidebar (Users and Groups)
        self.left_panel = ttk.Frame(self.main_container, width=250)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))

        # Users
        ttk.Label(self.left_panel, text="Online Users", font=("Arial", 12, "bold")).pack(pady=(0, 5))
        self.user_listbox = tk.Listbox(self.left_panel, height=10)
        self.user_listbox.pack(fill="x", pady=(0, 10))

        # Groups
        ttk.Label(self.left_panel, text="Groups", font=("Arial", 12, "bold")).pack(pady=(0, 5))
        self.group_listbox = tk.Listbox(self.left_panel, height=10)
        self.group_listbox.pack(fill="x", pady=(0, 5))
        
        btn_frame = ttk.Frame(self.left_panel)
        btn_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(btn_frame, text="Join Group", command=self.join_selected_group).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(btn_frame, text="Leave Group", command=self.leave_selected_group).pack(side="left", fill="x", expand=True, padx=2)
        
        ttk.Button(self.left_panel, text="Refresh Lists", command=self.refresh_lists).pack(fill="x")

        # Right Panel
        self.right_panel = ttk.Frame(self.main_container)
        self.right_panel.pack(side="right", fill="both", expand=True)

        # View Selector
        self.view_label = ttk.Label(self.right_panel, text="Viewing: Main Board", font=("Arial", 14, "bold"))
        self.view_label.pack(anchor="w", pady=(0, 10))

        # Message List (Treeview)
        columns = ("id", "sender", "date", "subject", "group")
        self.msg_tree = ttk.Treeview(self.right_panel, columns=columns, show="headings", height=15)
        self.msg_tree.heading("id", text="ID")
        self.msg_tree.column("id", width=50)
        self.msg_tree.heading("sender", text="Sender")
        self.msg_tree.column("sender", width=100)
        self.msg_tree.heading("date", text="Date")
        self.msg_tree.column("date", width=150)
        self.msg_tree.heading("subject", text="Subject")
        self.msg_tree.column("subject", width=300)
        self.msg_tree.heading("group", text="Group")
        self.msg_tree.column("group", width=80)
        
        self.msg_tree.pack(fill="both", expand=True, pady=(0, 10))
        self.msg_tree.bind("<<TreeviewSelect>>", self.on_message_select)

        # Message Body View
        ttk.Label(self.right_panel, text="Message Content", font=("Arial", 10, "bold")).pack(anchor="w")
        self.msg_body_text = scrolledtext.ScrolledText(self.right_panel, height=6, state="disabled")
        self.msg_body_text.pack(fill="x", pady=(0, 10))

        # Post Area
        self.post_frame = ttk.LabelFrame(self.right_panel, text="Post New Message", padding="10")
        self.post_frame.pack(fill="x")

        # Target Group Selection
        ttk.Label(self.post_frame, text="Post To:").grid(row=0, column=0, sticky="e", padx=5)
        self.post_target = ttk.Combobox(self.post_frame, state="readonly", width=47)
        self.post_target['values'] = ["Main Board"]
        self.post_target.current(0)
        self.post_target.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(self.post_frame, text="Subject:").grid(row=1, column=0, sticky="e", padx=5)
        self.post_subject = ttk.Entry(self.post_frame, width=50)
        self.post_subject.grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(self.post_frame, text="Body:").grid(row=2, column=0, sticky="ne", padx=5, pady=5)
        self.post_body = tk.Text(self.post_frame, height=3, width=50)
        self.post_body.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        self.post_btn = ttk.Button(self.post_frame, text="Post", command=self.post_message)
        self.post_btn.grid(row=3, column=1, sticky="e", padx=5)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")

        # Initial data fetch
        self.refresh_lists()

    def connect_and_join(self):
        host = self.host_entry.get()
        try:
            port = int(self.port_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return

        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Username cannot be empty")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            
            # Send JOIN command
            self.client_socket.send(f"JOIN|{username}\n".encode())
            self.username = username
            self.is_connected = True
            
            # Start receiving thread
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()

            self.create_main_screen()
            self.status_var.set(f"Connected as {username}")

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def receive_messages(self):
        buffer = ""
        while self.is_connected:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    self.root.after(0, self.handle_disconnect)
                    break
                
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.root.after(0, lambda l=line: self.process_message(l))
            except:
                self.root.after(0, self.handle_disconnect)
                break

    def process_message(self, message):
        if not message: return
        parts = message.split("|")
        command = parts[0].strip()

        if command == "MESSAGE":
            # Format 1 (Old/Join): MESSAGE | id | sender | date | subject | body
            # Format 2 (New): MESSAGE | id | sender | date | subject | body | group_id
            
            if len(parts) >= 6:
                msg_id = parts[1].strip()
                sender = parts[2].strip()
                date = parts[3].strip()
                subject = parts[4].strip()
                
                # Determine if we have a group_id
                # The server sends group_id as the LAST element.
                
                # Let's check the number of parts.
                # We can pop the last element if it looks like a group ID
                raw_body_and_group = "|".join(parts[5:])
                
                # Check if the message ends with " | <group_id>" or " | None"

                group_id = "Main"
                body = raw_body_and_group
                
                # Try to extract group ID from the end
                last_pipe_index = raw_body_and_group.rfind("|")
                if last_pipe_index != -1:
                    potential_group = raw_body_and_group[last_pipe_index+1:].strip()
                    potential_body = raw_body_and_group[:last_pipe_index].strip()
                    
                    if potential_group == "None":
                        group_id = "Main"
                        body = potential_body
                    elif potential_group.isdigit():
                        group_id = f"Group {potential_group}"
                        body = potential_body
                    else:
                        # Maybe it's the old format or body contains pipes and ends with text
                        # If it's the JOIN history message (line 61 in server), it has NO group_id at the end.
                        # So raw_body_and_group IS the body.
                        pass
                
                # Insert into Treeview
                self.msg_tree.insert("", 0, iid=msg_id, values=(msg_id, sender, date, subject, group_id))
                
                if not hasattr(self, 'message_bodies'):
                    self.message_bodies = {}
                self.message_bodies[msg_id] = body

        elif command == "USERS":
            if len(parts) > 1:
                users = parts[1].strip().split(",")
                self.user_listbox.delete(0, tk.END)
                for user in users:
                    if user:
                        self.user_listbox.insert(tk.END, user)

        elif command == "GROUPS":
            # GROUPS | 1 2 3 4 5
            if len(parts) > 1:
                groups_str = parts[1].strip()
                if groups_str:
                    self.available_groups = groups_str.split(" ")
                    self.group_listbox.delete(0, tk.END)
                    for grp in self.available_groups:
                        display = f"Group {grp}"
                        if grp in self.joined_groups:
                            display += " (Joined)"
                        self.group_listbox.insert(tk.END, display)
                    
                    # Update Post Target Combobox
                    targets = ["Main Board"] + [f"Group {g}" for g in self.joined_groups]
                    self.post_target['values'] = targets
                    if self.post_target.get() not in targets:
                        self.post_target.current(0)

        elif command == "SERVER":
            msg = parts[1].strip()
            self.status_var.set(msg)
            if "joined" in msg or "left" in msg:
                self.refresh_lists()

        elif command == "ERROR":
            if len(parts) > 1:
                messagebox.showerror("Server Error", parts[1].strip())
        
        # Handle group join/leave confirmations if server sends them as simple text or specific commands
        
        else:
            # Check for specific success messages that aren't prefixed
            if "Has Joined group" in message:
                # Refresh groups to show (Joined) status
                # We need to know WHICH group was joined to update local state if we want to be precise,
                # but refreshing lists is safer.
                # Extract group ID
                try:
                    grp = message.strip().split(" ")[-1]
                    if grp not in self.joined_groups:
                        self.joined_groups.append(grp)
                    self.refresh_lists()
                except:
                    pass
            elif "Has Left group" in message:
                try:
                    grp = message.strip().split(" ")[-1]
                    if grp in self.joined_groups:
                        self.joined_groups.remove(grp)
                    self.refresh_lists()
                except:
                    pass

    def refresh_lists(self):
        self.send_command("USERS")
        self.send_command("GROUPS")

    def join_selected_group(self):
        selection = self.group_listbox.curselection()
        if not selection:
            return
        
        grp_idx = selection[0]
        grp_id = self.available_groups[grp_idx]
        
        if grp_id in self.joined_groups:
            messagebox.showinfo("Info", f"Already in Group {grp_id}")
            return
            
        self.send_command(f"GROUPJOIN|{grp_id}")

    def leave_selected_group(self):
        selection = self.group_listbox.curselection()
        if not selection:
            return
        
        grp_idx = selection[0]
        grp_id = self.available_groups[grp_idx]
        
        if grp_id not in self.joined_groups:
            messagebox.showinfo("Info", f"Not a member of Group {grp_id}")
            return
            
        self.send_command(f"GROUPLEAVE|{grp_id}")

    def post_message(self):
        subject = self.post_subject.get().strip()
        body = self.post_body.get("1.0", tk.END).strip()
        target = self.post_target.get()
        
        if not subject or not body:
            messagebox.showwarning("Input Error", "Subject and Body are required.")
            return

        if target == "Main Board":
            self.send_command(f"POST|{subject}|{body}")
        else:
            # Target format "Group X"
            grp_id = target.split(" ")[1]
            self.send_command(f"GROUPPOST|{grp_id}|{subject}|{body}")
            
        self.post_subject.delete(0, tk.END)
        self.post_body.delete("1.0", tk.END)

    def on_message_select(self, event):
        selected_items = self.msg_tree.selection()
        if selected_items:
            msg_id = selected_items[0]
            if hasattr(self, 'message_bodies') and msg_id in self.message_bodies:
                body = self.message_bodies[msg_id]
                self.msg_body_text.config(state="normal")
                self.msg_body_text.delete("1.0", tk.END)
                self.msg_body_text.insert("1.0", body)
                self.msg_body_text.config(state="disabled")

    def send_command(self, cmd):
        if self.client_socket:
            try:
                self.client_socket.send(f"{cmd}\n".encode())
            except:
                self.handle_disconnect()

    def handle_disconnect(self):
        if self.is_connected:
            self.is_connected = False
            messagebox.showinfo("Disconnected", "Disconnected from server.")
            self.root.quit()

    def on_closing(self):
        if self.is_connected:
            self.send_command("LEAVE")
            self.is_connected = False
            if self.client_socket:
                self.client_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client = BulletinBoardClient(root)
    root.protocol("WM_DELETE_WINDOW", client.on_closing)
    root.mainloop()
