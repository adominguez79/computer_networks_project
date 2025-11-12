#python3 pool-status.py 0.0.0.0 54000 

import socket
import sys

def usage():
    print("Usage: pool-status.py <orchestrator_ip> <orchestrator_port>")
    sys.exit(1)

def main():
    if len(sys.argv) != 3:
        usage()

    orchestrator_ip = sys.argv[1]
    orchestrator_port = int(sys.argv[2])

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("[Pool Status]" + "connected to " + orchestrator_ip)
        # Send STATUS command
        msg = "STATUS"
        sock.sendto(msg.encode(), (orchestrator_ip, orchestrator_port))

        # Receive reply
        data, _ = sock.recvfrom(4096)
        print(f"[Pool Status]\n {data.decode()}")

    except socket.timeout:
        print("[pool-status] Timed out waiting for reply.")
    except Exception as e:
        print(f"[pool-status] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
