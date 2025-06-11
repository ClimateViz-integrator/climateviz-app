import React, { useEffect, useState } from "react";
import MapComponent from "../../components/map/MapComponent";
import SearchBar from "../../components/SearchBar/SearchBar";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import WeatherMap from "../../components/services_api/weatherMap";
import styles from "./DashboardPublic.module.css";
import ChatBotMap from "@/components/services_api/chatBotMap";
import { ForecastData } from "../../models/prediction/forecastData";
import WeatherDashboard from "@/components/services_api/weatherDashboard";

// Datos de respaldo por si no hay datos reales
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
  const [forecastData, setForecastData] = useState<ForecastData | null>(null);
  const [chartData, setChartData] = useState(weather.hourly);
  const [selectedTemperature, setSelectedTemperature] = useState<number | null>(null);

  // Función para actualizar los datos del pronóstico desde WeatherMap
  const handleForecastUpdate = (data: ForecastData) => {
    setForecastData(data);

    // Transformar los datos a formato para el gráfico
    if (data && data.hours) {
      const formattedData = data.hours.map(hour => ({
        time: formatDateTime(hour.date_time),
        temp: hour.temp_pred,
        humidity: hour.humidity_pred
      }));

      setChartData(formattedData);
      setCity(data.city);
      
      // Actualizar la temperatura seleccionada
      const selectedIndex = data.selectedHourIndex ?? 0;
      setSelectedTemperature(data.hours[selectedIndex]?.temp_pred ?? null);
    }
  };

  // Función para formatear la fecha/hora (extrae solo la hora del string ISO)
  const formatDateTime = (dateTimeStr: string) => {
    try {
      const date = new Date(dateTimeStr);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      // Si hay error en el formato, devuelve el string original
      return dateTimeStr.split(' ')[1] || dateTimeStr;
    }
  };

  // Calcular los valores actuales (temperatura y humedad)
  const selectedIndex = forecastData?.selectedHourIndex ?? 0;

  const currentTemperature = forecastData
    ? forecastData.hours[selectedIndex]?.temp_pred.toFixed(1)
    : weather.temperature;

  const currentHumidity = forecastData
    ? forecastData.hours[selectedIndex]?.humidity_pred.toFixed(0)
    : weather.humidity;
  
  useEffect(() => {
    // Al cargar la página, obtener la ubicación actual
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        position => {
          const { latitude, longitude } = position.coords;
          setForecastData({
            city: "Manizales",
            location: {
              lat: latitude, lon: longitude,
              name: "",
              tz_id: "",
              region: "",
              country: "",
              localtime: "",
              localtime_epoch: 0
            },
            hours: [],
          });
        },
        error => {
          console.error("Error obteniendo ubicación:", error);
        }
      );
    } else {
      console.error("Geolocalización no soportada por el navegador");
    }
  }, []);
    
  return (
    <div className={styles.dashboardContainer}>
      
      <div className={styles.weatherControls}>
        <WeatherMap onForecastUpdate={handleForecastUpdate} />
      </div>

      <div className={styles.weatherInfo}>
        <h1>{forecastData?.city}</h1>
        <h2>{currentTemperature}°C</h2>
        <div className={styles.weatherDetails}>
          <p>{weather.description}</p>
          <p>Wind: {weather.wind} kph</p>
          <p>Humidity: {currentHumidity}%</p>
        </div>
      </div>

      

      

      <div className={styles.mapContainer}>
        {forecastData && (
          <div className={styles.mapArea}>
            <MapComponent
              latitude={forecastData.location.lat}
              longitude={forecastData.location.lon}
              showTemperature={true}
              selectedTemperature={selectedTemperature}
            />
          </div>
        )}
      </div>

      {/* Nuevo componente WeatherDashboard */}
      {forecastData && (
        <div className={styles.weatherDashboardContainer}>
          <WeatherDashboard forecast={forecastData} />
        </div>
      )}
      
      <ChatBotMap />
      {/* 
      <div className={styles.chartContainer}>
      <h2>Hourly Forecast</h2>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <XAxis dataKey="time" />
          <YAxis
            domain={['dataMin - 2', 'dataMax + 2']}
            tickFormatter={(value) => value.toFixed(1)} 
          />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="temp"
            stroke="#007bff"
            name="Temperature (°C)"
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
    */}
    </div>
  );
};

export default Dashboard;
