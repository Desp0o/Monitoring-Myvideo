import os
import subprocess
import time
from PIL import Image
import imagehash
import glob
import requests
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo
import json

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
BASE_URL5 = os.getenv("BASE_URL5")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# ✅ სტრიმების სია
base_urls = {
    "BASE_URL": BASE_URL,
    "BASE_URL5": BASE_URL5
}

# JSON ჩატვირთვა
with open("streams.json", "r", encoding="utf-8") as f:
    streams_data = json.load(f)

# Python dict {სახელი: სრული_ლინკი}
streams = {
    item["name"]: f"{base_urls[item['base']]}{item['path']}"
    for item in streams_data
}

# 📷 დროებითი ფაილი
screenshot_file = "stream_frame.jpg"

# 📁 noSignalX.png ფაილების სია ავტომატურად
reference_imgs = glob.glob("noSignal*.png")

# 📸 ffmpeg სქრინშოტის აღება
def take_screenshot(url, out_file):
    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-i", url,
            "-frames:v", "1",
            "-q:v", "2",
            "-loglevel", "error",
            out_file
        ], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# 🧠 შედარება phash-ით against multiple reference images
def is_stream_down_hash(screenshot_path, reference_paths, threshold=15):
    screenshot = Image.open(screenshot_path)
    screenshot_hash = imagehash.phash(screenshot)

    for ref_path in reference_paths:
        ref_img = Image.open(ref_path)
        ref_hash = imagehash.phash(ref_img)
        diff = screenshot_hash - ref_hash
        if diff <= threshold:
            return True
    return False

# 📤 შეტყობინება დისკორდზე
def send_to_discord(message):
    if not DISCORD_WEBHOOK_URL.startswith("https://discord.com"):
        print("⚠️ Discord Webhook URL არ არის სწორად მითითებული.")
        return

    data = {
        "content": message
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("📨 შეტყობინება გაგზავნილია დისკორდზე")
        else:
            print(f"⚠️ Discord error: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Discord exception: {e}")

# დროის შტამპი        
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 🔁 მთავარი მონიტორინგის ციკლი
def monitor_streams():
    timestamp = datetime.now(ZoneInfo("Asia/Tbilisi")).strftime("%Y-%m-%d %H:%M:%S")
    messages = ["⎯ ⎯"]
    messages.append(f"🔄 შემოწმება: {timestamp} ⏰")
    messages.append(" ")
    
    for name, url in streams.items():
        print(f"\n🔍 {name} შემოწმება...")
        success = take_screenshot(url, screenshot_file)
        if not success:
            print(f"{name} ❌ სტრიმი მიუწვდომელია")
            messages.append(f"⚠️ {name}")
            continue

        if is_stream_down_hash(screenshot_file, reference_imgs):
            print(f"{name} 🔴")
            messages.append(f"🔴 {name}")
        else:
            print(f"{name} 🟢")
            # messages.append(f"{name} 🟢")

    if os.path.exists(screenshot_file):
        os.remove(screenshot_file)

    send_to_discord("\n".join(messages))

if __name__ == "__main__":
    monitor_streams()
