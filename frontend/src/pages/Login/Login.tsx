import React from "react";
import styles from "./Login.module.css";

const Login: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.loginBox}>
        <h2 className={styles.title}>Log in to Climate Data</h2>
        <form className={styles.form}>
          <label htmlFor="username">Username or email</label>
          <input type="text" id="username" className={styles.input} />

          <label htmlFor="password">Password</label>
          <input type="password" id="password" className={styles.input} />

          <div className={styles.checkboxContainer}>
            <input type="checkbox" id="keepLoggedIn" />
            <label htmlFor="keepLoggedIn">Keep me logged in</label>
          </div>

          <a href="#" className={styles.forgotPassword}>
            Forgot password?
          </a>

          <button type="submit" className={styles.loginButton}>
            Log in
          </button>

          <p className={styles.signupText}>
            Don't have an account? <a href="#">Sign up</a>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Login;
