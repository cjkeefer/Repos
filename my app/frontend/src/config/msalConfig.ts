/**
 * MSAL (Microsoft Authentication Library) Configuration
 * 
 * To set up:
 * 1. Go to https://portal.azure.com
 * 2. Create a new app registration
 * 3. Copy your Client ID
 * 4. Add redirect URI: http://localhost:5173
 * 5. Replace AZURE_CLIENT_ID with your actual Client ID
 */

export const msalConfig = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID || 'YOUR_AZURE_CLIENT_ID_HERE',
    authority: 'https://login.microsoftonline.com/common',
    redirectUri: 'http://localhost:5173',
  },
  cache: {
    cacheLocation: 'localStorage' as const,
    storeAuthStateInCookie: false,
  },
}

export const loginRequest = {
  scopes: ['Calendar.Read', 'Calendar.ReadWrite', 'user.read'],
}

export const graphConfig = {
  graphMeEndpoint: 'https://graph.microsoft.com/v1.0/me',
  graphCalendarEndpoint: 'https://graph.microsoft.com/v1.0/me/events',
}
