/**
 * Google OAuth Configuration
 * 
 * To set up:
 * 1. Go to https://console.cloud.google.com
 * 2. Create a new project
 * 3. Enable Google Calendar API
 * 4. Create OAuth 2.0 credentials (Web application)
 * 5. Add http://localhost:5173 as authorized redirect URI
 * 6. Copy your Client ID
 * 7. Replace VITE_GOOGLE_CLIENT_ID with your actual Client ID
 */

export const googleConfig = {
  clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID_HERE.apps.googleusercontent.com',
}
