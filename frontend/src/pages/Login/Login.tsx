import React, { useState } from "react";
import styles from "./Login.module.css";
import ForgotPassword from "../../components/forgot_password/ForgotPassword";

import { useAuth } from '../../components/context/AuthContext';
import authService from '../../components/services_api/authService';

interface LoginProps {
  onClose: () => void;
  onLoginSuccess?: (token: string) => void;
}

const Login: React.FC<LoginProps> = ({ onClose, onLoginSuccess }) => {
  const [email, setEmail] = useState(""); // Cambiado de username a email
  const [password, setPassword] = useState("");
  const [keepLoggedIn, setKeepLoggedIn] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const response = await authService.login({ email, password });

      if (response.jwt) {
        // Decodificar token para obtener info del usuario
        const userInfo = authService.decodeToken(response.jwt);
        
        if (userInfo) {
          // Usar el contexto para manejar el login
          login(response.jwt, userInfo);
          onClose();
        } else {
          setErrorMessage("Invalid token received");
        }
      } else {
        setErrorMessage(response.error || "Authentication failed");
      }
    } catch (error) {
      setErrorMessage("Network error. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleForgotPasswordClick = (e: React.MouseEvent) => {
    e.preventDefault();
    setShowForgotPassword(true);
  };

  const handleBackToLogin = () => {
    setShowForgotPassword(false);
  };

  if (showForgotPassword) {
    return (
      <ForgotPassword 
        onClose={onClose} 
        onBackToLogin={handleBackToLogin}
      />
    );
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.loginBox}>
        <button
          className={styles.closeButton}
          onClick={onClose}
          aria-label="Close login form"
        >
          ×
        </button>
        <div className={styles.loginHeader}>
          <h2 className={styles.title}>Welcome Back</h2>
          <p className={styles.subtitle}>Log in to access Climate Data</p>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          {errorMessage && (
            <div className={styles.errorMessage}>
              {errorMessage}
            </div>
          )}

          <div className={styles.inputGroup}>
            <label htmlFor="email" className={styles.inputLabel}>
              Email
            </label>
            <input
              type="email"
              id="email"
              className={styles.input}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="password" className={styles.inputLabel}>
              Password
            </label>
            <input
              type="password"
              id="password"
              className={styles.input}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>

          <div className={styles.optionsContainer}>
            <div className={styles.checkboxContainer}>
              <input
                type="checkbox"
                id="keepLoggedIn"
                checked={keepLoggedIn}
                onChange={(e) => setKeepLoggedIn(e.target.checked)}
                className={styles.checkbox}
              />
              <label htmlFor="keepLoggedIn" className={styles.checkboxLabel}>
                Remember me
              </label>
            </div>

            <button
              type="button"
              onClick={handleForgotPasswordClick}
              className={styles.forgotPassword}
            >
              Forgot password?
            </button>
          </div>

          <button
            type="submit"
            className={styles.loginButton}
            disabled={isSubmitting}
          >
            {isSubmitting ? <span className={styles.spinner}></span> : "Log In"}
          </button>

          <div className={styles.divider}>
            <span>or</span>
          </div>

          <button type="button" className={styles.socialButton}>
            <svg className={styles.socialIcon} viewBox="0 0 24 24">
              <path d="M12.545 10.239v3.821h5.445c-0.712 2.315-2.647 3.972-5.445 3.972-3.332 0-6.033-2.701-6.033-6.032s2.701-6.032 6.033-6.032c1.498 0 2.866 0.549 3.921 1.453l2.814-2.814c-1.784-1.667-4.166-2.685-6.735-2.685-5.522 0-10 4.477-10 10s4.478 10 10 10c8.396 0 10-7.524 10-10 0-0.768-0.081-1.526-0.219-2.261h-9.781z"></path>
            </svg>
            Continue with Google
          </button>

          <p className={styles.signupText}>
            Don't have an account?{" "}
            <a href="#" className={styles.signupLink}>
              Sign up
            </a>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Login;
