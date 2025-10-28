import socket
import sys
import time
import select
import queue

UDP_IP = "0.0.0.0"

# Workers: { identifier: {host, port, last_sent} }
worker_pool = {}

# Job queue: list of (job_string, client_addr)
job_queue = queue.Queue()

# Hit records: list of dicts
hits = []

def return_hits(message, addr, updsockfd):
    parts = message.strip().split()
    if len(parts) != 2:
        print(f"Invalid GET_HITS message: {message}")
        return
    _, n = parts
    lines = []
    for h in range(int(n)):
        try:
            hit = hits[h]
        except IndexError:
            break
        line = f"{hit[0]} {hit[1]} {hit[2]} {hit[3]}"
        lines.append(line)
    message = "\n".join(lines)
    updsockfd.sendto(message.encode(), addr)
    print("Sending hits")

def add_hit(message):
    parts = message.strip().split()
    if len(parts) != 5:
        print(f"Invalid HIT message: {message}")
        return
    _, identifier, siteID, delim, time = parts
    pool_status[identifier]['last_sent'] = time.time()
    hits.append((identifier, siteID, delim, time))
    print(f"Recorded hit from {identifier} on {siteID} at {time}")

def pool_status(addr, updsockfd):
    lines = []
    recieved_formated, sent_formated = "None", "None"
    for ident, info in worker_pool.items():
        sent_timestamp = info['last_sent']
        recieved_timestamp = info['last_recieved']
        if recieved_timestamp is not None:
            recieved_formated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(recieved_timestamp))
        if sent_timestamp is not None:
            sent_formated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sent_timestamp))

        line = f"{ident} Port:{info['port']} Last Sent: {sent_formated} Last Recieved: {recieved_formated}"
        lines.append(line)
        message = "\n".join(lines)
        updsockfd.sendto(message.encode(), addr)

# Handles request from client
def handle_request(message, addr, updsockfd):
    job_queue.put((message, addr))
    print(f"Job queued from {addr}")
    message = "200 OK"
    updsockfd.sendto(message.encode(), addr)

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
        "last_recieved": None,
    }
    print(f"Worker ({ident}) registered: {host}:{port}") 

# Deregister a worker
def deregister_worker(message, addr):

    parts = message.strip().split()
    if len(parts) != 2:
        print(f"Invalid message from {addr}")
        return

    _, ident = parts

    worker_pool.pop(ident, None)
    print(f"Worker {ident} deregistered")


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
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    print(f"Orchestrator Listening on {IPAddr}:{port}")

    try:
        while True:
            # Use select to wait for incoming UDP messages
            readable, _, _ = select.select([udpsockfd], [], [], 0.5)

            for sock in readable:
                if sock == udpsockfd:
                    data, addr = udpsockfd.recvfrom(1400)
                    message = data.decode()
                    #Message from worker
                    if message.startswith("REGISTER"):
                        register_worker(message, addr)
                    elif message.startswith("DEREGISTER"):
                        deregister_worker(message, addr)
                    #Message from client
                    elif message.startswith("CHECK"):
                        handle_request(message, addr, udpsockfd)
                    elif message.startswith("STATUS"):
                        print("Sending pool status")
                        pool_status(addr, udpsockfd)
                    elif message.startswith("GET_HITS"):
                        return_hits(message, addr, udpsockfd)
                    elif message.startswith("HIT"):
                        add_hit(message)
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