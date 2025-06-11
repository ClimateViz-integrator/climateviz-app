import React, { useState } from "react";
import styles from "./ForgotPassword.module.css";

interface ForgotPasswordProps {
  onClose: () => void;
  onBackToLogin: () => void;
}

const ForgotPassword: React.FC<ForgotPasswordProps> = ({ onClose, onBackToLogin }) => {
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage("");

    try {
      const response = await fetch("http://localhost:9000/auth/forgot-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setIsSuccess(true);
        setMessage("Password reset email sent successfully. Please check your inbox.");
      } else {
        setIsSuccess(false);
        setMessage(data.error || "An error occurred. Please try again.");
      }
    } catch (error) {
      setIsSuccess(false);
      setMessage("Network error. Please check your connection and try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.forgotPasswordBox}>
        <button
          className={styles.closeButton}
          onClick={onClose}
          aria-label="Close forgot password form"
        >
          ×
        </button>
        
        <div className={styles.header}>
          <h2 className={styles.title}>Forgot Password?</h2>
          <p className={styles.subtitle}>
            Enter your email address and we'll send you a link to reset your password.
          </p>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.inputGroup}>
            <label htmlFor="email" className={styles.inputLabel}>
              Email Address
            </label>
            <input
              type="email"
              id="email"
              className={styles.input}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email address"
              required
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
            disabled={isSubmitting}
          >
            {isSubmitting ? <span className={styles.spinner}></span> : "Send Reset Link"}
          </button>

          <div className={styles.backToLogin}>
            <button
              type="button"
              onClick={onBackToLogin}
              className={styles.backButton}
            >
              ← Back to Login
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ForgotPassword;
