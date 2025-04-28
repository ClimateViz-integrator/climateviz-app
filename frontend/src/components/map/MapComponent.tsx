import React, { useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "leaflet.heat";

// Fix para íconos
const customIcon = new L.Icon({
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// Tipos para los datos del heatmap
type HeatmapPoint = { lat: number; lng: number; intensity: number };

interface MapProps {
  latitude: number;
  longitude: number;
  showTemperature?: boolean;
  selectedTemperature: number | null;
}

// Componente de capa de temperatura
const TemperatureLayer = ({ points }: { points: HeatmapPoint[] }) => {
  const map = useMap();
  const heatLayerRef = useRef<any>(null);

  useEffect(() => {
    if (!points || points.length === 0) return;
  
    const heatMapData = points.map(p => [p.lat, p.lng, p.intensity]);
  
    if (!heatLayerRef.current) {
      // primera vez: creas la capa
      heatLayerRef.current = (L as any).heatLayer(heatMapData, {
        radius: 70,
        blur: 40,
        maxZoom: 10,
        gradient: { 0.0: 'gray', 0.2: 'blue', 0.5: 'lime', 0.8: 'orange', 1.0: 'red' },
      }).addTo(map);
    } else {
      // sólo actualizas los datos (y por tanto el color/intensidad)
      heatLayerRef.current.setLatLngs(heatMapData);
    }
  }, [points, map]);
  

  return null;
};

// Componente para actualizar la vista del mapa
const UpdateMapView = ({ latitude, longitude }: { latitude: number; longitude: number }) => {
  const map = useMap();
  
  useEffect(() => {
    map.setView([latitude, longitude], map.getZoom());
  }, [latitude, longitude, map]);
  
  return null;
};

const MapComponent: React.FC<MapProps> = ({
  latitude,
  longitude,
  showTemperature = true,
  selectedTemperature
}) => {
  // Rango esperado de temperaturas
  const minTemp = -10;
  const maxTemp = 40;

  // Datos del heatmap, solo si hay temperatura seleccionada
  const heatmapData: HeatmapPoint[] = [];
  if (selectedTemperature !== null && showTemperature) {
    const normalizedTemp = Math.max(0, Math.min(1, (selectedTemperature - minTemp) / (maxTemp - minTemp)));
    heatmapData.push({ lat: latitude, lng: longitude, intensity: normalizedTemp });
  }

  return (
    <div className="map-container-wrapper" style={{ position: 'relative', height: '500px', width: '100%' }}>
      {/* Contenedor del mapa con z-index bajo */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, zIndex: 1 }}>
        <MapContainer
          center={[latitude, longitude]}
          zoom={12}
          style={{ height: "100%", width: "100%" }}
          className="leaflet-container"
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          
          <Marker position={[latitude, longitude]} icon={customIcon}>
            <Popup>Ubicación seleccionada</Popup>
          </Marker>

          <UpdateMapView latitude={latitude} longitude={longitude} />
          
          {selectedTemperature !== null && showTemperature && (
            <TemperatureLayer points={heatmapData} />
          )}
        </MapContainer>
      </div>
    </div>
  );
};

export default MapComponent;