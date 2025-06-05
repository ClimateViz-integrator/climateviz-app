import React, { useState, useMemo } from "react";
import styles from "../../pages/DashboardPublic/WeatherDetailView.module.css";
import { ForecastData } from "../../models/prediction/forecastData";

interface WeatherDetailViewProps {
  forecast: ForecastData;
  onClose: () => void;
}

interface DayGroup {
  date: string;
  displayDate: string;
  hours: any[];
  startIndex: number;
}

const WeatherDetailView: React.FC<WeatherDetailViewProps> = ({ forecast, onClose }) => {
  const [selectedHourIndex, setSelectedHourIndex] = useState(0);
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set());

  const formatDateForDisplay = (dateStr: string) => {
    try {
      const [year, month, day] = dateStr.split('-').map(Number);
      const date = new Date(year, month - 1, day); // month - 1 porque Date usa 0-11 para meses

      const days = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
      const months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];

      return `${days[date.getDay()]}, ${date.getDate()} de ${months[date.getMonth()]}`;
    } catch (e) {
      console.error("Error formateando fecha:", e);
      return dateStr;
    }
  };

  // Agrupar horas por días
  const dayGroups = useMemo(() => {
    console.log("Agrupando horas por días...");

    if (!forecast?.hours || forecast.hours.length === 0) {
      console.log("No hay horas para agrupar");
      return [];
    }

    const groups: DayGroup[] = [];
    let currentDate = '';
    let currentGroup: any[] = [];
    let startIndex = 0;

    forecast.hours.forEach((hour, index) => {
      console.log(`Procesando hora ${index}:`, hour.date_time);

      const dateKey = hour.date_time.split('T')[0];
      console.log(`Fecha extraída: ${dateKey}, Fecha actual: ${currentDate}`);

      if (dateKey !== currentDate) {
        // Si hay un grupo anterior, guardarlo
        if (currentGroup.length > 0) {
          groups.push({
            date: currentDate,
            displayDate: formatDateForDisplay(currentDate),
            hours: currentGroup,
            startIndex: startIndex
          });
          console.log(`✅ Grupo creado para ${currentDate}:`, currentGroup.length, "horas");
        }

        // Iniciar nuevo grupo
        currentDate = dateKey;
        currentGroup = [hour];
        startIndex = index;
        console.log(`Nuevo grupo iniciado para ${currentDate}`);
      } else {
        currentGroup.push(hour);
        console.log(`Hora agregada al grupo ${currentDate}`);
      }
    });

    // Agregar el último grupo
    if (currentGroup.length > 0) {
      groups.push({
        date: currentDate,
        displayDate: formatDateForDisplay(currentDate),
        hours: currentGroup,
        startIndex: startIndex
      });
      console.log(`Último grupo creado para ${currentDate}:`, currentGroup.length, "horas");
    }

    console.log("Grupos finales:", groups);
    return groups;
  }, [forecast.hours]);




  const formatTime = (dateTimeStr: string) => {
    try {
      const date = new Date(dateTimeStr);
      const hours = date.getHours();
      const minutes = date.getMinutes();
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
    } catch (e) {
      return "N/A";
    }
  };

  const getWeatherCondition = (temp: number, humidity: number, cloud: number) => {
    if (temp < 5 && cloud > 80 && humidity > 70) return "Nieve o aguanieve";
    if (temp > 30 && humidity > 60) return "Clima muy caluroso y húmedo";
    if (cloud > 80 && humidity > 70) return "Tormentas eléctricas";
    if (humidity > 70) return "Lluvia moderada";
    if (temp < 10 && humidity > 80) return "Niebla densa";
    if (cloud > 50) return "Parcialmente nublado";
    if (temp > 35 && humidity < 40) return "Calor seco extremo";
    return "Despejado";
  };

  const getWeatherIcon = (temp: number, humidity: number, cloud: number) => {
    if (temp < 5 && cloud > 80 && humidity > 70) return "🌨️";
    if (temp > 30 && humidity > 60) return "🥵";
    if (cloud > 80 && humidity > 70) return "⛈️";
    if (cloud > 80) return "🌩️";
    if (humidity > 70) return "🌧️";
    if (temp < 10 && humidity > 80) return "🌫️";
    if (cloud > 50) return "⛅";
    if (temp > 35 && humidity < 40) return "🔥";
    return "☀️";
  };


  const toggleSection = (index: number) => {
    const newExpandedSections = new Set(expandedSections);
    if (newExpandedSections.has(index)) {
      newExpandedSections.delete(index);
    } else {
      newExpandedSections.add(index);
    }
    setExpandedSections(newExpandedSections);
  };

  const handleDayChange = (dayIndex: number) => {
    setSelectedDayIndex(dayIndex);
    // Resetear la hora seleccionada al primer índice del día seleccionado
    setSelectedHourIndex(dayGroups[dayIndex].startIndex);
    // Limpiar secciones expandidas
    setExpandedSections(new Set());
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Obtener datos del día y hora seleccionados
  const currentDay = dayGroups[selectedDayIndex];
  const selectedHour = forecast.hours[selectedHourIndex];

  return (
    <div className={styles.fullScreenContainer} onClick={handleOverlayClick}>
      <div className={styles.detailContainer}>
        <div className={styles.header}>
          <button className={styles.closeButton} onClick={onClose}>×</button>
          <div className={styles.titleSection}>
            <h2>Tiempo por hora</h2>
            <p className={styles.location}>- {forecast.city}, Caldas, Colombia</p>
            <p className={styles.timestamp}>Hasta 19:56 GMT-05:00</p>
          </div>
        </div>

        {/* Selector de días */}
        <div className={styles.daySelector}>
          <label htmlFor="daySelect">Seleccionar día:</label>
          <select
            id="daySelect"
            value={selectedDayIndex}
            onChange={(e) => handleDayChange(Number(e.target.value))}
            className={styles.daySelect}
          >
            {dayGroups.map((day, index) => (
              <option key={index} value={index}>
                {day.displayDate} ({day.hours.length} horas)
              </option>
            ))}
          </select>
        </div>


        <div className={styles.dateSection}>
          <h3>{currentDay?.displayDate}</h3>
        </div>

        <div className={styles.currentWeather}>
          <div className={styles.mainWeatherInfo}>
            <div className={styles.timeTemp}>
              <span className={styles.time}>{formatTime(selectedHour.date_time)}</span>
              <span className={styles.temperature}>{Math.round(selectedHour.temp_pred)}°</span>
            </div>

            <div className={styles.weatherCondition}>
              <span className={styles.weatherIcon}>
                {getWeatherIcon(selectedHour.temp_pred, selectedHour.humidity_pred, selectedHour.cloud)}
              </span>
              <span>{getWeatherCondition(selectedHour.temp_pred, selectedHour.humidity_pred, selectedHour.cloud)}</span>
            </div>

            <div className={styles.weatherDetails}>
              <div className={styles.detailItem}>
                <span className={styles.detailIcon}>💧</span>
                <span>{Math.round(selectedHour.humidity_pred)}%</span>
              </div>
              <div className={styles.detailItem}>
                <span className={styles.detailIcon}>💨</span>
                <span>{selectedHour.wind_kph} km/h</span>
              </div>
              <button
                className={styles.expandButton}
                onClick={() => toggleSection(selectedHourIndex)}
              >
                {expandedSections.has(selectedHourIndex) ? '−' : '+'}
              </button>
            </div>
          </div>

          {/* Detalles expandibles de la hora actual */}
          {expandedSections.has(selectedHourIndex) && (
            <div className={styles.additionalDetails}>
              <div className={styles.detailRow}>
                <div className={styles.detailCard}>
                  <span className={styles.cardIcon}>🌡️</span>
                  <div>
                    <span>Sensación</span>
                    <span>{Math.round(selectedHour.temp_pred)}°</span>
                  </div>
                </div>

                <div className={styles.detailCard}>
                  <span className={styles.cardIcon}>💨</span>
                  <div>
                    <span>Viento</span>
                    <span>{selectedHour.wind_kph} km/h</span>
                  </div>
                </div>

                <div className={styles.detailCard}>
                  <span className={styles.cardIcon}>💧</span>
                  <div>
                    <span>Humedad</span>
                    <span>{Math.round(selectedHour.humidity_pred)}%</span>
                  </div>
                </div>
              </div>

              <div className={styles.detailRow}>
                <div className={styles.detailCard}>
                  <span className={styles.cardIcon}>☀️</span>
                  <div>
                    <span>Índice UV</span>
                    <span>{selectedHour.uv} de 11</span>
                  </div>
                </div>

                <div className={styles.detailCard}>
                  <span className={styles.cardIcon}>☁️</span>
                  <div>
                    <span>Nubosidad</span>
                    <span>{selectedHour.cloud}%</span>
                  </div>
                </div>


              </div>
            </div>
          )}
        </div>

        {/* Lista expandible de las horas del día seleccionado */}
        <div className={styles.hourlyList}>
          {currentDay?.hours.map((hour, index) => {
            const globalIndex = currentDay.startIndex + index;
            return (
              <div key={index} className={styles.hourlyItem}>
                <div className={styles.hourlyHeader}>
                  <span className={styles.hourTime}>{formatTime(hour.date_time)}</span>
                  <span className={styles.hourTemp}>{Math.round(hour.temp_pred)}°</span>
                  <span className={styles.hourIcon}>
                    {getWeatherIcon(hour.temp_pred, hour.humidity_pred, hour.cloud)}
                  </span>
                  <span className={styles.hourCondition}>
                    {getWeatherCondition(hour.temp_pred, hour.humidity_pred, hour.cloud)}
                  </span>
                  <div className={styles.hourDetails}>
                    <span>💧 {Math.round(hour.humidity_pred)}%</span>
                    <span>💨 {hour.wind_kph} km/h</span>
                  </div>
                  <button
                    className={styles.hourExpandButton}
                    onClick={() => toggleSection(globalIndex)}
                  >
                    {expandedSections.has(globalIndex) ? '−' : '+'}
                  </button>
                </div>

                {/* Contenido expandible para cada hora */}
                {expandedSections.has(globalIndex) && (
                  <div className={styles.expandedContent}>
                    <div className={styles.expandedGrid}>
                      <div className={styles.expandedCard}>
                        <span className={styles.cardIcon}>🌡️</span>
                        <div>
                          <span>Sensación térmica</span>
                          <span>{Math.round(hour.temp_pred)}°</span>
                        </div>
                      </div>

                      <div className={styles.expandedCard}>
                        <span className={styles.cardIcon}>💨</span>
                        <div>
                          <span>Viento</span>
                          <span>{hour.wind_kph} km/h</span>
                        </div>
                      </div>

                      <div className={styles.expandedCard}>
                        <span className={styles.cardIcon}>💧</span>
                        <div>
                          <span>Humedad</span>
                          <span>{Math.round(hour.humidity_pred)}%</span>
                        </div>
                      </div>

                      <div className={styles.expandedCard}>
                        <span className={styles.cardIcon}>☀️</span>
                        <div>
                          <span>Índice UV</span>
                          <span>{hour.uv}</span>
                        </div>
                      </div>

                      <div className={styles.expandedCard}>
                        <span className={styles.cardIcon}>☁️</span>
                        <div>
                          <span>Nubosidad</span>
                          <span>{hour.cloud}%</span>
                        </div>
                      </div>

                      <div className={styles.expandedCard}>
                        <span className={styles.cardIcon}>🌧️</span>
                        <div>
                          <span>Prob. lluvia</span>
                          <span>{Math.round(hour.humidity_pred)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default WeatherDetailView;
