import React, { useState } from "react";
import MapComponent from "../../components/map/MapComponent";
import SearchBar from "../../components/SearchBar/SearchBar";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import styles from "./DashboardPublic.module.css"; // Importa los estilos

const mockWeatherData = {
  temperature: 25,
  humidity: 60,
  wind: 10,
  description: "Soleado",
  latitude: 40.7128,
  longitude: -74.006,
  hourly: [
    { time: "08:00", temp: 22 },
    { time: "09:00", temp: 23 },
    { time: "10:00", temp: 24 },
    { time: "11:00", temp: 25 },
    { time: "12:00", temp: 26 },
    { time: "13:00", temp: 27 },
    { time: "14:00", temp: 28 },
  ],
};

const Dashboard: React.FC = () => {
  const [city, setCity] = useState("New York");
  const [weather] = useState(mockWeatherData);

  return (
    <div className={styles.dashboardContainer}>
      <div className={styles.searchBarContainer}>
        <SearchBar onSearch={setCity} />
      </div>

      <div className={styles.weatherInfo}>
        <h1>{city}</h1>
        <h2>{weather.temperature}°C</h2>
        <div className={styles.weatherDetails}>
        <p>{weather.description}</p>
        <p>Wind: {weather.wind} mph</p>
        <p>Humidity: {weather.humidity}%</p>
        </div>
      </div>

      <div className={styles.mapContainer}>
        <MapComponent latitude={weather.latitude} longitude={weather.longitude} />
      </div>

      <div className={styles.chartContainer}>
        <h2>Hourly Forecast</h2>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={weather.hourly}>
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="temp" stroke="#007bff" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Dashboard;
