import os
import socket
import threading
import bcrypt
import tkinter as tk
from tkinter import Listbox, scrolledtext
from datetime import datetime

BUFFER_SIZE = 1024
PATH_TO_SAVE = "mails"
server_socket = None
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_message(message):

    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, f"[{timestamp}]:  {message}\n")
    log_text.config(state=tk.DISABLED)
    log_text.yview(tk.END)


def handle_client(data, client_address):

    command = data.decode("utf-8").split(":")
    global server_socket

    if command[0] == "CREATE_ACCOUNT":
        username = command[1]
        password = command[2]
        IPAddr = command[3]
        user_dir = os.path.join(PATH_TO_SAVE, username)


        if os.path.exists(user_dir):
            server_socket.sendto(b"USERNAME_EXISTS", client_address)
        else:
            os.makedirs(user_dir, exist_ok=True)
            with open(os.path.join(user_dir, "new_email.txt"), "w") as f:
                f.write(f"Created at: {timestamp}\nUsername: {username}\nPassword: {password}\nIPAddress: {IPAddr}")
            server_socket.sendto(b"Account created successfully.", client_address)
            log_message(f"New account created: {username}")



    elif command[0] == "LOGIN":

        username = command[1]

        password = command[2]

        user_dir = os.path.join(PATH_TO_SAVE, username)

        new_email_file = os.path.join(user_dir, "new_email.txt")

        if not os.path.exists(user_dir):

            server_socket.sendto(b"USER_NOT_FOUND", client_address)

        else:

            try:

                with open(new_email_file, "r", encoding="utf-8") as f:

                    lines = f.readlines()

                # Tìm dòng chứa mật khẩu

                stored_password = None

                for line in lines:

                    if line.startswith("Password: "):  # Tìm dòng chứa password

                        stored_password = line.split("Password: ")[1].strip()

                        break

                if stored_password is None:

                    server_socket.sendto(b"ERROR_READING_PASSWORD", client_address)

                elif password == stored_password:  # So sánh trực tiếp chuỗi mật khẩu

                    server_socket.sendto(b"LOGIN_SUCCESS", client_address)

                    log_message(f"User {username} logged in successfully.")

                else:

                    server_socket.sendto(b"INVALID_PASSWORD", client_address)

            except Exception as e:

                print(f"Error reading password file for {username}: {e}")

                server_socket.sendto(b"ERROR_READING_PASSWORD", client_address)


    elif command[0] == "SEND_EMAIL":
        username = command[1]
        email_content = command[2]
        sending_user = command[3]
        user_dir = os.path.join(PATH_TO_SAVE, username)
        filename = os.path.join(user_dir, f"email_{len(os.listdir(user_dir)) + 1}_from_{sending_user}.txt")

        with open(filename, "w") as f:
            f.write(f"{timestamp}: {email_content}\n from: {sending_user}");
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


def start_server():
    global server_socket
    port = int(port_entry.get())
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("0.0.0.0", port))
    log_message(f"Mail Server started on port {port}")

    while True:
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        threading.Thread(target=handle_client, args=(data, client_address)).start()


def switch_to_log_view():

    start_frame.pack_forget()
    root.geometry("800x300")
    log_frame.pack(fill=tk.BOTH, expand=True)
    threading.Thread(target=start_server, daemon=True).start()


# Giao diện Tkinter
root = tk.Tk()
root.title("Mail Server")
root.geometry("400x130")
root.eval('tk::PlaceWindow . center')

# Giao diện nhập cổng server
start_frame = tk.Frame(root)
start_frame.pack(pady=20)

tk.Label(start_frame, text="Enter Port:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5)
port_entry = tk.Entry(start_frame, width=15, font=("Arial", 14))
port_entry.grid(row=0, column=1, padx=10, pady=5)
port_entry.insert(0, "1233")

tk.Button(start_frame, text="Start Server", command=switch_to_log_view, font=("Arial", 14), bg="lightblue").grid(row=1,
                                                                                                                 column=0,
                                                                                                                 columnspan=2,
                                                                                                                 pady=10)

# Giao diện log
log_frame = tk.Frame(root)
log_text = scrolledtext.ScrolledText(log_frame, width=90, height=25, font=("Arial", 14), state=tk.DISABLED)
log_text.pack(padx=10, pady=10)



root.mainloop()
