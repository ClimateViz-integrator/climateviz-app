import React, { useRef } from "react";
import styles from "../../pages/DashboardPublic/weatherPublic.module.css";
import { ForecastData } from "../../models/prediction/forecastData";

interface WeatherDashboardProps {
  forecast?: ForecastData;
  onDashboardClick?: (forecast: ForecastData) => void;
}

const WeatherDashboard: React.FC<WeatherDashboardProps> = ({ forecast, onDashboardClick  }) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  if (!forecast || !forecast.hours || forecast.hours.length === 0) {
    return null;
  }

  // Calcular la temperatura mínima
  const minTemp = Math.min(...forecast.hours.map(h => h.temp_pred));

  // Función para obtener el icono según la condición climática
  const getWeatherIcon = (temp: number, humidity: number) => {
    if (humidity > 70) return "🌧️"; // Lluvia
    if (humidity > 50) return "🌦️"; // Parcialmente nublado con lluvia
    if (humidity > 30) return "☁️"; // Nublado
    if (temp > 25) return "☀️";    // Soleado
    return "🌤️";                   // Parcialmente nublado
  };

  // Función para formatear la hora correctamente con AM/PM
    const formatHour = (dateTimeStr: string) => {
        try {
        const date = new Date(dateTimeStr);
        const hours = date.getHours();
        const ampm = hours >= 12 ? 'p. m.' : 'a. m.';
        
        // Convertir a formato 12 horas
        const displayHours = hours % 12 || 12; // Si es 0, mostrar como 12
        
        return `${displayHours} ${ampm}`;
        } catch (e) {
        return "N/A";
        }
    };
  

  // Función para manejar el clic en el dashboard
  const handleDashboardClick = () => {
    if (onDashboardClick) {
      onDashboardClick(forecast);
    } else {
      // URL a la que quieres redirigir (puedes personalizarla)
      const url = `/weather/detail?city=${forecast.city}`;
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };
  return (
    <div className={`${styles.weatherDashboard} ${styles.clickable}`} onClick={handleDashboardClick}>
      <div className={styles.header}>
        <h2>{forecast.city}, Mínima de {Math.round(minTemp)} C.</h2>
      </div>
      
      <div 
        className={styles.scrollContainer}
        ref={scrollContainerRef}
        onClick={(e) => e.stopPropagation()} 
      >
        <div className={styles.forecastContainer}>
          {forecast.hours.map((hour, index) => (
            <div key={index} className={styles.hourForecast}>
              <p className={styles.time}>{formatHour(hour.date_time)}</p>
              <div className={styles.weatherIcon}>
                {getWeatherIcon(hour.temp_pred, hour.humidity_pred)}
              </div>
              <p className={styles.temperature}>{Math.round(hour.temp_pred)}°</p>
            </div>
          ))}
        </div>
        
        <div className={styles.divider}></div>
        
        <div className={styles.humidityContainer}>
          {forecast.hours.map((hour, index) => (
            <div key={index} className={styles.humidityItem}>
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
