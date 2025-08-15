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

BASE_URL0 = os.getenv("BASE_URL0")
BASE_URL1 = os.getenv("BASE_URL1")
BASE_URL2 = os.getenv("BASE_URL2")
BASE_URL4 = os.getenv("BASE_URL4")
BASE_URL5 = os.getenv("BASE_URL5")
BASE_URL6 = os.getenv("BASE_URL6")
BASE_URL8 = os.getenv("BASE_URL8")
BASE_URL9 = os.getenv("BASE_URL9")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
WEB_DOMAIN = os.getenv("WEB_DOMAIN")

# ✅ სტრიმების სია
base_urls = {
    "BASE_URL0": BASE_URL0,
    "BASE_URL1": BASE_URL1,
    "BASE_URL2": BASE_URL2,
    "BASE_URL4": BASE_URL4,
    "BASE_URL5": BASE_URL5,
    "BASE_URL6": BASE_URL6,
    "BASE_URL8": BASE_URL8,
    "BASE_URL9": BASE_URL9,
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
        return

    data = {
        "content": message
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        

# დროის შტამპი        
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 🔁 მთავარი მონიტორინგის ციკლი
def monitor_streams():
    timestamp = datetime.now(ZoneInfo("Asia/Tbilisi")).strftime("%Y-%m-%d %H:%M:%S")
    messages = ["⎯ ⎯"]
    messages.append(f"🔄 შემოწმება: {timestamp} ⏰")
    messages.append(" ")

    totalDown = 0
    totalActive = 0
    totalUnreached = 0
    
    for name, url in streams.items():
        base_key = next((item["base"] for item in streams_data if item["name"] == name), None)


        success = take_screenshot(url, screenshot_file)
        if not success:

            messages.append(f"⚠️ {name} \n {WEB_DOMAIN}{name} \n {base_urls.get(base_key)} \n")
            totalUnreached += 1
            continue

        if is_stream_down_hash(screenshot_file, reference_imgs):

            totalDown += 1
            messages.append(f"🔴 {name} \n {WEB_DOMAIN}{name} \n {base_urls.get(base_key)} \n")
        else:

            totalActive += 1
            # messages.append(f"{name} 🟢")

    if os.path.exists(screenshot_file):
        os.remove(screenshot_file)

    messages.append(" ")
    messages.append(f"✅ აქტიური: {totalActive}" )
    messages.append(f"⚠️ მიუწვდომელი: {totalUnreached}" )
    messages.append(f"❌ გათიშული: {totalDown}" )
     
    send_to_discord("\n".join(messages))

while True:
    monitor_streams()
    time.sleep(30 * 60)