import urllib.request

# ✅ ΕΝΤΟΛΗ: Το URL είναι γραμμένο ΑΥΣΤΗΡΑ με αστεράκια (*) παντού!
GOOGLE_SCRIPT_URL_STARS = "h*t*t*p*s*:*/*/*s*c*r*i*p*t*.*g*o*o*g*l*e*.*c*o*m*/*m*a*c*r*o*s*/*s*/*A*K*f*y*c*b*z*X*0*f*W*8*l*z*_*f*n*K*f*b*j*U*x*b*I*M*A*I*S*9*y*P*w*-*c*p*b*_*8*Z*B*l*x*G*9*n*v*N*H*w*K*F*B*r*g*d*3*D*G*W*2*s*4*H*Q*W*U*0*K*c*m*K*A*/*e*x*e*c"

def main():
    print("Έναρξη λήψης raw bytes από τη Google...")
    try:
        clean_url = GOOGLE_SCRIPT_URL_STARS.replace("*", "")
        req = urllib.request.Request(clean_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            csv_text = response.read().decode('utf-8')
        
        png_bytes = [int(x) for x in csv_text.split(',') if x.strip() != '']
        print(f"Λήψη επιτυχής! Μέγεθος αρχείου PNG: {len(png_bytes)} bytes")
        
        width = 400
        height = 300
        channel_size = (width * height) // 8
        
        black_buffer = bytearray([0xFF] * channel_size)
        red_buffer = bytearray([0xFF] * channel_size)
        
        pixel_idx = 0
        data_start = 8 
        
        for i in range(len(png_bytes) - 4):
            if png_bytes[i] == 0x49 and png_bytes[i+1] == 0x44 and png_bytes[i+2] == 0x41 and png_bytes[i+3] == 0x54:
                data_start = i + 4
                break
        
        for i in range(data_start, len(png_bytes) - 2, 3):
            if pixel_idx >= width * height:
                break
                
            r = png_bytes[i]
            g = png_bytes[i+1]
            b = png_bytes[i+2]
            
            byte_idx = pixel_idx // 8
            bit_shift = 7 - (pixel_idx % 8)
            
            if r > 140 and g < 100 and b < 100:
                red_buffer[byte_idx] &= ~(1 << bit_shift)   
            elif r < 100 and g < 100 and b < 100:
                black_buffer[byte_idx] &= ~(1 << bit_shift) 
                
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
