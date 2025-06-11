import React, { useState } from "react";
import { useAuth } from '../context/AuthContext'
import UserMenu from "../userMenu/UserMenu";
import styles from "./Navbar.module.css";

interface NavbarProps {
  onLoginClick: () => void;
  onRegisterClick: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onLoginClick, onRegisterClick }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, loading } = useAuth();

  // Cerrar menú móvil cuando se hace clic en una opción
  const handleMenuClose = () => {
    setIsOpen(false);
  };

  const handleLoginClick = () => {
    onLoginClick();
    handleMenuClose();
  };

  const handleRegisterClick = () => {
    onRegisterClick();
    handleMenuClose();
  };

  if (loading) {
    return (
      <nav className={styles.navbar}>
        <div className={styles.navbarLogo}>
          <a href="#" className={styles.navbarLink}>
            ClimateViz
          </a>
        </div>
        <div className={styles.loadingSpinner}></div>
      </nav>
    );
  }

  return (
    <nav className={styles.navbar}>
      <div className={styles.navbarLogo}>
        <a href="#" className={styles.navbarLink}>
          ClimateViz
        </a>
      </div>

      {/* UserMenu visible siempre en desktop cuando está autenticado */}
      {isAuthenticated && (
        <div className={styles.desktopUserMenu}>
          <UserMenu onMenuAction={handleMenuClose} />
        </div>
      )}

      {/* Menú hamburguesa - solo visible en móvil */}
      <div 
        className={styles.menuIcon} 
        onClick={() => setIsOpen(!isOpen)}
        style={{ display: isAuthenticated ? 'none' : 'block' }} // Ocultar si está autenticado en móvil
      >
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
      </div>

      {/* Avatar visible en móvil cuando está autenticado */}
      {isAuthenticated && (
        <div className={styles.mobileUserMenu}>
          <UserMenu onMenuAction={handleMenuClose} />
        </div>
      )}

      {/* Menú principal - solo para usuarios no autenticados */}
      {!isAuthenticated && (
        <div className={`${styles.navbarMenu} ${isOpen ? styles.show : ""}`}>
          <button
            className={`${styles.navbarButton} ${styles.signup}`}
            onClick={handleRegisterClick}
          >
            Sign up
          </button>
          <button
            className={`${styles.navbarButton} ${styles.login}`}
            onClick={handleLoginClick}
          >
            Log in
          </button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
