import React, { useState } from "react";
import { useAuth } from "../../components/context/AuthContext";
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

      {/* Menú hamburguesa - solo visible en móvil */}
      <div className={styles.menuIcon} onClick={() => setIsOpen(!isOpen)}>
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
      </div>

      {/* Menú principal */}
      <div className={`${styles.navbarMenu} ${isOpen ? styles.show : ""}`}>
        {isAuthenticated ? (
          // Usuario autenticado - mostrar UserMenu
          <div className={styles.userMenuContainer}>
            <UserMenu />
          </div>
        ) : (
          // Usuario no autenticado - mostrar botones de login/register
          <>
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
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
