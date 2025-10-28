#python3 check-hits.py 127.0.1.1 54000 

import socket
import sys


def usage():
    print("Usage: check-hits.py <orchestrator_ip> <orchestrator_port> <N>")
    sys.exit(1)

def main():
    if len(sys.argv) != 4:
        usage()

    hits = int(sys.argv[3])
    if hits < 1 or hits > 5:
        print("ERROR: You can only request between 1 and 5 hits.")
        sys.exit(1)

    orchestrator_ip = sys.argv[1]
    orchestrator_port = int(sys.argv[2])

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Send HITS command
        msg = f"GET_HITS {hits}"
        sock.sendto(msg.encode(), (orchestrator_ip, orchestrator_port))

        # Receive reply
        data, _ = sock.recvfrom(4096)
        print(f"Current hits:\n{data.decode()}" )

    except socket.timeout:
        print("Timed out waiting for reply.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()