
import React from "react";
import styles from "./DashboardPrincipal.module.css";
import imagePrincipal from "../../assets/images/dashboard_principal_image.png";

const DashboardPrincipal: React.FC = () => {
  return (
    <div className={styles.dashboard}>
      {/* Sección Hero */}
      <section className={styles.hero}>
        <img 
          src={imagePrincipal}
          alt="Globe background" 
          className={styles.heroImage} 
        />
        <div className={styles.heroContent}>
          <h1 className={styles.heroTitle}>
            Visualize climate data, predict future trends
          </h1>
          <p className={styles.heroSubtitle}>
            We provide powerful tools to help you analyze, visualize, and predict climate data.
          </p>
        </div>
      </section>

      {/* Sección de Features */}
      <section className={styles.features}>
        <h2 className={styles.featuresTitle}>Features</h2>
        <p className={styles.featuresDescription}>
        We provide powerful tools to help you analyze, visualize, and predict climate data. Our platform is designed to be easy to use, yet powerful enough for advanced analysis and modeling
        </p>
        <div className={styles.cta}>
          <h3>Ready to start visualizing the future of our planet?</h3>
          <button className={styles.ctaButton}>Get Started</button>
        </div>
      </section>
    </div>
  );
};

export default DashboardPrincipal;
