import urllib.request
import zlib

# 📋 Το δικό σου αληθινό Web App URL της Google (Καθαρό, χωρίς αστεράκια)
GOOGLE_SCRIPT_URL = "https://script.googleusercontent.com/macros/echo?user_content_key=AUkAhnT4GV0xXgvAMTwsn85M4KmiXfRAEENM5HmWedc6JAbwn3uBpJWMyVyGZ-fUjVy5JoR6yRm2OqUJtwyVyjL572Rl3XV31KCVomrARSwNos-ORP3PljSb4z7jwQsiJUbtox3KGlthoh6JhMCsMotj4kNqqXt0VfWVa6FWSEEJpF7QXxcoqsNsJ4HB2G4r_v0hq7UDsWVTM1-5U5D9ezo-xWf3PfUbr7-gqRp4ps_t3v3UwzJdVnBULv0c4uUU24-ErNcTo_471uD6ZbAyZlV1_OGN2OHPeQ&lib=Mm1ufKnYuJ-Ps5c1lsDNhXOhMY1gs6E2h"

def main():
    print("Έναρξη λήψης binary PNG από τη Google...")
    try:
        req = urllib.request.Request(GOOGLE_SCRIPT_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            raw_data = response.read()
            
        print(f"Λήψη επιτυχής! Μέγεθος ακατέργαστου PNG: {len(raw_data)} bytes")
        
        width = 400
        height = 300
        channel_size = (width * height) // 8 # 15000 bytes
        
        black_buffer = bytearray([0xFF] * channel_size)
        red_buffer = bytearray([0xFF] * channel_size)
        
        palette = []
        idat_data = bytearray()
        pos = 8
        
        # ✅ ΔΙΟΡΘΩΘΗΚΕ: Ασφαλές, standard σκανάρισμα όλων των IDAT chunks της Google
        while pos < len(raw_data) - 4:
            chunk_len = int.from_bytes(raw_data[pos:pos+4], byteorder='big')
            if pos + 8 + chunk_len > len(raw_data):
                break
                
            chunk_type = raw_data[pos+4:pos+8].decode('ascii', errors='ignore')
            
            if chunk_type == 'PLTE':
                plte_bytes = raw_data[pos+8:pos+8+chunk_len]
                for idx in range(0, len(plte_bytes), 3):
                    palette.append((plte_bytes[idx], plte_bytes[idx+1], plte_bytes[idx+2]))
            elif chunk_type == 'IDAT':
                idat_data.extend(raw_data[pos+8:pos+8+chunk_len])
            elif chunk_type == 'IEND':
                break
            pos += 12 + chunk_len
            
        print(f"Συγκέντρωση δεδομένων IDAT: {len(idat_data)} bytes. Έναρξη αποσυμπίεσης...")
        
        # Αποσυμπίεση ολόκληρου του stream
        decompressed = zlib.decompress(idat_data)
        
        pixel_idx = 0
        stride = width + 1 # 1 byte φίλτρου + 400 bytes pixels
        
        for y in range(height):
            row_start = y * stride + 1
            for x in range(width):
                if row_start + x < len(decompressed):
                    palette_index = decompressed[row_start + x]
                    
                    if palette_index < len(palette):
                        r, g, b = palette[palette_index]
                        
                        byte_idx = pixel_idx // 8
                        bit_shift = 7 - (pixel_idx % 8)
                        
                        # Σωστά hardware thresholds χρωμάτων (0 = Pixel Ενεργό)
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
        exit(1)

if __name__ == "__main__":
    main()
