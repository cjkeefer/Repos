# Calendar Integration Setup Guide

This guide will help you set up both Google Calendar and Outlook Calendar integration.

## Google Calendar Setup

### Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a Project" → "New Project"
3. Name it "My App Calendar"
4. Go to "APIs & Services" → "Library"
5. Search for "Google Calendar API" and enable it
6. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
7. Choose "Web application"
8. Add authorized redirect URIs:
   - `http://localhost:5173`
   - `http://localhost:5173/calendar`
9. Copy your **Client ID**

### Step 2: Add Client ID to Frontend

1. Open `frontend/.env.local`
2. Replace `YOUR_GOOGLE_CLIENT_ID` with your actual Client ID:
   ```
   VITE_GOOGLE_CLIENT_ID=YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com
   ```

### Step 3: Test

1. Navigate to the Calendar page
2. Click "Sign in with Google"
3. You should see your calendar events

---

## Outlook Calendar Setup

### Step 1: Create Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Name: "My App Calendar"
5. Supported account types: "Accounts in any organizational directory (Any Azure AD directory - Multitenant)"
6. Redirect URI: 
   - Platform: Web
   - URI: `http://localhost:5173`
7. Click "Register"

### Step 2: Configure API Permissions

1. Go to "API permissions"
2. Click "Add a permission" → "Microsoft Graph"
3. Select "Delegated permissions"
4. Search and add:
   - `Calendar.Read`
   - `Calendar.ReadWrite`
   - `user.read`
5. Click "Grant admin consent"

### Step 3: Create Client Secret (Optional)

1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Copy the secret value

### Step 4: Add Client ID to Frontend

1. Open `frontend/.env.local`
2. Replace `YOUR_AZURE_CLIENT_ID` with your actual Client ID:
   ```
   VITE_AZURE_CLIENT_ID=YOUR_ACTUAL_CLIENT_ID
   ```

### Step 5: Test

1. Navigate to the Calendar page
2. Click the "Outlook Calendar" tab
3. Click "Sign in with Microsoft"
4. Authorize the app
5. You should see your calendar events

---

## Frontend Installation

```bash
cd frontend
npm install
npm run dev
```

Then navigate to `http://localhost:5173/calendar`

---

## Features

- **Google Calendar Integration**: View Google Calendar events
- **Outlook Integration**: View Microsoft Outlook/Office 365 calendar events
- **Tab Navigation**: Switch between Google and Outlook calendars
- **Event Display**: View upcoming events with full details
- **Responsive Design**: Works on desktop and mobile

---

## Troubleshooting

### "Client ID not configured"
- Make sure you have `.env.local` in the frontend folder
- Restart the dev server after updating `.env.local`

### "Login popup blocked"
- Check your browser popup blocker settings
- Ensure you're using `http://localhost` (not just `localhost`)

### "API not enabled"
- For Google: Make sure Google Calendar API is enabled in Cloud Console
- For Outlook: Check that Calendar.Read permission is granted

### Events not loading
- Make sure you're logged in
- Check browser console for error messages
- Verify tokens are being generated correctly

---

## Next Steps

1. **Store tokens securely**: Save tokens in backend database
2. **Add calendar create**: Allow creating new events
3. **Sync events**: Periodically sync events from both sources
4. **Add notifications**: Display upcoming event reminders
5. **Share calendars**: Allow viewing other users' calendars

---

## Security Notes

- Never commit `.env.local` to git
- Keep Client Secret confidential
- Use HTTPS in production
- Implement proper token refresh logic
- Add rate limiting to API calls

---

For more information:
- [Google Calendar API Docs](https://developers.google.com/calendar)
- [Microsoft Graph API Docs](https://docs.microsoft.com/en-us/graph/api/overview)
