import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

const customIcon = new L.Icon({
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

interface MapProps {
  latitude: number;
  longitude: number;
}

const MapComponent: React.FC<MapProps> = ({ latitude, longitude }) => {
  return (
    <MapContainer center={[latitude, longitude]} zoom={12} style={{ height: "400px", width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <Marker position={[latitude, longitude]} icon={customIcon}>
        <Popup>Ubicación seleccionada</Popup>
      </Marker>
    </MapContainer>
  );
};

export default MapComponent;
