import urllib.request
import zlib
import sys
from PIL import Image

# 📋 Τάσο, εδώ υπάρχει URL! Πήγαινε στη γραμμή 7 να το δεις και βάλε το δικό σου:
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
        channel_size = (width * height) // 8
        
        black_buffer = bytearray([0xFF] * channel_size)
        red_buffer = bytearray([0xFF] * channel_size)
        
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
        
        # Δημιουργία έγχρωμης εικόνας preview (Pillow)
        preview_img = Image.new("RGB", (width, height), "white")
        preview_pixels = preview_img.load()
        
        pixel_idx = 0
        stride = width + 1
        
        for y in range(height):
            row_start = y * stride + 1
            for x in range(width):
                if row_start + x < len(decompressed):
                    palette_index = decompressed[row_start + x]
                    if palette_index < len(palette):
                        r, g, b = palette[palette_index]
                        
                        byte_idx = pixel_idx // 8
                        bit_shift = 7 - (pixel_idx % 8)
                        
                        if r > 120 and r > g + 30 and r > b + 30:
                            red_buffer[byte_idx] &= ~(1 << bit_shift)   # Κόκκινο hardware buffer
                            preview_pixels[x, y] = (255, 0, 0)          # Κόκκινο οπτικό preview
                        elif r < 100 and g < 100 and b < 100:
                            black_buffer[byte_idx] &= ~(1 << bit_shift) # Μαύρο hardware buffer
                            preview_pixels[x, y] = (0, 0, 0)            # Μαύρο οπτικό preview
                pixel_idx += 1
                
        final_bytes = black_buffer + red_buffer
        
        with open("image.bin", "wb") as f:
            f.write(final_bytes)
            
        # 🔥 ΑΠΟΘΗΚΕΥΣΗ ΟΠΤΙΚΟΥ PREVIEW: Γέννηση του preview.png
        preview_img.save("preview.png")
            
        print("✅ Επιτυχία! Τα αρχεία image.bin και preview.png δημιουργήθηκαν!")
        
    except Exception as e:
        print(f"❌ Σφάλμα κατά την εκτέλεση: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
