import React, { useState } from "react";
import styles from "./Navbar.module.css";

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className={styles.navbar}>
      <div className={styles.navbarLogo}>
        <a href="#" className={styles.navbarLink}>
          ClimateViz
        </a>
      </div>

      {/* Botón Hamburguesa */}
      <div className={styles.menuIcon} onClick={() => setIsOpen(!isOpen)}>
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
        <div className={`${styles.bar} ${isOpen ? styles.open : ""}`} />
      </div>

      {/* Menú */}
      <div className={`${styles.navbarMenu} ${isOpen ? styles.show : ""}`}>
        <button className={`${styles.navbarButton} ${styles.signup}`}>Sign up</button>
        <button className={`${styles.navbarButton} ${styles.login}`}>Log in</button>
      </div>
    </nav>
  );
};

export default Navbar;
