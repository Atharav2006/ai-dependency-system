"""
Simple script to help you get your JWT token from the browser
"""

print("""
╔══════════════════════════════════════════════════════════════════════╗
║              GET YOUR SUPABASE JWT TOKEN                             ║
╔══════════════════════════════════════════════════════════════════════╗

Follow these steps:

1. Open your browser and go to: http://localhost:5173
   
2. Log in to your application
   
3. Open Browser DevTools (Press F12)
   
4. Go to the CONSOLE tab
   
5. Copy and paste this code, then press Enter:
   
   ┌────────────────────────────────────────────────────────────────┐
   │ (async () => {                                                 │
   │   const { data } = await window.supabase.auth.getSession();    │
   │   if (data?.session?.access_token) {                           │
   │     console.log('✅ Token copied to clipboard!');              │
   │     console.log('Token:', data.session.access_token);          │
   │     navigator.clipboard.writeText(data.session.access_token);  │
   │   } else {                                                     │
   │     console.log('❌ Not logged in. Please log in first.');     │
   │   }                                                            │
   │ })()                                                           │
   └────────────────────────────────────────────────────────────────┘

6. The token will be automatically copied to your clipboard!

7. Come back here and paste it when prompted.

══════════════════════════════════════════════════════════════════════

Alternative: If the above doesn't work, try this simpler version:

   ┌────────────────────────────────────────────────────────────────┐
   │ localStorage.getItem('sb-ltdmrgpvisfyrxwrwbev-auth-token')     │
   └────────────────────────────────────────────────────────────────┘

   Then copy the "access_token" value from the JSON.

══════════════════════════════════════════════════════════════════════
""")

token = input("\n📋 Paste your JWT token here: ").strip()

if not token:
    print("\n❌ No token provided. Exiting.")
    exit(1)

if len(token) < 100:
    print("\n⚠️  Warning: This token looks too short. Make sure you copied the full token.")
    confirm = input("Continue anyway? (y/n): ").strip().lower()
    if confirm != 'y':
        exit(1)

# Save to a temporary file for easy access
with open('.test_token', 'w') as f:
    f.write(token)

print("\n✅ Token saved to .test_token file")
print("\nYou can now run the test script:")
print("  python test_ai_integration.py")
print("\nOr use it with cURL:")
print(f'  curl -X POST http://localhost:8000/sessions/start -H "Authorization: Bearer {token[:20]}..."')
