import subprocess
import time
import ctypes
import sys

def is_admin():
    """Checks if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def get_admin_count():
    """Counts how many users are currently in the Administrators group."""
    try:
        output = subprocess.check_output("net localgroup Administrators", shell=True).decode()
        lines = output.splitlines()
        # Find the separator line to start counting names
        try:
            start_index = lines.index('-------------------------------------------------------------------------------') + 1
            # Filter out empty lines and the 'The command completed successfully' message
            names = [line.strip() for line in lines[start_index:] if line.strip() and "The command completed" not in line]
            return len(names)
        except ValueError:
            return 0
    except Exception:
        return 0

def user_exists(username):
    """Checks if the user exists on the system before trying to modify them."""
    try:
        subprocess.run(["net", "user", username], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def manage_privilege(username, action):
    """
    Adds or removes a user from the Administrators group.
    Returns True if successful, False otherwise.
    """
    # SAFETY: Never revoke if it's the last admin
    if action == "/delete" and get_admin_count() <= 1:
        print(f"[!] SAFETY TRIGGERED: {username} is the last admin. Revocation blocked.")
        return False

    command = ["net", "localgroup", "Administrators", username, action]
    
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        if action == "/add":
            print(f"[+] SUCCESS: {username} granted Temporary Admin Rights.")
        else:
            # OPTIONAL: Explicitly ensure they are in the 'Users' group so they don't become a 'Guest'
            subprocess.run(["net", "localgroup", "Users", username, "/add"], capture_output=True)
            print(f"[-] SUCCESS: {username} returned to Standard User.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] ERROR: Failed to {action} {username}.")
        # This prevents the 'Details' from being empty or messy
        error_msg = e.stderr.strip() if e.stderr else "User not found or Access Denied."
        print(f"Details: {error_msg}")
        return False

def jit_elevation_session(username, minutes_active):
    """Grants admin rights, waits, and revokes them only if elevation worked."""
    print(f"\n--- Ghost-Aegis JIT Controller Initiated ---")
    
    # 1. Check if user exists first
    if not user_exists(username):
        print(f"[!] ABORT: The user '{username}' does not exist on this system.")
        return

    # 2. Attempt to elevate
    if manage_privilege(username, "/add"):
        # 3. Only start timer if elevation actually worked
        seconds_active = minutes_active * 60
        print(f"[*] Timer started for {minutes_active} minute(s).")
        
        try:
            time.sleep(seconds_active)
            print(f"\n[*] Time expired! Revoking privileges...")
            manage_privilege(username, "/delete")
        except KeyboardInterrupt:
            print(f"\n[!] Manual interruption detected! Revoking rights early for safety...")
            manage_privilege(username, "/delete")
    else:
        print("[!] JIT Session cancelled due to elevation failure.")
    
    print(f"--- Session Closed ---")

if __name__ == "__main__":
    if not is_admin():
        print("[!] Ghost-Aegis requires Administrator privileges to run.")
        sys.exit()

    # Dynamic target: Use the current user instead of 'TestUser' to avoid errors
    import os
    current_user = os.getlogin() 
    
    # Or keep a manual toggle for testing
    target = current_user 
    elevation_time = 1 

    jit_elevation_session(target, elevation_time)