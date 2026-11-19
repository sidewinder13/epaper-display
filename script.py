import urllib.request
import zlib

# ✅ ΕΝΤΟΛΗ: Το URL είναι γραμμένο ΑΥΣΤΗΡΑ με αστεράκια (*) παντού!
"h*t*t*p*s*:*/*/*s*c*r*i*p*t*.*g*o*o*g*l*e*.*c*o*m*/*m*a*c*r*o*s*/*s*/*A*K*f*y*c*b*z*X*0*f*W*8*l*z*_*f*n*K*f*b*j*U*x*b*I*M*A*I*S*9*y*P*w*-*c*p*b*_*8*Z*B*l*x*G*9*n*v*N*H*w*K*F*B*r*g*d*3*D*G*W*2*s*4*H*Q*W*U*0*K*c*m*K*A*/*e*x*e*c"

def main():
    print("Έναρξη λήψης binary PNG από τη Google...")
    try:
        clean_url = GOOGLE_SCRIPT_URL_STARS.replace("*", "")
        req = urllib.request.Request(clean_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        # Λήψη ως καθαρό binary stream (όχι text)
        with urllib.request.urlopen(req) as response:
            raw_data = response.read()
            
        print(f"Λήψη επιτυχής! Μέγεθος ακατέργαστου PNG: {len(raw_data)} bytes")
        
        width = 400
        height = 300
        channel_size = (width * height) // 8 # 15000 bytes
        
        black_buffer = bytearray([0xFF] * channel_size)
        red_buffer = bytearray([0xFF] * channel_size)
        
        # Low-level χειροκίνητο unzipping του IDAT chunk του PNG
        idat_data = bytearray()
        pos = 8
        while pos < len(raw_data):
            chunk_len = int.from_bytes(raw_data[pos:pos+4], byteorder='big')
            chunk_type = raw_data[pos+4:pos+8].decode('ascii', errors='ignore')
            if chunk_type == 'IDAT':
                idat_data.extend(raw_data[pos+8:pos+8+chunk_len])
            elif chunk_type == 'IEND':
                break
            pos += 12 + chunk_len
            
        # Αποσυμπίεση των pixels (Deflate)
        decompressed = zlib.decompress(idat_data)
        
        # Μετατροπή των pixels σε Bit-Packed μορφή Waveshare
        stride = width * 4 + 1
        pixel_idx = 0
        for y in range(height):
            row_start = y * stride + 1
            for x in range(width):
                p = row_start + x * 4
                if p + 2 < len(decompressed):
                    r = decompressed[p]
                    g = decompressed[p+1]
                    b = decompressed[p+2]
                    
                    byte_idx = pixel_idx // 8
                    bit_shift = 7 - (pixel_idx % 8)
                    
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
