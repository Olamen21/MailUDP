import socket
import os
import threading
import tkinter as tk
import bcrypt
from tkinter import Listbox

SERVER_HOST = "localhost"
SERVER_PORT = 1233
BUFFER_SIZE = 1024
PATH_TO_SAVE = "mails"


# Function to update the user list in the GUI
def update_user_list():
    users = os.listdir(PATH_TO_SAVE)  # List all directories (users)
    user_listbox.delete(0, tk.END)  # Clear the Listbox
    for user in users:
        user_listbox.insert(tk.END, user)  # Add users to the Listbox


def handle_client(data, client_address):
    command = data.decode("utf-8").split(":")

    if command[0] == "CREATE_ACCOUNT":
        username = command[1]
        password = command[2].encode("utf-8")
        user_dir = os.path.join(PATH_TO_SAVE, username)

        if os.path.exists(user_dir):  # Kiểm tra username đã tồn tại chưa
            server_socket.sendto(b"USERNAME_EXISTS", client_address)
        else:
            os.makedirs(user_dir, exist_ok=True)
            # Băm mật khẩu trước khi lưu
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            with open(os.path.join(user_dir, "password.txt"), "wb") as f:
                f.write(hashed_password)  # Lưu mật khẩu đã băm
            with open(os.path.join(user_dir, "new_email.txt"), "w") as f:
                f.write(
                    "Thank you for using this service. We hope that you will feel comfortable."
                )
            server_socket.sendto(b"Account created successfully.", client_address)
            # Update the user list in the GUI when a new account is created
            update_user_list()
    elif command[0] == "LOGIN":
        username = command[1]
        password = command[2].encode("utf-8")
        user_dir = os.path.join(PATH_TO_SAVE, username)
        password_file = os.path.join(user_dir, "password.txt")
        if not os.path.exists(user_dir):
            server_socket.sendto(b"USER_NOT_FOUND", client_address)
        else:
            with open(password_file, "rb") as f:
                stored_hashed_password = f.read()

            if bcrypt.checkpw(password, stored_hashed_password):  # So sánh mật khẩu đã mã hóa
                server_socket.sendto(b"LOGIN_SUCCESS", client_address)
            else:
                server_socket.sendto(b"INVALID_PASSWORD", client_address)



    elif command[0] == "SEND_EMAIL":
        username = command[1]
        email_content = command[2]
        sending_user = command[3]

        user_dir = os.path.join(PATH_TO_SAVE, username)
        filename = os.path.join(
            user_dir, f"email_{len(os.listdir(user_dir)) + 1}_from_{sending_user}.txt"
        )

        with open(filename, "w") as f:
            f.write(email_content)
        server_socket.sendto(b"Email sent successfully.", client_address)

    elif command[0] == "GET_EMAILS":
        username = command[1]
        user_dir = os.path.join(PATH_TO_SAVE, username)

        files = os.listdir(user_dir)
        files_list = ", ".join(files).encode("utf-8")
        server_socket.sendto(files_list, client_address)

    elif command[0] == "READ_EMAIL":
        username = command[1]
        email_filename = command[2]
        user_dir = os.path.join(PATH_TO_SAVE, username)
        email_path = os.path.join(user_dir, email_filename)

        if os.path.exists(email_path):
            with open(email_path, "r") as f:
                email_content = f.read()
            server_socket.sendto(email_content.encode("utf-8"), client_address)
        else:
            server_socket.sendto(b"Email not found.", client_address)


# Function to start the server in a separate thread
def start_server():
    print("Mail Server is running...")

    while True:
        # Receive data from a client
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)

        # Handle each client request in a separate thread
        client_thread = threading.Thread(
            target=handle_client, args=(data, client_address)
        )
        client_thread.start()


# Initialize Tkinter for GUI
root = tk.Tk()
root.title("Mail Server Interface")

# Create a listbox to display users
user_listbox = Listbox(root, width=50, height=20)
user_listbox.pack()

# Create a button to manually refresh the user list
refresh_button = tk.Button(root, text="Refresh User List", command=update_user_list)
refresh_button.pack()

# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))

# Start the server in a separate thread so the GUI remains responsive
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True  # Ensure the thread will close when the main program ends
server_thread.start()

# Load the current list of users when the program starts
update_user_list()

# Start the Tkinter main loop
root.mainloop()
