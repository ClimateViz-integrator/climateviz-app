import React, { useState } from "react";
import api from "../Api";
import styles from "../../pages/DashboardPublic/DashboardPublic.module.css";
import { ForecastData } from "../../models/prediction/forecastData";



interface WeatherMapProps {
  onForecastUpdate?: (data: ForecastData) => void;
}

const WeatherMap: React.FC<WeatherMapProps> = ({ onForecastUpdate }) => {
  const [city, setCity] = useState("");
  const [days, setDays] = useState(1);
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [selectedHourIndex, setSelectedHourIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    console.log("Formulario enviado con ciudad:", city, "y días:", days);
    
    try {
      const resp = await api.post("weather/predict", { city, days });
      const data = resp.data;

      if (!data || data.length === 0) {
        throw new Error("No se recibieron datos para la ciudad especificada");
      }

      // Combinar todas las horas de todos los días
      const combinedHours = data.flatMap((day: any) => day.hours);

      const forecastData = {
        city: data[0].city,
        location: data[0].location,
        hours: combinedHours,
        selectedHourIndex: 0 
      };

      setForecast(forecastData);
      setSelectedHourIndex(0);
      
      // Notificar al componente padre con los datos actualizados
      if (onForecastUpdate) {
        onForecastUpdate(forecastData);
      }
    } catch (err) {
      console.error(err);
      setError("Error al obtener la predicción. Por favor intenta con otra ciudad o más tarde.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleHourChange = (newIndex: number) => {
    setSelectedHourIndex(newIndex);
    
    // Actualizar el forecast con el nuevo índice seleccionado
    if (forecast) {
      const updatedForecast = {
        ...forecast,
        selectedHourIndex: newIndex
      };
      
      // Actualizar estado local
      setForecast(updatedForecast);
      
      // Notificar al componente padre
      if (onForecastUpdate) {
        onForecastUpdate(updatedForecast);
      }
    }
  };

  return (
    <div className={styles.weatherControlsFixed}>
      {/* Formulario siempre visible en la parte superior */}
      <form onSubmit={handleSubmit} className={styles.futuristicForm}>
        <input
          type="text"
          placeholder="Ciudad"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          className={styles.futuristicInput}
          required
        />
        <input
          type="number"
          min={1}
          max={7}
          placeholder="Días"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className={styles.futuristicInput}
          required
        />
        <button 
          type="submit" 
          className={styles.futuristicButton}
          disabled={isLoading}
        >
          {isLoading ? "Cargando..." : "Consultar"}
        </button>
      </form>

      {/* Mensaje de error */}
      {error && (
        <div className={styles.errorMessage}>
          {error}
        </div>
      )}

      {/* Información de pronóstico (slider) - siempre visible si hay datos */}
      {forecast && (
        <div className={styles.forecastControls}>
          <p className={styles.cityTitle}>Predicción para {forecast.city}</p>
          
          <input
            type="range"
            min={0}
            max={forecast.hours.length - 1}
            value={selectedHourIndex}
            onChange={(e) => handleHourChange(Number(e.target.value))}
            step={1}
            className={styles.futuristicSlider}
          />

          <p className={styles.hourDetails}>
            Hora: {forecast.hours[selectedHourIndex].date_time} — Temp:{" "}
            {forecast.hours[selectedHourIndex].temp_pred.toFixed(1)}°C — Hum:{" "}
            {forecast.hours[selectedHourIndex].humidity_pred.toFixed(0)}%
          </p>
        </div>
      )}
    </div>
  );
};

export default WeatherMap;