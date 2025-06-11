import React, { useState } from "react";
import styles from "./Register.module.css";

interface RegisterProps {
  onClose: () => void;
  onSwitchToLogin?: () => void; // Para cambiar al login después del registro
}

const Register: React.FC<RegisterProps> = ({ onClose, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [serverError, setServerError] = useState("");
  const [termsAccepted, setTermsAccepted] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [id]: value,
    }));
    // Clear error when user types
    if (errors[id]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[id];
        return newErrors;
      });
    }
    // Clear server error when user types
    if (serverError) {
      setServerError("");
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/^\S+@\S+\.\S+$/.test(formData.email)) {
      newErrors.email = "Email is invalid";
    }

    if (!formData.username) {
      newErrors.username = "Username is required";
    } else if (formData.username.length < 4) {
      newErrors.username = "Username must be at least 4 characters";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 8 characters";
    }

    if (!termsAccepted) {
      newErrors.terms = "You must accept the terms and conditions";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setServerError("");
    setSuccessMessage("");

    try {
      const response = await fetch("http://localhost:9000/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Registro exitoso
        if (data.numOfErrors === 0) {
          setSuccessMessage(data.message || "Registration successful! Please check your email to verify your account.");
          
          // Limpiar formulario
          setFormData({
            email: "",
            username: "",
            password: "",
            confirmPassword: "",
          });
          setTermsAccepted(false);

          // Opcional: cerrar modal después de unos segundos
          setTimeout(() => {
            onClose();
            if (onSwitchToLogin) {
              onSwitchToLogin();
            }
          }, 3000);
        } else {
          // Hay errores de validación del servidor
          setServerError(data.message || "Registration failed");
        }
      } else {
        // Error HTTP
        setServerError(data.message || "Registration failed. Please try again.");
      }
    } catch (error) {
      console.error("Registration error:", error);
      setServerError("Network error. Please check your connection and try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSwitchToLogin = () => {
    onClose();
    if (onSwitchToLogin) {
      onSwitchToLogin();
    }
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.registerBox}>
        <button
          className={styles.closeButton}
          onClick={onClose}
          aria-label="Close registration form"
        >
          ×
        </button>

        <div className={styles.registerHeader}>
          <h2 className={styles.title}>Join ClimateViz</h2>
          <p className={styles.subtitle}>
            Create your account to access climate data insights
          </p>
        </div>

        <form className={styles.form} onSubmit={handleSubmit} noValidate>
          {/* Mensaje de éxito */}
          {successMessage && (
            <div className={styles.successMessage}>
              ✅ {successMessage}
            </div>
          )}

          {/* Mensaje de error del servidor */}
          {serverError && (
            <div className={styles.serverError}>
              ❌ {serverError}
            </div>
          )}

          <div className={styles.inputGroup}>
            <label htmlFor="email" className={styles.inputLabel}>
              Email
            </label>
            <input
              type="email"
              id="email"
              className={`${styles.input} ${
                errors.email ? styles.inputError : ""
              }`}
              value={formData.email}
              onChange={handleChange}
              placeholder="your@email.com"
              required
              disabled={isSubmitting}
            />
            {errors.email && (
              <span className={styles.errorMessage}>{errors.email}</span>
            )}
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="username" className={styles.inputLabel}>
              Username
            </label>
            <input
              type="text"
              id="username"
              className={`${styles.input} ${
                errors.username ? styles.inputError : ""
              }`}
              value={formData.username}
              onChange={handleChange}
              placeholder="Choose a username"
              required
              disabled={isSubmitting}
            />
            {errors.username && (
              <span className={styles.errorMessage}>{errors.username}</span>
            )}
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="password" className={styles.inputLabel}>
              Password
            </label>
            <input
              type="password"
              id="password"
              className={`${styles.input} ${
                errors.password ? styles.inputError : ""
              }`}
              value={formData.password}
              onChange={handleChange}
              placeholder="At least 6 characters"
              required
              disabled={isSubmitting}
            />
            {errors.password && (
              <span className={styles.errorMessage}>{errors.password}</span>
            )}
          </div>

          <div className={styles.termsContainer}>
            <input
              type="checkbox"
              id="terms"
              className={styles.checkbox}
              checked={termsAccepted}
              onChange={(e) => setTermsAccepted(e.target.checked)}
              required
              disabled={isSubmitting}
            />
            <label htmlFor="terms" className={styles.termsText}>
              I agree to the{" "}
              <a href="#" className={styles.termsLink}>
                Terms of Service
              </a>{" "}
              and{" "}
              <a href="#" className={styles.termsLink}>
                Privacy Policy
              </a>
            </label>
            {errors.terms && (
              <span className={styles.errorMessage}>{errors.terms}</span>
            )}
          </div>

          <button
            type="submit"
            className={styles.registerButton}
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <span className={styles.spinner}></span>
            ) : (
              "Create Account"
            )}
          </button>

          <p className={styles.loginText}>
            Already have an account?{" "}
            <button
              type="button"
              className={styles.loginLink}
              onClick={handleSwitchToLogin}
              disabled={isSubmitting}
            >
              Log in
            </button>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Register;
