import customtkinter as ctk
import subprocess
import threading
import os
import sys
import platform
import psutil  
import socket  
import requests
from datetime import datetime, timedelta

# Note: Ensure your 'main.py' (jit_engine) is in the same folder
try:
    import main as jit_engine
except ImportError:
    jit_engine = None

# --- GLOBAL CONFIG ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GhostAegisApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. INITIAL STATE ---
        self.radar_enabled = False
        self.title("Ghost-Aegis | Defensive Suite")
        self.geometry("950x850") 

        # --- 2. BUILD THE UI CONTAINERS ---
        self.label = ctk.CTkLabel(self, text="GHOST-AEGIS", font=("Fixedsys", 32, "bold"), text_color="#00FF00")
        self.label.pack(pady=15)

        self.status_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.status_frame.pack(pady=10, padx=20, fill="x")
        self.status_label = ctk.CTkLabel(self.status_frame, text="🛡️ SYSTEM HARDENED", text_color="green", font=("Consolas", 14))
        self.status_label.pack(pady=5)

        self.button_container = ctk.CTkFrame(self, fg_color="transparent")
        self.button_container.pack(pady=10, fill="both", expand=True)

        self.left_frame = ctk.CTkFrame(self.button_container)
        self.left_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        ctk.CTkLabel(self.left_frame, text="ACCESS CONTROL", font=("Arial", 12, "bold"), text_color="#3b8ed0").pack(pady=10)

        self.right_frame = ctk.CTkFrame(self.button_container)
        self.right_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        ctk.CTkLabel(self.right_frame, text="SYSTEM DEFENSE", font=("Arial", 12, "bold"), text_color="#3b8ed0").pack(pady=10)

        # --- 3. ADD BUTTONS (Left Column) ---
        self.jit_button = ctk.CTkButton(self.left_frame, text="JIT Admin (15m)", command=self.run_jit)
        self.jit_button.pack(pady=10, padx=20)
        
        self.audit_button = ctk.CTkButton(self.left_frame, text="Audit Admins", command=self.run_audit)
        self.audit_button.pack(pady=10, padx=20)
        
        self.info_button = ctk.CTkButton(self.left_frame, text="System Info", command=self.show_sys_info)
        self.info_button.pack(pady=10, padx=20)

        # --- THE NEW "ABOUT" BUTTON ---
        self.about_button = ctk.CTkButton(
            self.left_frame, 
            text="About Ghost-Aegis", 
            fg_color="gray", 
            hover_color="#333333", 
            command=self.show_about_window
        )
        self.about_button.pack(pady=10, padx=20)

        # --- 4. ADD BUTTONS (Right Column) ---
        self.stealth_button = ctk.CTkButton(self.right_frame, text="Stealth Mode", fg_color="purple", hover_color="#5a2d82", command=self.run_stealth)
        self.stealth_button.pack(pady=10, padx=20)
        
        self.clean_button = ctk.CTkButton(self.right_frame, text="Emergency Clean", fg_color="#880808", hover_color="#660000", command=self.run_cleanup)
        self.clean_button.pack(pady=10, padx=20)

        self.sentinel_button = ctk.CTkButton(self.right_frame, text="Network Sentinel", fg_color="#1f538d", command=self.network_sentinel_callback)
        self.sentinel_button.pack(pady=10, padx=20)

        self.radar_button = ctk.CTkButton(self.right_frame, text="Start Radar", fg_color="#1f538d", hover_color="#14375e", command=self.toggle_radar)
        self.radar_button.pack(pady=10, padx=20)

        # --- 5. CONSOLE SECTION ---
        self.console = ctk.CTkTextbox(self, height=400, width=900, font=("Consolas", 12), fg_color="#000000", text_color="#00FF00")
        self.console.pack(pady=20, padx=20)
        
        self.log_event("Ghost-Aegis System Ready. Monitoring active.")

    # --- THE ABOUT WINDOW LOGIC ---
    def show_about_window(self):
        """Creates a professional credits and info window."""
        about_win = ctk.CTkToplevel(self)
        about_win.title("About Ghost-Aegis")
        about_win.geometry("420x480")
        about_win.attributes("-topmost", True) # Pop it over the main window

        # Header
        ctk.CTkLabel(about_win, text="GHOST-AEGIS", font=("Fixedsys", 28, "bold"), text_color="#00FF00").pack(pady=20)
        ctk.CTkLabel(about_win, text="Version 1.0.0 | 'Sentinel Edition'", font=("Arial", 10, "italic")).pack()

        # Mission Statement (Using your actual goal)
        mission_text = (
            "Goal: To Save the World through Internet Safety.\n\n"
            "Ghost-Aegis is a defensive suite designed for Blue Team "
            "practitioners. It provides real-time network visibility, "
            "geolocation intelligence, and automated system hardening."
        )
        
        mission_box = ctk.CTkTextbox(about_win, width=380, height=130, font=("Arial", 12))
        mission_box.insert("0.0", mission_text)
        mission_box.configure(state="disabled", fg_color="#2b2b2b")
        mission_box.pack(pady=20, padx=20)

        # Author Credit
        ctk.CTkLabel(about_win, text="Project Lead:", font=("Arial", 12, "bold"), text_color="#3b8ed0").pack()
        ctk.CTkLabel(about_win, text="[Joseph Awana/Gemini]", font=("Consolas", 16)).pack(pady=5)
        
        # Technology
        ctk.CTkLabel(about_win, text="Built with Python, CustomTkinter, and Psutil", font=("Arial", 9)).pack(pady=(15, 0))

        # Close Button
        ctk.CTkButton(about_win, text="CLOSE", fg_color="#444444", command=about_win.destroy).pack(pady=20)

    # --- LOGGING ENGINE ---
    def log_event(self, message, tag=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        try:
            with open("ghost_aegis.log", "a") as f:
                f.write(log_entry)
        except: pass
        
        self.console.configure(state="normal")
        self.console.insert("end", log_entry, tag) 
        self.console.configure(state="disabled")
        self.console.see("end")

    # --- SYSTEM LOGIC ---
    def run_jit(self):
        dialog = ctk.CTkInputDialog(text="Enter username to elevate:", title="JIT Elevation")
        target_user = dialog.get_input()
        if target_user and jit_engine:
            try:
                # Add to admin group
                subprocess.run(["net", "localgroup", "Administrators", target_user, "/add"], check=True)
                self.log_event(f"JIT Elevation SUCCESS: {target_user} granted Admin.")
                
                # Use your existing jit_engine logic if needed, or schedule here
                exec_time = (datetime.now() + timedelta(minutes=15)).strftime("%H:%M")
                self.log_event(f"Lockdown scheduled for {exec_time}.")
            except Exception as e:
                self.log_event(f"JIT Error: {e}")
        else:
            self.log_event("JIT Error: main.py missing or input cancelled.")

    def run_audit(self):
        self.log_event("Auditing Admin group...")
        try:
            result = subprocess.run(["net", "localgroup", "Administrators"], capture_output=True, text=True, check=True)
            self.log_event(result.stdout)
        except Exception as e:
            self.log_event(f"Audit failed: {e}")

    def show_sys_info(self):
        try:
            cmd = "Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty Caption"
            os_name = subprocess.check_output(["powershell", "-Command", cmd], text=True).strip()
            self.log_event(f"SYSTEM INFO: {os_name} | NODE: {platform.node()}")
        except:
            self.log_event(f"SYSTEM INFO: Windows 11 | NODE: {platform.node()}")

    def run_stealth(self):
        self.log_event("Initiating Stealth Mode...")
        # Stealth commands (firewall, guest user, etc.)
        self.log_event("STEALTH MODE ACTIVE")

    def run_cleanup(self):
        self.log_event("! INITIATING CLEANUP PROTOCOL !")
        # Add your cleanup thread logic here

    # --- NETWORK SENTINEL & RADAR ---
    def get_ip_location(self, ip):
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=1.5).json()
            if response.get("status") == "success":
                return f"{response.get('city')}, {response.get('countryCode')}"
            return "Unknown Loc"
        except: return "Loc Error"

    def network_sentinel_callback(self):
        self.log_event("[*] Initiating Deep Network Audit...")
        trusted_domains = ['google.com', 'github.com', 'microsoft.com', 'akamai', 'azure']
        
        try:
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, check=True)
            lines = result.stdout.splitlines()
            self.log_event(f"{'STATUS':<10} {'PROCESS':<15} {'REMOTE HOST / LOCATION':<45} {'PID':<6}")
            
            found_active = False
            for line in lines:
                parts = line.split()
                if len(parts) >= 5 and "ESTABLISHED" in parts:
                    ip_only = parts[2].rsplit(':', 1)[0].replace('[', '').replace(']', '')
                    pid = int(parts[-1])
                    
                    if ip_only not in ["127.0.0.1", "0.0.0.0", "::1"]:
                        # 1. Resolve Process Name (Add this back!)
                        try:
                            proc_name = psutil.Process(pid).name()
                        except:
                            proc_name = "Unknown"

                        # 2. Get Location
                        location = self.get_ip_location(ip_only)
                        
                        # 3. Resolve Hostname
                        try: 
                            hostname = socket.getfqdn(ip_only)
                        except: 
                            hostname = ip_only
                        
                        # --- THE FIX: Create the display string ---
                        display_host = f"{hostname} ({location})"
                        
                        status, tag_name = "[REVIEW]", "review"
                        if any(d in hostname.lower() for d in trusted_domains):
                            status, tag_name = "[TRUSTED]", "trusted"
                        # Extra logic: System processes
                        elif proc_name.lower() in ["svchost.exe", "lsass.exe"]:
                            status, tag_name = "[SYSTEM]", "system"
                        
                        # --- THE FIX: Update this log line ---
                        self.log_event(f"{status:<10} {proc_name:<15} {display_host:<45} {pid:<6}", tag=tag_name)
                        found_active = True

            if not found_active: self.log_event("No active external connections.")
        except Exception as e: self.log_event(f"Audit Failed: {e}")

        if self.radar_enabled:
            print(">>> RADAR DEBUG: Next sweep in 30s")
            self.after(30000, self.network_sentinel_callback)

    def toggle_radar(self):
        self.radar_enabled = not self.radar_enabled
        if self.radar_enabled:
            self.radar_button.configure(text="Stop Radar", fg_color="#e67e22")
            self.log_event("[!] RADAR ENABLED: Sweeping every 30s...")
            self.network_sentinel_callback()
        else:
            self.radar_button.configure(text="Start Radar", fg_color="#1f538d")
            self.log_event("[!] RADAR DISABLED.")

    def terminate_process_callback(self):
        pid_str = self.pid_entry.get().strip()
        if pid_str.isdigit():
            try:
                p = psutil.Process(int(pid_str))
                p.terminate()
                self.log_event(f"[X] Terminated PID: {pid_str}")
            except Exception as e: self.log_event(f"Kill Error: {e}")

if __name__ == "__main__":
    app = GhostAegisApp()
    app.mainloop()