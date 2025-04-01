import React, { useState } from 'react';
import styles from './Register.module.css';

const Register: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setError('');
    // Aquí puedes manejar la lógica de registro
    console.log('Username:', username);
    console.log('Password:', password);
  };

  return (
    <div className={styles.registerContainer}>
      <form onSubmit={handleSubmit} className={styles.registerForm}>
        <h2>Create an account</h2>
        <div className={styles.inputGroup}>
          <label htmlFor="username">Email or username</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <p className={styles.helperText}>Must be at least 6 characters</p>
        </div>
        <div className={styles.inputGroup}>
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <p className={styles.helperText}>At least 8 characters</p>
        </div>
        <div className={styles.inputGroup}>
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
          {error && <p className={styles.errorText}>{error}</p>}
        </div>
        <button type="submit" className={styles.signUpButton}>Sign Up</button>
        <p className={styles.termsText}>
          By clicking Sign Up, you agree to our <a href="#">Terms of Service</a> and have read our <a href="#">Privacy Policy</a>
        </p>
        <p className={styles.loginText}>
          Already have an account? <a href="#">Login</a>
        </p>
      </form>
    </div>
  );
};

export default Register;