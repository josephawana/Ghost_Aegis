import subprocess
import os
import shutil
import sys

def get_all_admins():
    """Returns a list of all users in the Administrators group, excluding system accounts."""
    print("[*] Auditing Administrator Group...")
    # Add your own permanent Windows username to this list to stay safe!
    # Example: protected_accounts = ["Administrator", "Guest", "DefaultAccount", "WDAGUtilityAccount", "Mass Effect 3"]
    protected_accounts = ["Administrator", "Guest", "DefaultAccount", "WDAGUtilityAccount"]
    
    admin_list = []
    try:
        result = subprocess.run(["net", "localgroup", "Administrators"], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        start_parsing = False
        for line in lines:
            if "---" in line:
                start_parsing = True
                continue
            if start_parsing:
                name = line.strip()
                if not name or "The command completed" in name:
                    break
                if name not in protected_accounts:
                    admin_list.append(name)
        return admin_list
    except subprocess.CalledProcessError as e:
        print(f"[!] Error auditing groups: {e}")
        return []

def revoke_admin(username):
    """Demotes the user back to Standard User and prevents the Guest bug."""
    print(f"[*] Revoking Admin rights for {username}...")
    
    # STEP 1: Remove from Administrators
    try:
        subprocess.run(["net", "localgroup", "Administrators", username, "/delete"], 
                       capture_output=True, text=True, check=True)
        print(f"[+] {username} removed from Administrators.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to revoke rights for {username}: {e.stderr.strip()}")

    # STEP 2: The Guest Bug Fix - Explicitly add to Users group
    try:
        subprocess.run(["net", "localgroup", "Users", username, "/add"], 
                       capture_output=True, text=True, check=True)
        print(f"[+] SAFETY CHECK: {username} explicitly secured in standard 'Users' group.")
    except subprocess.CalledProcessError:
        # We can ignore errors here; Windows throws one if they are already in the group.
        pass

def wipe_temp_files():
    """Removes temporary files from common locations."""
    print("[*] Wiping temporary files...")
    temp_paths = [
        os.environ.get("TEMP", ""),
        os.environ.get("TMP", ""),
        os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Temp"),
    ]
    for path in temp_paths:
        if path and os.path.exists(path):
            try:
                # ignore_errors=True allows us to skip files currently in use by Windows
                shutil.rmtree(path, ignore_errors=True)
                # Re-creating the folder if it was the main temp dir so apps don't crash
                if not os.path.exists(path):
                    os.makedirs(path)
                print(f"[+] Cleaned: {path}")
            except Exception as e:
                print(f"[-] Failed to clean {path}: {e}")

def flush_dns():
    """Flushes the DNS resolver cache."""
    print("[*] Flushing DNS cache...")
    try:
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, check=True)
        print("[+] DNS cache flushed.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to flush DNS: {e}")

if __name__ == "__main__":
    print("=== GHOST-AEGIS CLEANUP PROTOCOL INITIATED ===")
    
    # 1. Automate Revocation
    # Check if a specific user was passed by the Task Scheduler (e.g., from main.py)
    if len(sys.argv) > 1:
        target_user = sys.argv[1]
        print(f"[*] Targeted JIT Cleanup for user: {target_user}")
        revoke_admin(target_user)
    else:
        # If no specific user was passed, sweep the whole system for extra admins
        print("[*] Performing full system Admin sweep...")
        targets = get_all_admins()
        if not targets:
            print("[+] No secondary Admin accounts found.")
        else:
            for user in targets:
                revoke_admin(user)

    # 2. System Sanitation
    wipe_temp_files()
    flush_dns()
    
    print("=== SESSION SECURED ===")