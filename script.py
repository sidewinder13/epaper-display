import urllib.request
import zlib
import sys

# 📋 Τάσο, εδώ υπάρχει URL! Πήγαινε στη γραμμή 6 να το δεις και βάλε το δικό σου:
GOOGLE_SCRIPT_URL = "https://script.googleusercontent.com/macros/echo?user_content_key=AUkAhnT4GV0xXgvAMTwsn85M4KmiXfRAEENM5HmWedc6JAbwn3uBpJWMyVyGZ-fUjVy5JoR6yRm2OqUJtwyVyjL572Rl3XV31KCVomrARSwNos-ORP3PljSb4z7jwQsiJUbtox3KGlthoh6JhMCsMotj4kNqqXt0VfWVa6FWSEEJpF7QXxcoqsNsJ4HB2G4r_v0hq7UDsWVTM1-5U5D9ezo-xWf3PfUbr7-gqRp4ps_t3v3UwzJdVnBULv0c4uUU24-ErNcTo_471uD6ZbAyZlV1_OGN2OHPeQ&lib=Mm1ufKnYuJ-Ps5c1lsDNhXOhMY1gs6E2h"

def main():
    print("Έναρξη λήψης Signed Bytes text stream από τη Google...")
    try:
        req = urllib.request.Request(GOOGLE_SCRIPT_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            csv_text = response.read().decode('utf-8')
        
        signed_bytes = [int(x) for x in csv_text.split(',') if x.strip() != '']
        
        png_bytes = bytearray()
        for b in signed_bytes:
            if b < 0:
                png_bytes.append(b + 256)
            else:
                png_bytes.append(b)
                
        width = 400
        height = 300
        
        palette = []
        idat_data = bytearray()
        pos = 8
        
        while pos < len(png_bytes) - 4:
            chunk_len = int.from_bytes(png_bytes[pos:pos+4], byteorder='big')
            if pos + 8 + chunk_len > len(png_bytes):
                break
            chunk_type = png_bytes[pos+4:pos+8]
            
            if chunk_type == b'PLTE':
                plte_bytes = png_bytes[pos+8:pos+8+chunk_len]
                for idx in range(0, len(plte_bytes), 3):
                    palette.append((plte_bytes[idx], plte_bytes[idx+1], plte_bytes[idx+2]))
            elif chunk_type == b'IDAT':
                idat_data.extend(png_bytes[pos+8:pos+8+chunk_len])
            elif chunk_type == b'IEND':
                break
            pos += 12 + chunk_len
            
        decompressed = zlib.decompress(idat_data)
        
        print("\n--- ΑΝΑΛΥΣΗ ΧΡΩΜΑΤΩΝ ΠΑΛΕΤΑΣ (PLTE) ---")
        print(f"Βρέθηκαν {len(palette)} χρώματα στην παλέτα της Google:")
        for i, color in enumerate(palette[:20]): # Τυπώνουμε τα πρώτα 20 χρώματα
            print(f"Χρώμα {i}: R={color[0]}, G={color[1]}, B={color[2]}")
        print("----------------------------------------\n")
        
        raise Exception("Low-level ανάλυση χρωμάτων ολοκληρώθηκε.")
        
    except Exception as e:
        print(f"❌ Αποτέλεσμα ανάλυσης: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
