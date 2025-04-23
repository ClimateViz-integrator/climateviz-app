import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "leaflet.heat";
import { useEffect } from "react";

// Fix para íconos (TypeScript compatible)
const customIcon = new L.Icon({
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// Tipos para los datos del heatmap
type HeatmapPoint = [number, number, number]; // [lat, lng, intensity]

// Componente de capa de temperatura
const TemperatureLayer = ({ points }: { points: HeatmapPoint[] }) => {
  const map = useMap();

  useEffect(() => {
    if (!points || points.length === 0) return;

    const heatLayer = L.heatLayer(points, {
      radius: 70,
      blur: 40,
      maxZoom: 10,
      gradient: {0.0: 'gray', 0.2: 'blue', 0.5: 'lime', 0.8: 'orange', 1.0: 'red' },
    }).addTo(map);

    return () => {
      map.removeLayer(heatLayer);
    };
  }, [points, map]);

  return null;
};

interface MapProps {
  latitude: number;
  longitude: number;
  showTemperature?: boolean;
}

const MapComponent: React.FC<MapProps> = ({
  latitude,
  longitude,
  showTemperature = true
}) => {
  // Ejemplo de temperaturas reales
  const temperaturePoints = [
    { lat: latitude, lng: longitude, temp: 25 }
  ];

  // Rango esperado de temperaturas (ajústalo según el contexto real)
  const minTemp = -10;
  const maxTemp = 40;

  // Normalización de temperaturas
  const heatmapData: HeatmapPoint[] = temperaturePoints.map(({ lat, lng, temp }) => {
    const normalized = Math.max(0, Math.min(1, (temp - minTemp) / (maxTemp - minTemp)));
    return [lat, lng, normalized];
  });

  return (
    <MapContainer
      center={[latitude, longitude]}
      zoom={12}
      style={{ height: "500px", width: "100%" }}
      className="leaflet-container"
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />
      <Marker position={[latitude, longitude]} icon={customIcon}>
        <Popup>Ubicación seleccionada</Popup>
      </Marker>

      {showTemperature && <TemperatureLayer points={heatmapData} />}
    </MapContainer>
  );
};

export default MapComponent;
