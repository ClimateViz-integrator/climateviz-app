import React, { useRef } from "react";
import styles from "../../pages/DashboardPublic/weatherPublic.module.css";
import { ForecastData } from "../../models/prediction/forecastData";
import {
  ResponsiveContainer, LineChart, Line,
  YAxis,
  Tooltip
} from "recharts";

interface WeatherDashboardProps {
  forecast?: ForecastData;
  onDashboardClick?: (forecast: ForecastData) => void;
}

const HOUR_WIDTH = 80; // Puedes ajustar este valor

const WeatherDashboard: React.FC<WeatherDashboardProps> = ({ forecast, onDashboardClick }) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  if (!forecast || !forecast.hours || forecast.hours.length === 0) {
    return null;
  }

  const minTemp = Math.min(...forecast.hours.map(h => h.temp_pred));

  const getWeatherIcon = (temp: number, humidity: number) => {
    if (humidity > 70) return "🌧️";
    if (humidity > 50) return "🌦️";
    if (humidity > 30) return "☁️";
    if (temp > 25) return "☀️";
    return "🌤️";
  };

  const formatHour = (dateTimeStr: string) => {
    try {
      const date = new Date(dateTimeStr);
      const hours = date.getHours();
      const ampm = hours >= 12 ? 'p. m.' : 'a. m.';
      const displayHours = hours % 12 || 12;
      return `${displayHours} ${ampm}`;
    } catch (e) {
      return "N/A";
    }
  };

  const chartData = forecast.hours.map((hour, index) => ({
    x: index * HOUR_WIDTH + HOUR_WIDTH / 2, // centro de cada bloque
    temp: hour.temp_pred,
  }));


  const handleDashboardClick = () => {
    if (onDashboardClick) {
      onDashboardClick(forecast);
    } else {
      const url = `/weather/detail?city=${forecast.city}`;
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  // Ancho total del gráfico y de los contenedores scrolleables
  const totalWidth = forecast.hours.length * HOUR_WIDTH;

  return (
    <div className={`${styles.weatherDashboard} ${styles.clickable}`} onClick={handleDashboardClick}>
      <div className={styles.header}>
        <h2>{forecast.city}, Mínima de {Math.round(minTemp)} C.</h2>
      </div>

      <div
        className={styles.scrollContainer}
        ref={scrollContainerRef}
        onClick={(e) => e.stopPropagation()}
        style={{ overflowX: "auto" }}
      >
        {/* Contenedor scrolleable para las horas */}
        <div
          className={styles.forecastContainer}
          style={{ width: totalWidth, minWidth: "100%" }}
        >
          {forecast.hours.map((hour, index) => (
            <div
              key={index}
              className={styles.hourForecast}
              style={{ width: HOUR_WIDTH, display: "inline-block" }}
            >
              <p className={styles.time}>{formatHour(hour.date_time)}</p>
              <div className={styles.weatherIcon}>
                {getWeatherIcon(hour.temp_pred, hour.humidity_pred)}
              </div>
              <p className={styles.temperature}>{Math.round(hour.temp_pred * 100) / 100}°</p>

            </div>
          ))}
        </div>

        {/* Gráfico scrolleable alineado */}
        <div
          className={styles.tempLineChart}
          style={{ width: totalWidth, minWidth: "100%", height: 40, marginBottom: 30 }}
        >
          <ResponsiveContainer width="100%" height={80} >
            <LineChart data={chartData}>
              <YAxis
                hide
                domain={['dataMin', 'dataMax']}
              />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="temp"
                stroke="#007bff"
                name="Temperature (°C)"
                strokeWidth={2}
                dot={{ r: 5, stroke: "#fff", strokeWidth: 2, fill: "#8ecaff" }}
                activeDot={{ r: 7 }}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>

        </div>

        {/* Contenedor scrolleable para la humedad */}
        <div
          className={styles.humidityContainer}
          style={{ width: totalWidth, minWidth: "100%", marginTop: 30 }}
        >
          {forecast.hours.map((hour, index) => (
            <div
              key={index}
              className={styles.humidityItem}
              style={{ width: HOUR_WIDTH, display: "inline-block" }}
            >
              <span className={styles.humidityIcon}>💧</span>
              <span className={styles.humidityValue}>{Math.round(hour.humidity_pred)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WeatherDashboard;
