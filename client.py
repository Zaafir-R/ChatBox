from socket import *
import sys, time, threading, os

class Client:
    def __init__(self):
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_port = self.find_udp_port()
        self.username = "guest"
        self.connect_to_server()

    def connect_to_server(self):
        """Tries to establish a TCP connection with the server."""
        try: 
            self.tcp_socket.connect(("localhost", 12345))
        except ConnectionRefusedError:
            print("\n==========[ChatBox:]==========")
            print("[ERROR] Couldn't connect to server. Rerun client.py to try again.")
            print("\n======[Exiting program]=======\n")
            sys.exit(1)   

    def find_udp_port(self) -> int:
        """Returns a port available for use"""
        for port in range(10000, 10021):
            try:
                self.udp_socket.bind(("localhost", port))
                return port
            except OSError:
                #Port is already in use
                pass
        print("[ERROR] No available UDP ports found.")
        sys.exit(1)

    def login(self, username, password) -> str:
        """Sends LOGIN command and returns server response string."""
        msg = f"LOGIN|{username}|{password}|{self.udp_port}"
        self.tcp_socket.send(msg.encode())
        response = self.tcp_socket.recv(1024).decode()
        if response == "Valid":
            self.username = username
        return response

    def send_message(self, msg: str, receiver):
        """Sends a message to the server."""
        if(receiver.lower().startswith("(group)")):
            msg = f"GROUP|{self.username}|{receiver}|{msg}"
        else:
            msg = f"PRIVATE|{self.username}|{receiver}|{msg}"
        self.tcp_socket.send(msg.encode())

    def show_group_msg(self, app, group, sender, msg):
        app.show_message(f"{msg}", "default")

    def request_file_transfer(self, receiver: str, file_path: str):
        """Asks the server for the target's UDP address so we can push a file."""
        msg = f"MEDIA_REQUEST|{self.username}|{receiver}|{file_path}"
        self.tcp_socket.send(msg.encode())


    def receive_messages(self, app):
        while True:
            try:
                msg = self.tcp_socket.recv(1024).decode()
                
                if not msg:
                    break
                
                msg_parts = msg.split("|")
                msg_type = msg_parts[0]
                match msg_type:
                    case "PRIVATE":
                        app.show_message(msg_parts[2], "default")

                    case "GROUP":
                        group = msg_parts[1]
                        sender = msg_parts[2]
                        msg = msg_parts[3]
                        self.show_group_msg(app, group, sender, msg)

                    case "MEDIA_INFO":
                        #Serever tells sender where file must go
                        #split for components to share file
                        msg_parts = msg.split("|")
                        target = msg_parts[1]
                        target_ip = msg_parts[2]
                        target_udp  = int(msg_parts[3])
                        file_path   = msg_parts[4]
                        threading.Thread(target=self.share_file,args=(target, target_ip, target_udp, file_path),daemon=True).start()
                    
                    
                    case "MEDIA_READY":
                        #server tells the reciever there is a file coming
                        msg_parts = msg.split("|")
                        sender    = msg_parts[1]
                        file_path = msg_parts[3]
                        app.show_message(f"📎  {sender} is sending you a file: {os.path.basename(file_path)}")
                        threading.Thread(target=self.receive_files,args=(file_path,app),daemon=True).start()

                    case "ERROR":
                        app.show_message(f"ERROR:{msg}", tag="error")           
            except:
                print("[Error] Cannot create thread to receive messages.")
                print("\n==========[Exiting program]===========")
                sys.exit(0)

    def share_file(self, target: str, target_ip: str, target_port: int, file_path: str):
        #send message to reciever notfying them ofr files being sent
        if not os.path.isfile(file_path):
           print(f"[ERROR] File not found: {file_path}")
           return
         
        msg = f"MEDIA_READY|{self.username}|{target}|{file_path}"
        self.tcp_socket.send(msg.encode())
        
        time.sleep(0.3)#give the reciever thread time to start before sending data

        print(f"Sending '{os.path.basename(file_path)}' to {target} …")
        with open(file_path, "rb") as f:
            while chunk := f.read(1024):
                self.udp_socket.sendto(chunk, (target_ip, target_port))
            
            self.udp_socket.sendto(b"<EOF>", (target_ip, target_port))
        print(f"File '{file_path}' sent.")


    def receive_files(self, file_path, sender):
        """
        Receives files using a seperate socket so there is no conflict and saves the file
        a working directory
        """
        save_path = os.path.basename(file_path)
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        full_save_path = os.path.join(downloads, save_path)

        # recv_sock = socket(AF_INET, SOCK_DGRAM)
        # recv_sock.bind(("localhost", self.udp_port))

        with open(full_save_path, "wb") as f:
            while True:
                data, addr = self.udp_socket.recvfrom(1024)
                if data == b"<EOF>":
                    break
                f.write(data)
        
        
        msg = f"📎  File received: '{save_path}'"
        print(f"[UDP] {msg}")
        if app:
            app.show_message(msg, tag="system")


if __name__ == "__main__":
    client = Client() 
    client.username = "Bahu"
    client.send_message(msg="Hello Zakes", receiver="zakes")
    print("sent")
