import socket
import tkinter as tk
from tkinter import messagebox, Listbox

SERVER_HOST = "localhost"
SERVER_PORT = 1233
BUFFER_SIZE = 1024


class MailClient:
    def __init__(self, master):
        self.master = master
        master.title("Mail Client")

        self.username_label = tk.Label(
            master, text="Enter username:", height=2, width=20
        )
        self.username_label.pack(padx=10, pady=10)
        self.username_entry = tk.Entry(master)
        self.username_entry.pack(padx=20, pady=20)

        self.create_account_button = tk.Button(
            master,
            text="Create Account",
            command=self.create_account,
            height=2,
            width=20,
        )
        self.create_account_button.pack()

    def display_main_window(self):
        self.master.title(self.username_entry.get())
        self.username_label.destroy()
        self.username_entry.pack_forget()
        self.create_account_button.destroy()

        self.label_title = tk.Label(
            self.master, text=f"Hello {self.username_entry.get()}", width=20, height=3
        )
        self.label_title.pack(padx=20, pady=20)

        # Send Email Button
        self.send_email_button = tk.Button(
            self.master,
            text="Send Email",
            command=self.open_send_email_window,
            height=2,
            width=20,
        )
        self.send_email_button.pack(padx=15, pady=15)

        # Get Emails Button
        self.get_emails_button = tk.Button(
            self.master, text="Get Emails", command=self.get_emails, height=2, width=20
        )
        self.get_emails_button.pack(padx=15, pady=15)

    def open_send_email_window(self):
        self.send_email_window = tk.Toplevel(self.master)
        self.send_email_window.title("Send Email")

        tk.Label(self.send_email_window, text="Send to").pack()
        self.recipient_entry = tk.Entry(self.send_email_window)
        self.recipient_entry.pack()

        tk.Label(self.send_email_window, text="Content:").pack()
        self.content_entry = tk.Entry(self.send_email_window)
        self.content_entry.pack()

        self.send_button = tk.Button(
            self.send_email_window, text="Send", command=self.send_email
        )
        self.send_button.pack()

        self.cancel_button = tk.Button(
            self.send_email_window, text="Cancel", command=self.cancel_send_email
        )
        self.cancel_button.pack()

    def cancel_send_email(self):
        self.send_email_window.destroy()

    def create_account(self):
        username = self.username_entry.get().strip()
        if username:
            response = self.send_to_server(f"CREATE_ACCOUNT:{username}")
            if "successfully" in response:
                messagebox.showinfo("Success", "Account created!")
                self.display_main_window()
            else:
                messagebox.showerror("Error", "Failed to create account!")
        else:
            messagebox.showerror("Error", "Username cannot be empty!")

    def send_email(self):
        username = self.recipient_entry.get()
        email_content = self.content_entry.get().strip()
        sending_name = self.username_entry.get()

        self.send_to_server(f"SEND_EMAIL:{username}:{email_content}:{sending_name}")

        messagebox.showinfo("Success", "Mail was sent")
        self.send_email_window.destroy()

    def get_emails(self):
        username = self.username_entry.get()
        response = self.send_to_server(f"GET_EMAILS:{username}")
        email_files = response.split(", ")

        self.display_emails(email_files)

    def display_emails(self, email_files):
        self.email_window = tk.Toplevel(self.master)
        self.email_window.title("Emails")

        self.email_listbox = Listbox(self.email_window)
        for email_file in email_files:
            self.email_listbox.insert(tk.END, email_file)
        self.email_listbox.pack()

        self.email_listbox.bind("<<ListboxSelect>>", self.read_email)

    def read_email(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            email_filename = event.widget.get(index)

            username = self.username_entry.get()
            response = self.send_to_server(f"READ_EMAIL:{username}:{email_filename}")
            messagebox.showinfo("Email Content", response)

    def send_to_server(self, message):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.sendto(message.encode("utf-8"), (SERVER_HOST, SERVER_PORT))
            response, _ = client_socket.recvfrom(BUFFER_SIZE)
            return response.decode("utf-8")


if __name__ == "__main__":
    root = tk.Tk()
    client = MailClient(root)
    root.mainloop()
