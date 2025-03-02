import socket
import os
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

BUFFER_SIZE = 1024
PATH_TO_SAVE = "mails"
server_socket = None

# Function to log messages with timestamps
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, f"[{timestamp}]:  {message}\n")
    log_text.config(state=tk.DISABLED)
    log_text.yview(tk.END)

def handle_client(data, client_address):
    command = data.decode("utf-8").split(":")
    global server_socket

    if command[0] == "CREATE_ACCOUNT":
        username = command[1]
        user_dir = os.path.join(PATH_TO_SAVE, username)
        os.makedirs(user_dir, exist_ok=True)

        with open(os.path.join(user_dir, "new_email.txt"), "w") as f:
            f.write("Welcome! Your account has been created successfully.")

        server_socket.sendto(b"Account created successfully.", client_address)
        log_message(f"Account created for user: {username}")

    elif command[0] == "SEND_EMAIL":
        username = command[1]
        email_content = command[2]
        sending_user = command[3]

        user_dir = os.path.join(PATH_TO_SAVE, username)
        filename = os.path.join(user_dir, f"email_{len(os.listdir(user_dir)) + 1}_from_{sending_user}.txt")

        with open(filename, "w") as f:
            f.write(email_content)
        server_socket.sendto(b"Email sent successfully.", client_address)
        log_message(f"Email sent from {sending_user} to {username}")

    elif command[0] == "GET_EMAILS":
        username = command[1]
        user_dir = os.path.join(PATH_TO_SAVE, username)
        files = os.listdir(user_dir)
        files_list = ", ".join(files).encode("utf-8")
        server_socket.sendto(files_list, client_address)
        log_message(f"Sent email list to {username}")

    elif command[0] == "READ_EMAIL":
        username = command[1]
        email_filename = command[2]
        user_dir = os.path.join(PATH_TO_SAVE, username)
        email_path = os.path.join(user_dir, email_filename)

        if os.path.exists(email_path):
            with open(email_path, "r") as f:
                email_content = f.read()
            server_socket.sendto(email_content.encode("utf-8"), client_address)
            log_message(f"Email {email_filename} read by {username}")
        else:
            server_socket.sendto(b"Email not found.", client_address)
            log_message(f"Email {email_filename} not found for {username}")

# Function to start the server
def start_server():
    global server_socket
    port = int(port_entry.get())
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("localhost", port))
    log_message(f"Mail Server started on port {port}")

    while True:
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        threading.Thread(target=handle_client, args=(data, client_address)).start()

# Function to switch to the log view
def switch_to_log_view():
    start_frame.pack_forget()
    root.geometry("800x300")
    log_frame.pack(fill=tk.BOTH, expand=True)
    threading.Thread(target=start_server, daemon=True).start()

# Initialize Tkinter
root = tk.Tk()
root.title("Mail Server")
root.geometry("400x130")
root.eval('tk::PlaceWindow . center')  # Center window on screen

# Frame for initial UI (Port entry and Start button)
start_frame = tk.Frame(root)
start_frame.pack(pady=20)

label = tk.Label(start_frame, text="Enter Port:", font=("Arial", 14))
label.grid(row=0, column=0, padx=10, pady=5)

port_entry = tk.Entry(start_frame, width=15, font=("Arial", 14))
port_entry.grid(row=0, column=1, padx=10, pady=5)
port_entry.insert(0, "1233")

start_button = tk.Button(start_frame, text="Start Server", command=switch_to_log_view, font=("Arial", 14), bg="lightblue")
start_button.grid(row=1, column=0, columnspan=2, pady=10)

# Frame for server logs
log_frame = tk.Frame(root)
log_text = scrolledtext.ScrolledText(log_frame, width=90, height=25, font=("Arial", 14), state=tk.DISABLED)
log_text.pack(padx=10, pady=10)

root.mainloop()