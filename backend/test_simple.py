import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

candidates = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

print("START_TEST")
for m in candidates:
    try:
        model = genai.GenerativeModel(m)
        model.generate_content("Hi")
        print(f"MODEL {m}: SUCCESS")
    except Exception as e:
        err = str(e)
        if "404" in err:
            print(f"MODEL {m}: 404 NOT_FOUND")
        elif "429" in err:
            print(f"MODEL {m}: 429 QUOTA_EXCEEDED")
        elif "400" in err:
             print(f"MODEL {m}: 400 BAD_REQUEST - {err[:50]}")
        else:
            print(f"MODEL {m}: ERROR {err[:50]}")
print("END_TEST")
