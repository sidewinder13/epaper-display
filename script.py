import urllib.request
import sys

# 📋 Τάσο, εδώ υπάρχει URL! Πήγαινε στη γραμμή 5 να το δεις και βάλε το δικό σου:
GOOGLE_SCRIPT_URL = "https://script.googleusercontent.com/macros/echo?user_content_key=AUkAhnT4GV0xXgvAMTwsn85M4KmiXfRAEENM5HmWedc6JAbwn3uBpJWMyVyGZ-fUjVy5JoR6yRm2OqUJtwyVyjL572Rl3XV31KCVomrARSwNos-ORP3PljSb4z7jwQsiJUbtox3KGlthoh6JhMCsMotj4kNqqXt0VfWVa6FWSEEJpF7QXxcoqsNsJ4HB2G4r_v0hq7UDsWVTM1-5U5D9ezo-xWf3PfUbr7-gqRp4ps_t3v3UwzJdVnBULv0c4uUU24-ErNcTo_471uD6ZbAyZlV1_OGN2OHPeQ&lib=Mm1ufKnYuJ-Ps5c1lsDNhXOhMY1gs6E2h"

def main():
    print("Έναρξη λήψης δεδομένων για βαθιά low-level ανάλυση...")
    try:
        req = urllib.request.Request(
            GOOGLE_SCRIPT_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            raw_data = response.read()
            
        print(f"Λήψη επιτυχής! Μέγεθος ακατέργαστου stream: {len(raw_data)} bytes")
        
        # 🔥 ΟΠΤΙΚΟΣ ΕΛΕΓΧΟΣ: Τυπώνουμε τα πρώτα 200 bytes σε μορφή κειμένου για να δούμε τι στέλνει η Google
        print("\n--- ΑΝΑΛΥΣΗ ΚΕΦΑΛΙΔΑΣ (ΠΡΩΤΑ 200 BYTES) ---")
        print(raw_data[:200])
        print("-------------------------------------------\n")
        
        # Σκόπιμο σταμάτημα για να διαβάσουμε το log
        raise Exception("Οπτικός έλεγχος κεφαλίδας ολοκληρώθηκε.")
        
    except Exception as e:
        print(f"❌ Αποτέλεσμα ανάλυσης: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
