import socket
import tkinter as tk
from tkinter import messagebox, Listbox, scrolledtext
from tkinter import *

SERVER_HOST = "localhost"
SERVER_PORT = 1233
BUFFER_SIZE = 8192


class MailClient:
    def __init__(self, master):
        self.master = master
        master.title("Mail Client")

        self.username_label = tk.Label(
            master, text="Enter username: ", height=3, width=20
        )
        self.username_label.grid(row=0, column=0)
        self.username_entry = tk.Entry(master)
        self.username_entry.grid(row=0, column=1)

        self.password_label = tk.Label(
            master, text="Enter password: ", height=3, width=20
        )
        self.password_label.grid(row=1,column=0)
        self.password_entry = tk.Entry(master)
        self.password_entry.grid(row=1, column=1)

        self.create_account_button = tk.Button(
            master,
            text="Create Account",
            command=self.create_account,
            height=2,
            width=20,
            bg='lightblue'
        )
        self.create_account_button.grid(row=3, column=0, padx=5, pady=10)

        self.login_account_button = tk.Button(
            master,
            text="Login Account",
            command=self.login_account,
            height=2,
            width=20,
            bg='azure'
        )
        self.login_account_button.grid(row=3, column=1, padx=5, pady=10)

    def display_main_window(self, username):
        self.username = username
        for widget in self.master.winfo_children():
            widget.destroy()
        self.label_title = tk.Label(
            self.master, text=f"Hello {username}", width=20, height=3, font=("Arial",23)
        )
        self.label_title.pack(padx=20, pady=20)

        # Send Email Button
        self.send_email_button = tk.Button(
            self.master,
            text="Send Email",
            command=lambda: self.open_send_email_window(username),
            height=2,
            width=20,
            bg='lightblue'
        )
        self.send_email_button.pack(padx=15, pady=15)

        # Get Emails Button
        self.get_emails_button = tk.Button(
            self.master, text="Get Emails", command=lambda: self.get_emails(username), height=2, width=20, bg='azure'
        )
        self.get_emails_button.pack(padx=15, pady=15)

    def open_send_email_window(self, username):
        self.send_email_window = tk.Toplevel(self.master)
        self.send_email_window.title("Send Email")
        self.send_email_window.geometry("520x320")

        tk.Label(self.send_email_window, text="Send to").grid(row=0,column=0,padx=5,pady=10)
        self.recipient_entry = tk.Entry(self.send_email_window, width=66)
        self.recipient_entry.grid(row=0,column=1,padx=5,pady=10, sticky='w')

        tk.Label(self.send_email_window, text="Content:").grid(row=1,column=0,padx=5,pady=10)
        self.content_entry = scrolledtext.ScrolledText(self.send_email_window, wrap=tk.WORD, width=40, height=8, font=("Times New Roman", 15))
        self.content_entry.grid(row=1,column=1,padx=5,pady=10)

        self.send_button = tk.Button(
            self.send_email_window, text="Send", command=lambda: self.send_email(username), height= 2, width=10, bg='lightblue'
        )
        self.send_button.grid(row=2,column=0,padx=5,pady=10)

        self.cancel_button = tk.Button(
            self.send_email_window, text="Cancel", command=self.cancel_send_email, height= 2, width=10, bg='azure'
        )
        self.cancel_button.grid(row=2,column=1, sticky='w', padx=5,pady=10) # stick to the west side of the column.

    def cancel_send_email(self):
        self.send_email_window.destroy()

    def create_account(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty!")
            return

        response = self.send_to_server(f"CREATE_ACCOUNT:{username}:{password}")
        if "successfully" in response:
            messagebox.showinfo("Success", "Account created!")
            self.display_main_window(username)
        elif response == "USERNAME_EXISTS":
            messagebox.showinfo("Info", "Username already exists, please enter password to login!")
        else:
            messagebox.showerror("Error", "Failed to create account!")


    def login_account(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty!")

        response = self.send_to_server(f"LOGIN:{username}:{password}")
        if response == "LOGIN_SUCCESS":
            messagebox.showinfo("Success", "Login successful!")
            self.display_main_window(username)  # Chuyển sang màn hình chính
        elif response == "INVALID_PASSWORD":
            messagebox.showerror("Error", "Incorrect password! Please try again.")
            return
        elif response == "USER_NOT_FOUND":
            messagebox.showerror("Error", "Username not found! Please create an account.")
            return
        else:
            messagebox.showerror("Error", "Login failed! Please try again later.")

    def send_email(self,username):
        recipient_name = self.recipient_entry.get()
        email_content = self.content_entry.get("1.0", tk.END).strip()

        self.send_to_server(f"SEND_EMAIL:{recipient_name}:{email_content}:{username}")

        messagebox.showinfo("Success", "Mail was sent")
        self.send_email_window.destroy()

    def get_emails(self, username):
        response = self.send_to_server(f"GET_EMAILS:{username}")
        email_files = response.split(", ")

        self.display_emails(email_files)

    def display_emails(self, email_files):
        self.email_window = tk.Toplevel(self.master)
        self.email_window.title("Emails")
        self.email_window.geometry("700x350")

        # Tạo frame chứa danh sách email và scrollbar
        frame = tk.Frame(self.email_window)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = Scrollbar(frame,orient=tk.VERTICAL)

        self.email_listbox = Listbox(frame,yscrollcommand=scrollbar.set,bg="lightblue",font=("Arial",11))
        # Gán thanh cuộn cho Listbox
        scrollbar.config(command=self.email_listbox.yview)
        # Đặt listbox và scrollbar vào frame
        self.email_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        for email_file in email_files:
            self.email_listbox.insert(tk.END, email_file)
        self.email_listbox.bind("<<ListboxSelect>>", self.read_email)
        self.content_label = tk.Label(
            self.email_window, text="Select an email to read", anchor="nw", justify="left", wraplength=400, bg="azure",
            font=("Arial", 11)
        )
        self.content_label.pack(side=RIGHT,fill=BOTH, expand=True, padx=10, pady=5)

    def read_email(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            email_filename = event.widget.get(index)

            response = self.send_to_server(f"READ_EMAIL:{self.username}:{email_filename}")
            self.content_label.config(text=response)

    def send_to_server(self, message):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.settimeout(5)
            client_socket.sendto(message.encode("utf-8"), (SERVER_HOST, SERVER_PORT))
            response, _ = client_socket.recvfrom(BUFFER_SIZE)
            return response.decode("utf-8")


if __name__ == "__main__":
    root = tk.Tk()
    client = MailClient(root)
    root.mainloop()
