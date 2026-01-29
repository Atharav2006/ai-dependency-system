# How to Get Your Supabase JWT Token

There are several ways to get your JWT token for testing:

## Method 1: Browser Developer Tools (Easiest)

1. **Open your frontend** (already running at `http://localhost:5173`)
2. **Log in** to your application
3. **Open Browser DevTools**:
   - Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
   - Or right-click → "Inspect"
4. **Go to the Console tab**
5. **Paste this code** and press Enter:
   ```javascript
   // Get the session from Supabase
   const { data } = await window.supabase.auth.getSession()
   console.log('JWT Token:', data.session.access_token)
   copy(data.session.access_token)
   ```
6. The token will be **copied to your clipboard** automatically!

## Method 2: Application Tab (Alternative)

1. Open DevTools (`F12`)
2. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Expand **Local Storage** → `http://localhost:5173`
4. Look for a key like `sb-ltdmrgpvisfyrxwrwbev-auth-token`
5. Copy the `access_token` value from the JSON object

## Method 3: Network Tab

1. Open DevTools (`F12`)
2. Go to **Network** tab
3. Perform any action in your app (like starting a session)
4. Look for API requests to your backend
5. Click on a request
6. Go to **Headers** → **Request Headers**
7. Copy the value after `Authorization: Bearer `

## Method 4: Add a "Copy Token" Button (Recommended for Development)

I can add a button to your frontend that copies the token to clipboard. Would you like me to do that?

## Using the Token

Once you have the token, you can:

### Option A: Use it in the test script
```bash
python test_ai_integration.py
# When prompted, paste the token
```

### Option B: Use it with cURL
```bash
curl -X POST http://localhost:8000/sessions/start \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Option C: Use it in Postman/Thunder Client
1. Create a new request
2. Add header: `Authorization: Bearer YOUR_TOKEN_HERE`
3. Send the request

## Token Expiration

⚠️ **Important**: JWT tokens expire after a certain time (usually 1 hour). If you get authentication errors, get a fresh token using the methods above.

## Quick Test

After getting your token, test it quickly:
```bash
# Replace YOUR_TOKEN with your actual token
curl http://localhost:8000/sessions/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -X POST
```

If you see a session ID in the response, your token is valid! ✅
