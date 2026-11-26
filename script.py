
import os
import requests
from PIL import Image

# 📋 Τάσο, εδώ υπάρχει URL! Πήγαινε στη γραμμή 7 να το δεις και βάλε το δικό σου:
GOOGLE_SCRIPT_URL = "https://script.googleusercontent.com/macros/echo?user_content_key=AUkAhnT4GV0xXgvAMTwsn85M4KmiXfRAEENM5HmWedc6JAbwn3uBpJWMyVyGZ-fUjVy5JoR6yRm2OqUJtwyVyjL572Rl3XV31KCVomrARSwNos-ORP3PljSb4z7jwQsiJUbtox3KGlthoh6JhMCsMotj4kNqqXt0VfWVa6FWSEEJpF7QXxcoqsNsJ4HB2G4r_v0hq7UDsWVTM1-5U5D9ezo-xWf3PfUbr7-gqRp4ps_t3v3UwzJdVnBULv0c4uUU24-ErNcTo_471uD6ZbAyZlV1_OGN2OHPeQ&lib=Mm1ufKnYuJ-Ps5c1lsDNhXOhMY1gs6E2h"

BIN_PATH = "image.bin"
TEMP_PNG = "temp_slide.png"
TEMP_BIN = "temp_image.bin"



print("🚀 Έναρξη Server-Side Python Guard...")

# Low-level συνάρτηση αφαίρεσης αστερίσκων
clean_url = GOOGLE_SCRIPT_URL.replace('*', '')

# 📡 Λήψη των bytes της εικόνας από το Google Script Proxy
try:
    print("📡 Λήψη εικόνας από το Google Slide Proxy...")
    response = requests.get(clean_url, timeout=30)
    if response.status_code == 200:
        with open(TEMP_PNG, "wb") as f:
            f.write(response.content)
        print("✅ Η εικόνα κατέβηκε επιτυχώς.")
    else:
        print(f"❌ Σφάλμα Google Proxy HTTP Code: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Αποτυχία σύνδεσης στο Google Proxy: {str(e)}")
    exit(1)

# 🎨 Επεξεργασία και Μετατροπή σε 3-Color Bytes (Black/White/Red)
try:
    img = Image.open(TEMP_PNG).convert("RGB")
    img = img.resize((400, 300))
    new_bytes = bytearray()
    
    for y in range(300):
        for x in range(400):
            r, g, b = img.getpixel((x, y))
            if r > 200 and g < 50 and b < 50:  # Κόκκινο
                new_bytes.append(2)
            elif r > 150 and g > 150 and b > 150:  # Λευκό
                new_bytes.append(1)
            else:  # Μαύρο
                new_bytes.append(0)
                
    with open(TEMP_BIN, "wb") as f:
        f.write(new_bytes)
        
except Exception as e:
    print(f"❌ Αποτυχία low-level επεξεργασίας εικόνας: {str(e)}")
    if os.path.exists(TEMP_PNG): os.remove(TEMP_PNG)
    exit(1)

# 🔬 Σύγκριση Bytes με το προηγούμενο αρχείο (Η Λογική του Server Guard)
if os.path.exists(BIN_PATH):
    print("🔬 Ανιχνεύθηκε υπάρχον αρχείο image.bin. Έναρξη σύγκρισης bytes...")
    with open(BIN_PATH, "rb") as f:
        old_bytes = f.read()
        
    with open(TEMP_BIN, "rb") as f:
        current_bytes = f.read()
        
    if old_bytes == current_bytes:
        print("🛑 MATCH: Τα bytes είναι ολόιδια! Η ατζέντα δεν άλλαξε.")
        print("Locks: Ακύρωση εγγραφής. Το image.bin ΔΕΝ θα αντικατασταθεί.")
        if os.path.exists(TEMP_PNG): os.remove(TEMP_PNG)
        if os.path.exists(TEMP_BIN): os.remove(TEMP_BIN)
        exit(0)
    else:
        print("📢 NEW DATA: Ανιχνεύθηκαν αλλαγές στα pixels της ατζέντας!")

os.replace(TEMP_BIN, BIN_PATH)
print("💾 Το νέο image.bin αποθηκεύτηκε επιτυχώς!")

if os.path.exists(TEMP_PNG): 
    os.remove(TEMP_PNG)

print("🏁 Server-Side Guard ολοκληρώθηκε.")





