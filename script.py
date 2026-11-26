import os
import requests
from PIL import Image

# 📢 ΤΑΣΟ, ΒΑΛΕ ΕΔΩ ΤΟ ΚΑΘΑΡΟ Web App URL ΣΟΥ (Αυτό που τελειώνει σε /exec)
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzX0fW8lz_fnKfbjUxbIMAIS9yPw-cpb_8ZBlxG9nvNHwdKFBrgd3DGW2s4HQWU0KcmKA/exec"
BIN_PATH = "image.bin"
TEMP_PNG = "temp_slide.png"
TEMP_BIN = "temp_image.bin"

print("🚀 Έναρξη Server-Side Python Guard (Decimal Byte Array Parser)...")

# 📡 1. Λήψη δεδομένων από το Google Script Proxy
try:
    print("📡 Λήψη δεδομένων από το Google Slide Proxy...")
    response = requests.get(GOOGLE_SCRIPT_URL, timeout=30)
    if response.status_code == 200:
        raw_text = response.text.strip()
        print("🔬 Μετατροπή Decimal String σε Raw Image Bytes...")
        
        try:
            # Σπάμε το κείμενο στα κόμματα και μετατρέπουμε κάθε αριθμό σε byte (0-255)
            # Αν ο αριθμός είναι αρνητικός (π.χ. -119), η C++ / Python τον μετατρέπει σε 256 + X
            byte_list = []
            for num_str in raw_text.split(','):
                val = int(num_str.strip())
                if val < 0:
                    val = 256 + val
                byte_list.append(val)
                
            image_bytes = bytes(byte_list)
        except Exception as parse_err:
            print(f"❌ Αποτυχία low-level ανάλυσης των αριθμών: {str(parse_err)}")
            exit(1)
            
        # Επιβεβαίωση Magic Bytes PNG μετά την ανασύνθεση
        if not image_bytes.startswith(b'\x89PNG'):
            print("❌ Low-Level Σφάλμα: Τα ανασυντεθειμένα bytes δεν αντιστοιχούν σε PNG!")
            exit(1)
            
        with open(TEMP_PNG, "wb") as f:
            f.write(image_bytes)
        print("✅ Η εικόνα PNG ανασυντέθηκε και αποθηκεύτηκε επιτυχώς.")
    else:
        print(f"❌ Σφάλμα Google Proxy HTTP Code: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Αποτυχία σύνδεσης στο Google Proxy: {str(e)}")
    exit(1)

# 🎨 2. Επεξεργασία και Μετατροπή σε 3-Color Bytes
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

# 🔬 3. Έλεγχος και Σύγκριση Bytes
if os.path.exists(BIN_PATH):
    print("🔬 Ανιχνεύθηκε υπάρχον αρχείο image.bin. Έναρξη σύγκρισης bytes...")
    try:
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
    except Exception as e:
        print(f"⚠️ Προειδοποίηση κατά την ανάγνωση του αρχείου: {str(e)}")
else:
    print("📢 FIRST RUN: Το αρχείο image.bin δεν υπάρχει στον σέρβερ. Θα δημιουργηθεί τώρα!")

# 💾 4. Αντικατάσταση ή δημιουργία του επίσημου αρχείου
try:
    if os.path.exists(TEMP_BIN):
        if os.path.exists(BIN_PATH):
            os.remove(BIN_PATH)
        os.rename(TEMP_BIN, BIN_PATH)
        print("💾 Το αρχείο image.bin αποθηκεύτηκε επιτυχώς στον σέρβερ!")
except Exception as e:
    print(f"❌ Αποτυχία low-level αποθήκευσης αρχείου: {str(e)}")
    exit(1)

if os.path.exists(TEMP_PNG): 
    os.remove(TEMP_PNG)

print("🏁 Server-Side Guard ολοκληρώθηκε.")
