from socket import *
from client import  Client
import threading

def login(user, password, tcp_socket, udp_port):
    """Validates user login details."""

    print(f"Login attempt: \nAccount name: {user}")
    if user in online_users:   #User's already online
        print("[Login Denied] User is already online.❌")
        tcp_socket.send("USER_ONLINE".encode())

    elif password == login_details.get(user): # Valid login
        print("User logged in successfully✅\n")
        tcp_socket.send("Valid".encode())
        online_users[user] = (tcp_socket, udp_port)

    else: # anything else return invalid
        print("[Login Denied] User details maybe incorrect.❌")
        tcp_socket.send("Invalid".encode())
    

def execute_msg(msg, sender_socket: socket, ip):
    """Decides the types of action the sender client wants to perform
    and runs the correspoding function.
    """
    msg_parts = msg.split("|")
    msg_type = msg_parts[0]
    
    match msg_type:
        case "LOGIN":
            username = msg_parts[1]
            password = msg_parts[2]
            udp_port = msg_parts[3]
            login(username, password, sender_socket, udp_port)

        case "PRIVATE":
            sender = msg_parts[1]
            target = msg_parts[2]
            msg = msg_parts[3]
            forward_msg(msg, sender, target, "")

        case "GROUP":
            sender = msg_parts[1]
            group = msg_parts[2]
            msg = msg = f"{sender}: {msg_parts[3]}"
            broadcast(msg, sender, group)

        case "MEDIA_REQUEST":
            sender = msg_parts[1]
            target = msg_parts[2]
            file_path = msg_parts[3]
            if target not in online_users:
                online_users[sender][0].send("ERROR|USER_OFFLINE\n".encode())
            else:
                msg = f"MEDIA_INFO|{target}|{ip[0]}|{online_users[target][1]}|{file_path}"
                online_users[sender][0].send(msg.encode())

        case "MEDIA_READY":
            sender   = msg_parts[1]
            target   = msg_parts[2]
            file_path = msg_parts[3]
            if target in online_users:
                msg = f"MEDIA_READY|{sender}|{target}|{file_path}"
                online_users[target][0].send(msg.encode())

def forward_msg(msg, sender, target, group):
    """Sends message from one client to another"""

    if target in online_users:
        print(f"{sender} -> {target}: {msg}")

        target_socket = online_users[target][0]
        if not group.startswith("(group)"):
            formatted_msg = f"PRIVATE|{sender}|{msg}"
        else:
            formatted_msg = f"GROUP|{group}|{sender}|{msg}"

        target_socket.send(formatted_msg.encode())

    """else:
        if sender in online_users:
            sender_socket = online_users[sender][0]
            sender_socket.send("ERROR|USER_OFFLINE\n".encode())"""
        
def broadcast(msg, sender, group):
    """Sends a group message to all members in the group."""
    targets = groups_list.get(group)

    for target in targets:
        if target != sender:
            forward_msg(msg, sender, target, group)

def set_user_offline(client_socket):
    print(f"Client disconnected: {client_socket}")
    offline_client = None
    for username, (sock, port) in online_users.items():
        if client_socket is sock:
           offline_client = username
           break
    if offline_client:
        del online_users[offline_client]
    client_socket.close()

def handle_client(client_socket, ip):
    """Listens for incoming messages from the client."""
    while True:
        #try:
            msg = client_socket.recv(1024).decode()
            execute_msg(msg, client_socket, ip)
        #except:
        #    set_user_offline(client_socket)
        #    break

def main():
    print("Server status: Online✅")
    while True:
        client_socket, ip_addr = server.accept()
        print(f"\nClient Connected: {ip_addr}")
        threading.Thread(
            target=handle_client, 
            args=(client_socket, ip_addr,),
            daemon=True
        ).start()

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 12345

    server = socket(AF_INET, SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    online_users = {}

    login_details = {"zakes"    : "password",
                    "Abu"       : "secure",
                    "Zaafir"    : "pass",
                    "Fayaaz"    : "CoD_007",
                    "Bahu"      : "owcs"}
    
    groups_list = {"(group) 90" : ["zakes", "Abu", "Zaafir"]}

    main()
