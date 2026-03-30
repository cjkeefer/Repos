import { useState, useEffect } from 'react'

interface WeatherData {
  current_weather: {
    temperature: number
    humidity: number
    wind_speed: number
    weather_code: number
  }
  forecast: {
    daily: {
      time: string[]
      temperature_2m_max: number[]
      temperature_2m_min: number[]
      weather_code: number[]
    }
  }
  location: {
    latitude: number
    longitude: number
    timezone: string
  }
}

export default function Home() {
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [location, setLocation] = useState<{ lat: number; lon: number } | null>(null)

  // Convert Celsius to Fahrenheit
  const celsiusToFahrenheit = (celsius: number): string => {
    return ((celsius * 9) / 5 + 32).toFixed(1)
  }

  // Get user's geolocation
  const getLocation = () => {
    setLoading(true)
    setError(null)

    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser')
      setLoading(false)
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords
        setLocation({ lat: latitude, lon: longitude })
        fetchWeather(latitude, longitude)
      },
      (err) => {
        setError(`Location error: ${err.message}`)
        setLoading(false)
      }
    )
  }

  // Fetch weather from backend
  const fetchWeather = async (lat: number, lon: number) => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(
        `http://localhost:8000/api/weather?lat=${lat}&lon=${lon}`
      )
      
      if (!response.ok) {
        throw new Error('Failed to fetch weather')
      }
      
      const data = await response.json()
      setWeather(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch weather'
      setError(message)
      console.error('Weather fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Get location on component mount
  useEffect(() => {
    getLocation()
  }, [])

  // Weather code to description
  const getWeatherDescription = (code: number): string => {
    const weatherCodes: { [key: number]: string } = {
      0: 'Clear sky',
      1: 'Mainly clear',
      2: 'Partly cloudy',
      3: 'Overcast',
      45: 'Foggy',
      48: 'Depositing rime fog',
      51: 'Light drizzle',
      53: 'Moderate drizzle',
      55: 'Dense drizzle',
      61: 'Slight rain',
      63: 'Moderate rain',
      65: 'Heavy rain',
      71: 'Slight snow',
      73: 'Moderate snow',
      75: 'Heavy snow',
      80: 'Slight rain showers',
      81: 'Moderate rain showers',
      82: 'Violent rain showers',
      85: 'Slight snow showers',
      86: 'Heavy snow showers',
      95: 'Thunderstorm',
      96: 'Thunderstorm with slight hail',
      99: 'Thunderstorm with heavy hail',
    }
    return weatherCodes[code] || 'Unknown'
  }

  return (
    <div>
      <h1>Weather Forecast</h1>
      
      {loading && <p>Loading weather data...</p>}
      
      {error && <p style={{ color: '#ff6b6b' }}>Error: {error}</p>}
      
      {weather && (
        <div className="weather-container">
          <div className="current-weather">
            <h2>Current Weather</h2>
            {location && (
              <p style={{ fontSize: '0.9em', opacity: 0.8 }}>
                📍 Lat: {location.lat.toFixed(2)}, Lon: {location.lon.toFixed(2)}
              </p>
            )}
            <div className="weather-details">
              <div className="weather-item">
                <span className="label">Temperature:</span>
                <span className="value">{celsiusToFahrenheit(weather.current_weather.temperature)}°F</span>
              </div>
              <div className="weather-item">
                <span className="label">Humidity:</span>
                <span className="value">{weather.current_weather.humidity}%</span>
              </div>
              <div className="weather-item">
                <span className="label">Wind Speed:</span>
                <span className="value">{weather.current_weather.wind_speed} km/h</span>
              </div>
              <div className="weather-item">
                <span className="label">Condition:</span>
                <span className="value">
                  {getWeatherDescription(weather.current_weather.weather_code)}
                </span>
              </div>
            </div>
          </div>

          <div className="forecast">
            <h3>7-Day Forecast</h3>
            <div className="forecast-grid">
              {weather.forecast.daily.time.map((date, index) => (
                <div key={index} className="forecast-day">
                  <p className="forecast-date">{new Date(date).toLocaleDateString()}</p>
                  <p className="forecast-condition">
                    {getWeatherDescription(weather.forecast.daily.weather_code[index])}
                  </p>
                  <p className="forecast-temp">
                    <span className="max">{celsiusToFahrenheit(weather.forecast.daily.temperature_2m_max[index])}°F</span>
                    <span className="min">{celsiusToFahrenheit(weather.forecast.daily.temperature_2m_min[index])}°F</span>
                  </p>
                </div>
              ))}
            </div>
          </div>

          <button onClick={() => getLocation()}>Refresh Weather</button>
        </div>
      )}
    </div>
  )
}
