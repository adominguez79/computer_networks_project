import os
import sys
import subprocess

def  usage():
    print("Usage: launch-workers.py <orchestrator_ip> <orchestrator_port> <worker_ip> <starting_port> <num_workers>")
    sys.exit(1)

def main():
    if len(sys.argv) != 6:
        usage()

    orch_ip = sys.argv[1]
    orch_port = int(sys.argv[2])
    worker_ip = sys.argv[3]
    starting_port = int(sys.argv[4])
    num_workers = int(sys.argv[5])

    if num_workers < 1 or num_workers > 5:
        print("ERROR: You can only launch between 1 and 5 workers.")
        sys.exit(1)

    for i in range(num_workers):
        port = starting_port + i
        if port < 54000 or port > 54150:
            print(f"ERROR: Port {port} is out of range. Must be between 54000-54150.")
            sys.exit(1)
        worker_id = f"worker-{i+1:03d}"
        log_dir = f"{worker_id}"

        os.makedirs(log_dir, exist_ok=True)

        cmd = [
            "python3", "worker.py",
            port,
            log_dir,
            worker_ip,
            orch_ip,
            orch_port,
            worker_id
        ]

        print(f"Launching {worker_id} on port {port}...")
        subprocess.Popen(cmd)





if __name__ == "__main__":
    main()
