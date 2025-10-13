
import socket
import sys
import scanner
import os

def get_tokens(msg):
    tokens = msg.split()
    if len(tokens) != 4 or tokens[0] != "CHECK":
        print(f"Invalid request format: {msg}")
        return None, None
    return tokens[1], tokens[2], tokens[3]

def main(orchestrator_ip, orchestrator_port, host_ip, port, identifier):
    message = f"REGISTER {host_ip} {port} {identifier}"
    sock_fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_fd.sendto(message.encode(), (orchestrator_ip, orchestrator_port))
    print(f"[{identifier}] Registered with orchestrator")

def tcp_requests(port,identifier):
    
    if(not os.path.isdir(identifier)):
        os.mkdir(identifier)
        os.chdir(identifier)
    else:
        os.chdir(identifier)
    base_dir = os.getcwd()
    

    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd.bind(('0.0.0.0', port))
    sockfd.listen()

    print(f"[{identifier}] Listening on port {port}")

    while True:
        try:
            conn, addr = sockfd.accept()
            print(f"[{identifier}] Got connection from {addr}")
            with conn:
                data = conn.recv(1024)
                #Terminate worker
                if data.decode() == "TERMINATE":  
                    print(f"[{identifier}] Terminating")
                    break
                if not data:
                    continue
                request = data.decode()
                print(f"[{identifier}] Got request: {request}")
                website, delim, siteID = get_tokens(request)
                try:
                    os.chdir(siteID)
                except FileNotFoundError:
                    os.mkdir(siteID)
                    os.chdir(siteID)
                #create siteID dir if it doesn't exist
                print(os.getcwd())
                scanner.main(identifier,website,siteID,sockfd,delim)
                os.chdir(base_dir)
                print(os.getcwd())
        except BrokenPipeError:
            print(f"[{identifier}] Broken pipe — orchestrator may have closed connection early.")
        except Exception as e:
            print(f"[Worker] Error: {e}")
        finally:
            conn.close()




if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: worker.py <port> <log_path> <worker_ip> <orchestrator_ip> <orchestrator_port> <identifier>")
        sys.exit(1)

    port = int(sys.argv[1])
    log_path = sys.argv[2]
    host_ip = sys.argv[3]
    orchestrator_ip = sys.argv[4]
    orchestrator_port = int(sys.argv[5])
    identifier = sys.argv[6]

    main(orchestrator_ip, orchestrator_port, host_ip, port, identifier)
    tcp_requests(port, identifier)