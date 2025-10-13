import socket
import sys
import argparse
import time
import math
import select
import queue

UDP_IP = "0.0.0.0"

# Workers: { identifier: {host, port, last_sent, last_response} }
worker_pool = {}

# Job queue: list of (job_string, client_addr)
job_queue = queue.Queue()

# Hit records: list of dicts
hits = []

# Handles request from client
def handle_request(message, addr, udp_sock):
    job_queue.put((message, addr))
    print(f"Job queued from {addr}")
    message = "200 OK"
    udp_sock.sendto(message.encode(), addr)

# Reregister a woker
def register_worker(message, addr):

    parts = message.strip().split()
    if len(parts) != 4:
        print(f"Invalid message from {addr}")
        return

    _, host, port_str, ident = parts
    port = int(port_str)

    worker_pool[ident] = {
        "host": host,
        "port": port,
        "last_sent": None,
        "last_response": None
    }
    print(f"Worker {ident} registered: {host}:{port}")


#Assing job from queue to worker
def dispatch_jobs():
    if job_queue.empty() or not worker_pool:
        return

    job, client_addr = job_queue.get()

    for ident, info in worker_pool.items():
        try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((info["host"], info["port"]))
                s.sendall(job.encode())
                print(f"Job dispatched to {ident}")
                info["last_sent"] = time.time()
                s.close()
                break
        except Exception as e:
            print(f"Could not send to {ident}: {e}")
            continue
    else:
        # No worker could take job
        job_queue.put((job, client_addr))

#Send terminate signal when CRLT-C
def terminate_workers():
     terminate_msg = "TERMINATE"
     for ident, info in worker_pool.items():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((info["host"], info["port"]))
                s.sendall(terminate_msg.encode())
            except Exception as e:
                print(f"Could not send terminate to {ident}: {e}")
                continue

def main(port):

    udpsockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpsockfd.bind((UDP_IP, port))
    print(f"Orchestrator Listening on {UDP_IP}:{port}")

    try:
        while True:
            readable, _, _ = select.select([udpsockfd], [], [], 0.5)

            for sock in readable:
                if sock == udpsockfd:
                    data, addr = udpsockfd.recvfrom(1400)
                    message = data.decode()
                    #Message from worker
                    if message.startswith("REGISTER"):
                        register_worker(message, addr)
                    #Message from client
                    elif message.startswith("CHECK"):
                        handle_request(message, addr, udpsockfd)
                    else:
                        print(f"Unknown message from {addr}: {message}")

            dispatch_jobs()

    except KeyboardInterrupt:
        print("\nShutting down orchestrator")
        terminate_workers()
        udpsockfd.close()

if __name__ == "__main__":
    port = int(sys.argv[1])
    if port < 54000 or port > 54150:
        print(f"Port is {port} out of range. Must be between 54000-54150.")
        sys.exit(1)
    main(port)