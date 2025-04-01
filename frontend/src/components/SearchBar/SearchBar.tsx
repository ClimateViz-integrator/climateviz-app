import { useState } from "react";
import  styles from "./SearchBar.module.css";

interface SearchBarProps {
  onSearch: (city: string) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [city, setCity] = useState("");

  const handleSearch = () => {
    if (city.trim() !== "") {
      onSearch(city);
    }
  };

  return (
    <div className={styles.searchBar}>
      <input
        type="text"
        placeholder="Search city..."
        value={city}
        onChange={(e) => setCity(e.target.value)}
      />
      <button onClick={handleSearch}>🔍</button>
    </div>
  );
};

export default SearchBar;
