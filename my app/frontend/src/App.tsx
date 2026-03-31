import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { MsalProvider } from '@azure/msal-react'
import { PublicClientApplication } from '@azure/msal-browser'
import Home from './pages/Home'
import About from './pages/About'
import Contact from './pages/Contact'
import Calendar from './pages/Calendar'
import { googleConfig } from './config/googleConfig'
import { msalConfig } from './config/msalConfig'
import './App.css'

// Initialize MSAL
const msalInstance = new PublicClientApplication(msalConfig)

function App() {
  return (
    <GoogleOAuthProvider clientId={googleConfig.clientId}>
      <MsalProvider instance={msalInstance}>
        <BrowserRouter>
          <div className="app">
            <nav className="navbar">
              <div className="container">
                <Link to="/" className="logo">Our Home App</Link>
                <ul className="nav-links">
                  <li><Link to="/">Home</Link></li>
                  <li><Link to="/about">About</Link></li>
                  <li><Link to="/calendar">Calendar</Link></li>
                  <li><Link to="/contact">Contact</Link></li>
                </ul>
              </div>
            </nav>

            <main className="container">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/about" element={<About />} />
                <Route path="/calendar" element={<Calendar />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </main>

            <footer className="footer">
              <p>&copy; 2024 My App. All rights reserved.</p>
            </footer>
          </div>
        </BrowserRouter>
      </MsalProvider>
    </GoogleOAuthProvider>
  )
}

function NotFound() {
  return (
    <div>
      <h1>404 - Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
    </div>
  )
}

export default App
