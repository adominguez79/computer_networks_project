#python3 launch-worker.py  0.0.0.0 54000 0.0.0.0 54002 2
import os
import sys
import subprocess

def  usage():
    print("Usage: launch-workers.py <worker_ip> <starting_port> <orchestrator_ip> <orchestrator_port> <num_workers>")
    sys.exit(1)

def main():
    if len(sys.argv) != 6:
        usage()

    
    worker_ip = sys.argv[1]
    starting_port = sys.argv[2]
    orch_ip = sys.argv[3]
    orch_port = sys.argv[4]
    num_workers = sys.argv[5]

    if int(num_workers) < 1 or int(num_workers) > 5:
        print("ERROR: You can only launch between 1 and 5 workers.")
        sys.exit(1)

    for i in range(int(num_workers)):
        port = int(starting_port) + i
        if port < 54000 or port > 54150:
            print(f"ERROR: Port {port} is out of range. Must be between 54000-54150.")
            sys.exit(1)
        worker_id = f"worker-{i+1:03d}"
        log_dir = f"{worker_id}"

        os.makedirs(log_dir, exist_ok=True)

        cmd = [
            "python3", "worker.py",
            str(worker_ip),
            str(port),
            str(orch_ip),
            str(orch_port),
            str(worker_id)
        ]

        print(f"Launching {worker_id} on port {port}...")
        subprocess.Popen(cmd)





if __name__ == "__main__":
    main()
