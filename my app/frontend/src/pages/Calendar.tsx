import { useState } from 'react'
import { GoogleLogin } from '@react-oauth/google'
import { useMsal } from '@azure/msal-react'
import { loginRequest } from '../config/msalConfig'

interface CalendarEvent {
  id: string
  title: string
  description?: string
  startTime: string
  endTime: string
  source: 'google' | 'outlook'
}

export default function Calendar() {
  const [events, setEvents] = useState<CalendarEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [googleToken, setGoogleToken] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'google' | 'outlook'>('google')
  const { instance, accounts } = useMsal()

  // Handle Google Login
  const handleGoogleLoginSuccess = async (credentialResponse: any) => {
    try {
      setLoading(true)
      setError(null)
      setGoogleToken(credentialResponse.credential)
      
      // Decode JWT to get user info (for demo purposes)
      const base64Url = credentialResponse.credential.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      const decodedToken = JSON.parse(jsonPayload)
      
      console.log('Google Login Success:', decodedToken)
      setError(null)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Google login failed'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLoginError = () => {
    setError('Google login failed. Please try again.')
  }

  // Handle Outlook/Microsoft Login
  const handleOutlookLogin = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await instance.loginPopup(loginRequest)
      console.log('Outlook Login Success:', response)
      
      // Fetch calendar events
      await fetchOutlookEvents(response.accessToken)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Outlook login failed'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  // Fetch events from Outlook
  const fetchOutlookEvents = async (accessToken: string) => {
    try {
      const response = await fetch(
        'https://graph.microsoft.com/v1.0/me/events?$top=10',
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      )
      
      if (!response.ok) {
        throw new Error('Failed to fetch Outlook events')
      }
      
      const data = await response.json()
      const formattedEvents: CalendarEvent[] = data.value.map((event: any) => ({
        id: event.id,
        title: event.subject,
        description: event.bodyPreview,
        startTime: new Date(event.start.dateTime).toLocaleString(),
        endTime: new Date(event.end.dateTime).toLocaleString(),
        source: 'outlook',
      }))
      
      setEvents(formattedEvents)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch Outlook events'
      setError(message)
    }
  }

  // Fetch Google Calendar events
  const fetchGoogleEvents = async () => {
    try {
      setLoading(true)
      setError(null)
      
      if (!googleToken) {
        setError('Please login with Google first')
        setLoading(false)
        return
      }

      // In a real app, you'd use the Google Calendar API
      // For demo, we'll show placeholder events
      const mockEvents: CalendarEvent[] = [
        {
          id: '1',
          title: 'Sample Meeting',
          description: 'This is a demo event',
          startTime: new Date().toLocaleString(),
          endTime: new Date(Date.now() + 3600000).toLocaleString(),
          source: 'google',
        },
      ]
      
      setEvents(mockEvents)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch Google events'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  // Logout
  const handleLogout = () => {
    setGoogleToken(null)
    setEvents([])
    setError(null)
  }

  const isGoogleLoggedIn = !!googleToken
  const isOutlookLoggedIn = accounts.length > 0

  return (
    <div>
      <h1>Calendar Integration</h1>
      
      {error && <p style={{ color: '#ff6b6b' }}>Error: {error}</p>}
      
      <div className="calendar-container">
        {/* Tab Navigation */}
        <div className="calendar-tabs">
          <button
            className={`tab-button ${activeTab === 'google' ? 'active' : ''}`}
            onClick={() => setActiveTab('google')}
          >
            Google Calendar
          </button>
          <button
            className={`tab-button ${activeTab === 'outlook' ? 'active' : ''}`}
            onClick={() => setActiveTab('outlook')}
          >
            Outlook Calendar
          </button>
        </div>

        {/* Google Calendar Tab */}
        {activeTab === 'google' && (
          <div className="calendar-content">
            <h2>Google Calendar</h2>
            
            {!isGoogleLoggedIn ? (
              <div className="login-section">
                <p>Sign in with your Google account to access your calendar</p>
                <div className="google-login-wrapper">
                  <GoogleLogin
                    onSuccess={handleGoogleLoginSuccess}
                    onError={handleGoogleLoginError}
                  />
                </div>
              </div>
            ) : (
              <div className="calendar-logged-in">
                <p style={{ color: '#4ade80' }}>✓ Logged in with Google</p>
                <button onClick={fetchGoogleEvents} disabled={loading}>
                  {loading ? 'Loading...' : 'Load Calendar Events'}
                </button>
                <button onClick={handleLogout} style={{ marginLeft: '1rem' }}>
                  Logout
                </button>
              </div>
            )}

            {events.length > 0 && (
              <div className="events-list">
                <h3>Upcoming Events</h3>
                {events.map((event) => (
                  <div key={event.id} className="event-card">
                    <h4>{event.title}</h4>
                    <p className="event-time">
                      📅 {event.startTime}
                    </p>
                    {event.description && (
                      <p className="event-description">{event.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Outlook Calendar Tab */}
        {activeTab === 'outlook' && (
          <div className="calendar-content">
            <h2>Outlook Calendar</h2>
            
            {!isOutlookLoggedIn ? (
              <div className="login-section">
                <p>Sign in with your Microsoft account to access your calendar</p>
                <button
                  onClick={handleOutlookLogin}
                  disabled={loading}
                  className="outlook-login-button"
                >
                  {loading ? 'Logging in...' : 'Sign in with Microsoft'}
                </button>
              </div>
            ) : (
              <div className="calendar-logged-in">
                <p style={{ color: '#4ade80' }}>
                  ✓ Logged in as {accounts[0]?.name}
                </p>
                <button onClick={() => instance.logout()} style={{ marginTop: '1rem' }}>
                  Logout
                </button>
              </div>
            )}

            {events.length > 0 && (
              <div className="events-list">
                <h3>Upcoming Events</h3>
                {events.map((event) => (
                  <div key={event.id} className="event-card">
                    <h4>{event.title}</h4>
                    <p className="event-time">
                      📅 {event.startTime}
                    </p>
                    {event.description && (
                      <p className="event-description">{event.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Setup Instructions */}
        <div className="setup-instructions">
          <h3>Setup Instructions</h3>
          
          <div className="instruction-section">
            <h4>Google Calendar Setup:</h4>
            <ol>
              <li>Go to <a href="https://console.cloud.google.com" target="_blank">Google Cloud Console</a></li>
              <li>Create a new project</li>
              <li>Enable Google Calendar API</li>
              <li>Create OAuth 2.0 credentials (Web application)</li>
              <li>Add <code>http://localhost:5173</code> as authorized redirect URI</li>
              <li>Update your Client ID in the GoogleLogin component</li>
            </ol>
          </div>

          <div className="instruction-section">
            <h4>Outlook Calendar Setup:</h4>
            <ol>
              <li>Go to <a href="https://portal.azure.com" target="_blank">Azure Portal</a></li>
              <li>Create a new app registration</li>
              <li>Configure API permissions (Calendar.Read, Calendar.ReadWrite)</li>
              <li>Add redirect URI: <code>http://localhost:5173</code></li>
              <li>Copy Client ID and update msalConfig.ts</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  )
}
