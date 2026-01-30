# Social Login Fix Guide for Production

## Problem

Google and GitHub login not working on production (Azure).

## Root Causes

### 1. Missing FRONTEND_URL Environment Variable

**Issue:** `LOGIN_REDIRECT_URL = FRONTEND_URL` but `FRONTEND_URL` not set on Azure.

**Current Azure Config:**

- ✅ `FRONTEND_ORIGIN=https://todo.hsonspace.id.vn`
- ❌ `FRONTEND_URL` (MISSING!)

**Fix:** Add to Azure App Service Configuration:

```
FRONTEND_URL=https://todo.hsonspace.id.vn/home?token={token}
```

### 2. OAuth Callback URLs

**Google OAuth App:**

- Authorized redirect URIs must include:
  - `https://hson.azurewebsites.net/accounts/google/login/callback/`
  - `https://todo.hsonspace.id.vn/home`

**GitHub OAuth App:**

- Authorization callback URL:
  - `https://hson.azurewebsites.net/accounts/github/login/callback/`

### 3. Settings.py Configuration

Current code (line 130-136):

```python
FRONTEND_URL = os.environ.get("FRONTEND_URL")
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", FRONTEND_URL)
BACKEND_ORIGIN = os.environ.get("BACKEND_ORIGIN")

LOGIN_REDIRECT_URL = FRONTEND_URL
LOGOUT_REDIRECT_URL = FRONTEND_URL
ACCOUNT_LOGOUT_REDIRECT_URL = FRONTEND_URL
```

**Problem:** If `FRONTEND_URL` is None, redirects will fail.

**Fix:** Add fallback in settings.py:

```python
FRONTEND_URL = os.environ.get("FRONTEND_URL") or os.environ.get("FRONTEND_ORIGIN")
```

## Step-by-Step Fix

### Step 1: Update Azure Environment Variables

Add these to Azure App Service → Configuration:

```bash
FRONTEND_URL=https://todo.hsonspace.id.vn/home
```

### Step 2: Update Google OAuth Settings

1. Go to: https://console.cloud.google.com/apis/credentials
2. Select your OAuth 2.0 Client ID
3. Add Authorized redirect URIs:
   ```
   https://hson.azurewebsites.net/accounts/google/login/callback/
   ```

### Step 3: Update GitHub OAuth Settings

1. Go to: https://github.com/settings/developers
2. Select your OAuth App
3. Set Authorization callback URL:
   ```
   https://hson.azurewebsites.net/accounts/github/login/callback/
   ```

### Step 4: Update settings.py (Optional but Recommended)

Add fallback to prevent None redirects:

```python
# Line 130
FRONTEND_URL = os.environ.get("FRONTEND_URL") or os.environ.get("FRONTEND_ORIGIN")
```

### Step 5: Test

1. Click "Login with Google" on https://todo.hsonspace.id.vn/login
2. Should redirect to Google OAuth
3. After auth, should redirect back to https://todo.hsonspace.id.vn/home?token=xxx
4. ProtectedRoute will extract token from URL and save to localStorage

## Current Flow

```
User clicks "Login with Google"
  ↓
Frontend: window.location.href = "https://hson.azurewebsites.net/accounts/google/login/"
  ↓
Backend: Redirect to Google OAuth
  ↓
Google: User authorizes
  ↓
Google: Redirect to https://hson.azurewebsites.net/accounts/google/login/callback/
  ↓
Backend: Process OAuth callback, create user, generate token
  ↓
Backend: Redirect to LOGIN_REDIRECT_URL (FRONTEND_URL) with ?token=xxx
  ↓
Frontend: ProtectedRoute extracts token from URL
  ↓
Frontend: Save token to localStorage
  ↓
User logged in!
```

## Quick Test

After adding `FRONTEND_URL` to Azure, restart the app and test:

```bash
# Should redirect properly
https://todo.hsonspace.id.vn/login → Click Google → Auth → Redirect to /home?token=xxx
```
