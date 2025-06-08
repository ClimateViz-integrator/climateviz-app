import React, { useState } from "react";
import styles from "./Navbar.module.css";

interface NavbarProps {
  onLoginClick: () => void;
  onRegisterClick: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onLoginClick, onRegisterClick }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className={styles.navbar}>
      <div className={styles.navbarLogo}>
        <a href="#" className={styles.navbarLink}>
          ClimateViz
        </a>
      </div>

      <div className={styles.menuIcon} onClick={() => setIsOpen(!isOpen)}>
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
      </div>

      <div className={`${styles.navbarMenu} ${isOpen ? styles.show : ""}`}>
        <button
          className={`${styles.navbarButton} ${styles.signup}`}
          onClick={onRegisterClick}
        >
          Sign up
        </button>
        <button
          className={`${styles.navbarButton} ${styles.login}`}
          onClick={onLoginClick}
        >
          Log in
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
