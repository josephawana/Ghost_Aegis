import subprocess
import datetime
import os
import sys

def run_network_sentinel():
    """Audits active network connections and identifies the process."""
    print("[*] Initiating Network Sentinel Scan...")
    try:
        # -a (all), -n (numerical), -o (owner PID)
        result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        
        print(f"{'Protocol':<10} {'Local Address':<25} {'Foreign Address':<25} {'State':<15} {'PID':<10}")
        print("-" * 85)
        
        # We only care about "ESTABLISHED" connections (active conversations)
        for line in lines[4:]:
            parts = line.split()
            if len(parts) >= 5 and parts[3] == "ESTABLISHED":
                proto, local, foreign, state, pid = parts[0], parts[1], parts[2], parts[3], parts[4]
                print(f"{proto:<10} {local:<25} {foreign:<25} {state:<15} {pid:<10}")
                
        print("[+] Network Audit Complete.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Sentinel Error: {e}")


def user_exists(username):
    """Verifies the user exists on the local system."""
    try:
        subprocess.run(["net", "user", username], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def elevate_user(username):
    """Attempts to add the user to the Administrators group."""
    try:
        subprocess.run(["net", "localgroup", "Administrators", username, "/add"], 
                       capture_output=True, text=True, check=True)
        print(f"[+] Success: {username} granted Temporary Admin Rights.")
        return True
    except subprocess.CalledProcessError as e:
        error_text = e.stderr.strip()
        if "1378" in error_text or "already a member" in error_text.lower():
            print(f"[*] Note: {username} is already an Administrator.")
            return True # We return True so we can still schedule a cleanup if desired
        else:
            print(f"[!] Elevation Failed: {error_text}")
            return False

def schedule_cleanup_session(username, minutes):
    """Schedules the aegis_cleanup.py script to run after the timer expires."""
    execute_time = (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).strftime("%H:%M")
    task_name = f"GhostAegis_Sanitize_{username.replace(' ', '_')}"
    
    python_exe = sys.executable
    cleanup_script = os.path.abspath("aegis_cleanup.py")
    
    # Building the command to call our cleanup script with the username as an argument
    revoke_command = f'"{python_exe}" "{cleanup_script}" "{username}"'
    
    cmd = [
        "schtasks", "/Create", "/F", "/SC", "ONCE",
        "/TN", task_name,
        "/TR", revoke_command,
        "/ST", execute_time,
        "/RL", "HIGHEST"
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"[+] Aegis Protocol Locked: Cleanup scheduled for {execute_time}.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to schedule cleanup task: {e.stderr.strip()}")

def start_jit_session(username, minutes=15):
    """The main entry point to start a JIT session."""
    print(f"\n--- Ghost-Aegis JIT Session: {username} ---")
    
    # 1. Existence Check
    if not user_exists(username):
        print(f"[!] Abort: User '{username}' not found on this system.")
        return

    # 2. Elevation Step
    if elevate_user(username):
        # 3. Scheduling Step (Only happens if elevation worked)
        schedule_cleanup_session(username, minutes)
    
    print("-" * 40)

if __name__ == "__main__":
    # Example usage for testing
    # In your GUI, you would call start_jit_session(target, time)
    test_user = "GhostTest"  # Replace with an actual username on your system for testing
    start_jit_session(test_user, 1)