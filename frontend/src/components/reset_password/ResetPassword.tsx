import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import styles from "./ResetPassword.module.css";

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);
  const [isValidToken, setIsValidToken] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const token = searchParams.get("code"); // Cambiado a "code" para coincidir con tu backend

  useEffect(() => {
    if (token) {
      validateToken();
    } else {
      setMessage("Invalid reset link");
      setIsLoading(false);
    }
  }, [token]);

  const validateToken = async () => {
    try {
      const response = await fetch(`http://localhost:9000/auth/reset-password?token=${token}`);
      const data = await response.json();

      if (response.ok && data.success) {
        setIsValidToken(true);
      } else {
        setMessage(data.error || "Invalid or expired reset link");
      }
    } catch (error) {
      setMessage("Network error. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setMessage("Passwords do not match");
      setIsSuccess(false);
      return;
    }

    if (newPassword.length < 6) {
      setMessage("Password must be at least 6 characters long");
      setIsSuccess(false);
      return;
    }

    setIsSubmitting(true);
    setMessage("");

    try {
      const response = await fetch("http://localhost:9000/auth/reset-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token,
          newPassword,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setIsSuccess(true);
        setMessage("Password updated successfully! Redirecting to home page...");
        
        // Redirigir a la página principal después de 3 segundos
        setTimeout(() => {
          navigate("/");
        }, 3000);
      } else {
        setIsSuccess(false);
        setMessage(data.error || "An error occurred. Please try again.");
      }
    } catch (error) {
      setIsSuccess(false);
      setMessage("Network error. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoHome = () => {
    navigate("/");
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingContainer}>
          <div className={styles.loadingSpinner}></div>
          <p>Validating reset link...</p>
        </div>
      </div>
    );
  }

  if (!isValidToken) {
    return (
      <div className={styles.container}>
        <div className={styles.errorContainer}>
          <h2>Invalid Reset Link</h2>
          <p>{message}</p>
          <button onClick={handleGoHome} className={styles.homeButton}>
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.resetPasswordBox}>
        <div className={styles.header}>
          <h2 className={styles.title}>Reset Password</h2>
          <p className={styles.subtitle}>Enter your new password below.</p>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.inputGroup}>
            <label htmlFor="newPassword" className={styles.inputLabel}>
              New Password
            </label>
            <input
              type="password"
              id="newPassword"
              className={styles.input}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Enter new password"
              required
              minLength={6}
            />
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="confirmPassword" className={styles.inputLabel}>
              Confirm Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              className={styles.input}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm new password"
              required
              minLength={6}
            />
          </div>

          {message && (
            <div className={`${styles.message} ${isSuccess ? styles.success : styles.error}`}>
              {message}
            </div>
          )}

          <button
            type="submit"
            className={styles.submitButton}
            disabled={isSubmitting || isSuccess}
          >
            {isSubmitting ? <span className={styles.spinner}></span> : "Update Password"}
          </button>

          <div className={styles.backToHome}>
            <button
              type="button"
              onClick={handleGoHome}
              className={styles.backButton}
            >
              ← Back to Home
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
