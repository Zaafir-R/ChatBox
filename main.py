from client import Client
from gui import UI
import sys, threading
import tkinter as tk


def login(client) -> str:
    try:
        while True:
            print("===========[ChatBox Login:]==========")
            print("(Press Ctrl + C to exit program)")
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            response = client.login(username, password)
            if response == "Valid":
                print(f"Welcome back, {username}! Starting app...")
                break
            else:
                print("Incorrect details. Try again."+ response)
        return username
    except:
        print(f"[ERROR] Login error.")
        print("\n==========[Exiting program]===========")
        sys.exit(0)


def main():
    client = Client()
    client.username = login(client)

    window = tk.Tk()
    app = UI(window, client)
    
    receive_thread = threading.Thread(
         target=client.receive_messages, 
         args=(app,), 
         daemon=True
    )
    receive_thread.start()

    window.focus_force()
    window.mainloop()


if __name__ == "__main__":
    main()
    
