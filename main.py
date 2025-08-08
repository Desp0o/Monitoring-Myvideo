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

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# if not BASE_URL.endswith("/"):
#     BASE_URL += "/"

# ✅ სტრიმების სია
streams = {
    "მთავარი": f"{BASE_URL}gncc-mtavari/index.m3u8",
    "TV პირველი": f"{BASE_URL}gncc-pirvelitv/index.m3u8",
    "ფორმულა": f"{BASE_URL}gncc-formula/index.m3u8",
    "GPB": f"{BASE_URL}gncc-gpbtv/index.m3u8",
    "Euronews":f"{BASE_URL}gncc-euronewsgeorgia/index.m3u8",
    "იმედი": f"{BASE_URL}gncc-imedi/index.m3u8",
    "კავკასია":f"{BASE_URL}gncc-caucasia/index.m3u8",
    "პალიტრა":f"{BASE_URL}gncc-palitra/index.m3u8",
    "Altinfo": f"{BASE_URL}gncc-altinfo/index.m3u8",
    "მაესტრო": f"{BASE_URL}gncc-maestrotv/index.m3u8",
    "რუსთავი 2":f"{BASE_URL}gncc-rustavi2hqnew/index.m3u8",
    "პოსტTv":f"{BASE_URL}gncc-postv/index.m3u8",
    "აჭარა":f"{BASE_URL}gncc-adjara/index.m3u8",
    "ობიექტრივი":f"{BASE_URL}gncc-obiektivi/index.m3u8",
    "რადიო იმედი":f"{BASE_URL}gncc-radioimedi/index.m3u8",
    "Abkhaz":f"{BASE_URL}gncc-abkhaz/index.m3u8",
    "სფერო TV":f"{BASE_URL}gncc-sferotv/index.m3u8",
    "tv 24":f"{BASE_URL}gncc-tv24/index.m3u8",
    "რიონი": f"{BASE_URL}gncc-rioni/index.m3u8",
    "დია TV": f"{BASE_URL}gncc-diatv/index.m3u8",
    "tv 25": f"{BASE_URL}gncc-tv25/index.m3u8",
    "ბათუნუ": f"{BASE_URL}gncc-batumitv/index.m3u8",
    "გურია tv": f"{BASE_URL}gncc-guriatv/index.m3u8",
    "Paravan tv": f"{BASE_URL}gncc-parvanatv/index.m3u8",
    "აგრო tv": f"{BASE_URL}gncc-argotv/index.m3u8",
    "მეგა tv": f"{BASE_URL}gncc-megatv/index.m3u8",
    "მარნეული": f"{BASE_URL}gncc-marneulitv/index.m3u8",
    "ლილო tv": f"{BASE_URL}gncc-lilotv/index.m3u8",
    "სდასუ tv": f"{BASE_URL}gncc-sdasutv/index.m3u8",
    "თრიალეთი": f"{BASE_URL}gncc-trialeti/index.m3u8",
    "ქართული":f"{BASE_URL}gncc-qartuli/index.m3u8",
    "ქართული არხი": f"{BASE_URL}gncc-kartuliarkhi/index.m3u8",
    "დრო TV":f"{BASE_URL}gncc-drotv/index.m3u8",
    "TVmax": f"{BASE_URL}gncc-tvmax/index.m3u8",
    "plus tv": f"{BASE_URL}gncc-plustv/index.m3u8",
    "BMG": f"{BASE_URL}gncc-bmg/index.m3u8",
    "GGTV": f"{BASE_URL}gncc-gttv/index.m3u8",
    "თანამგზავრი": f"{BASE_URL}gncc-tanamgzavri/index.m3u8",
    "nwbctv":f"{BASE_URL}gncc-nwbctv/index.m3u8",
    "odishi": f"{BASE_URL}gncc-odishi/index.m3u8",
    "ilontv": f"{BASE_URL}gncc-ilontv/index.m3u8",
    "gurjaani": f"{BASE_URL}gncc-gurjaani/index.m3u8",
    "qvemo qartli":f"{BASE_URL}gncc-qvemoqartli/index.m3u8",
    "tv12":f"{BASE_URL}gncc-tv12/index.m3u8",
    "tvmze":f"{BASE_URL}gncc-tvmze/index.m3u8",
    "toktv":f"{BASE_URL}gncc-toktv/index.m3u8",
    "atv12parvana":f"{BASE_URL}gncc-atv12parvana/index.m3u8",
    "გირჩი tv":f"{BASE_URL}gncc-girchitv/index.m3u8",
    "ეგრისი tv":f"{BASE_URL}gncc-egrisitv/index.m3u8",
    "gmtv": f"{BASE_URL}gncc-gmtv/index.m3u8",
    "კოლხეთი 89": f"{BASE_URL}gncc-kolkheti89/index.m3u8",
    "ბორჯომი tv": f"{BASE_URL}gncc-borjomitv/index.m3u8",
    "tv9": f"{BASE_URL}gncc-tv9/index.m3u8",
    "TV მონიტორინგი": f"{BASE_URL}gncc-tvmonitoring/index.m3u8",
    "სეზონი Tv":f"{BASE_URL}gncc-sezonitv/index.m3u8",
    "იმერვიზია": f"{BASE_URL}gncc-imervizia/index.m3u8",
    "ბოლნელი": f"{BASE_URL}gncc-bolneli/index.m3u8",
    "სტარვიზია": f"{BASE_URL}gncc-starvision/index.m3u8",
    "TV ზარი": f"{BASE_URL}gncc-tvzari/index.m3u8",
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
