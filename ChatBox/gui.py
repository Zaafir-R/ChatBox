import os
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from client import Client


class UI:
    def __init__(self, window, client: Client):
        self.client = client
        self.window = window
        self.receiver = None
        self.window.geometry("815x466")
        self.window.title("ChatBox")

        self.frame = tk.Frame(bg="#09435A")
        self.frame.pack()
        self.create_frames()
        self.create_widgets()
        
    def create_frames(self):
        self.chat_frame = tk.LabelFrame(self.frame)
        self.chat_frame.grid(sticky="w")

        self.chats_frame = tk.LabelFrame(
            self.frame,
            text="Chats:",
            font = ("Courier", 12),
            bg="#09435A",
            fg="#FFFFFF",
            borderwidth=0
        )
        
        self.chats_frame.grid(row=0, column=1, padx=(3,3))

        self.text_frame = tk.LabelFrame(
            self.frame, 
            bg = "#0C5F80",
            fg = "#FFFFFF",
            font= ("Courier", 10),
            text="Enter Message:",
            borderwidth=0
        )

        self.text_frame.grid(row=1, column=0, sticky="wes")

        self.button_frame = tk.LabelFrame(
            self.text_frame,
            bg="#0C5F80",
            borderwidth=0
        )
        
        self.button_frame.grid(row=2, column=0, sticky="e", pady=3)

    def create_widgets(self):
        self.chat_output = ScrolledText(
            self.chat_frame, 
            state="disabled"
        )
        self.chat_output.grid(row=0, column=0)
        
        self.textbar = tk.Entry(self.text_frame, width=105,)
        self.textbar.grid(row=0, column=0, padx = 10, pady=3)
        
        users_list = ["zakes", "Abu", "Bahu", "Fayaaz", "Zaafir", "(group) 90"]

        self.chat_listbox = tk.Listbox(
            self.chats_frame,
            font=("Aptos", 10)
        )

        for u in users_list:
            if u != self.client.username:
                self.chat_listbox.insert(tk.END, u)
        self.chat_listbox.grid(row=0, column=0)        

        self.open_chat_btn = tk.Button(
            self.chats_frame, 
            text="Open chat",
            command=self.on_open_chat_click
        )

        self.open_chat_btn.grid(row=1, column=0, pady =(5,0))

        self.send_btn = tk.Button(
            self.button_frame,
            text = "Send",
            command=self.on_send_click
        )

        self.send_btn.grid(row=1, column=1)

        self.share_btn = tk.Button(
            self.button_frame,
            text = "Share📂",
            command=self.on_sharefile_click
        )

        self.share_btn.grid(row= 1, column=2, padx=(0,8))
    
    def show_message(self, msg: str, tag: str = "them"):
        
        self.window.after(0, self._append_message, msg, tag)

    def _append_message(self, msg: str, tag: str):
        self.chat_output.config(state="normal")
        self.chat_output.insert(tk.END, msg + "\n", tag)
        self.chat_output.config(state="disabled")
        self.chat_output.see(tk.END)

    def clear_chat(self):
        """Removes all messages on screen"""
        self.chat_output.config(state='normal')
        self.chat_output.delete('1.0', tk.END)
        self.chat_output.config(state="disabled")

    def on_open_chat_click(self):
        chat_indexes = self.chat_listbox.curselection()
        if len(chat_indexes) > 0:
            self.receiver = self.chat_listbox.get(chat_indexes[0])
            self.clear_chat()
            self.show_message(f"==================================[{self.receiver}]================================",tag="system")

    def on_send_click(self):
        if self.receiver:
            msg = self.textbar.get()
            self.show_message(f"You: {msg}", "default")
            self.textbar.delete(0,tk.END)
            self.client.send_message(msg, self.receiver)

    def on_sharefile_click(self):
        if not self.receiver:
            self.show_message("Please select a contact or group",tag="System")
            return

        file_path = filedialog.askopenfilename(
            title="Select A File",
            filetypes=(("All Files", "*.*"),)
        )

        if not file_path:
            return

        filename = os.path.basename(file_path)
        self.show_message(f"You: 📎  Sending '{filename}' …", tag="you")
        
        self.textbar.delete(0, tk.END)
        self.textbar.insert(0, file_path)
        self.client.request_file_transfer(self.receiver,file_path)

if __name__ == "__main__":
    window = tk.Tk()
    client = Client()
    client.username = "zakes"
    app = UI(window, client)
    window.mainloop()
