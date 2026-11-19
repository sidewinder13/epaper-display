import urllib.request
import io
import sys
from PIL import Image

# 📋 Τάσο, εδώ υπάρχει URL! Πήγαινε στη γραμμή 7 να το δεις και βάλε το δικό σου:
GOOGLE_SCRIPT_URL = "https://script.googleusercontent.com/macros/echo?user_content_key=AUkAhnT4GV0xXgvAMTwsn85M4KmiXfRAEENM5HmWedc6JAbwn3uBpJWMyVyGZ-fUjVy5JoR6yRm2OqUJtwyVyjL572Rl3XV31KCVomrARSwNos-ORP3PljSb4z7jwQsiJUbtox3KGlthoh6JhMCsMotj4kNqqXt0VfWVa6FWSEEJpF7QXxcoqsNsJ4HB2G4r_v0hq7UDsWVTM1-5U5D9ezo-xWf3PfUbr7-gqRp4ps_t3v3UwzJdVnBULv0c4uUU24-ErNcTo_471uD6ZbAyZlV1_OGN2OHPeQ&lib=Mm1ufKnYuJ-Ps5c1lsDNhXOhMY1gs6E2h"

def main():
    print("Έναρξη λήψης δεδομένων μέσω Pillow Pipeline...")
    try:
        # Αποστολή αιτήματος με πλήρη browser προσομοίωση για να μην φάμε block
        req = urllib.request.Request(
            GOOGLE_SCRIPT_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req) as response:
            raw_data = response.read()
            
        print(f"Λήψη επιτυχής! Μέγεθος ακατέργαστου stream: {len(raw_data)} bytes")
        
        # 🔥 ΕΡΓΟΣΤΑΣΙΑΚΟ UNZIPPING: Η Pillow ανοίγει το stream εγγενώς
        img = Image.open(io.BytesIO(raw_data))
        img = img.resize((400, 300)).convert("RGB") # Εξασφάλιση True RGB (0-255)
        pixels = img.load()
        print("Η αποσυμπίεση των pixels ολοκληρώθηκε με επιτυχία!")
        
        width = 400
        height = 300
        channel_size = (width * height) // 8 # 15000 bytes
        
        black_buffer = bytearray([0xFF] * channel_size)
        red_buffer = bytearray([0xFF] * channel_size)
        
        # Low-level Bit Packing απευθείας από τα True RGB pixels της Pillow
        pixel_idx = 0
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                byte_idx = pixel_idx // 8
                bit_shift = 7 - (pixel_idx % 8)
                
                # Αυστηρά και σίγουρα hardware thresholds χρωμάτων (0 = Pixel Ενεργό)
                if r > 140 and g < 100 and b < 100:
                    red_buffer[byte_idx] &= ~(1 << bit_shift)   # Κόκκινο
                elif r < 100 and g < 100 and b < 100:
                    black_buffer[byte_idx] &= ~(1 << bit_shift) # Μαύρο
                    
                pixel_idx += 1
                
        final_bytes = black_buffer + red_buffer
        
        with open("image.bin", "wb") as f:
            f.write(final_bytes)
            
        print("✅ Επιτυχία! Το αρχείο image.bin (30.000 bytes) δημιουργήθηκε!")
        
    except Exception as e:
        print(f"❌ Σφάλμα κατά την εκτέλεση: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
