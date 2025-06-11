import "./App.css";
import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import Dashboard from "./pages/DashboardPublic/DashboardPublic";
import Navbar from "./components/navbar/Navbar";
import ResetPassword from "./components/reset_password/ResetPassword"; // Nuevo componente
import { AuthProvider } from './components/context/AuthContext';
import EmailVerification from "./components/emailVerification/EmailVerification";

function App() {
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  const handleOpenLogin = () => {
    setShowRegister(false); // Cerrar register si está abierto
    setShowLogin(true);
  };
  const handleCloseLogin = () => setShowLogin(false);

  const handleOpenRegister = () => {
    setShowLogin(false); // Cerrar login si está abierto
    setShowRegister(true);
  };
  
  const handleCloseRegister = () => setShowRegister(false);

  // Función para cambiar de Register a Login
  const handleSwitchToLogin = () => {
    setShowRegister(false);
    setShowLogin(true);
  };

  // Función para cambiar de Login a Register (opcional)
  const handleSwitchToRegister = () => {
    setShowLogin(false);
    setShowRegister(true);
  };

  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Ruta principal */}
          <Route
            path="/"
            element={
              <>
                <Navbar
                  onLoginClick={handleOpenLogin}
                  onRegisterClick={handleOpenRegister}
                />
                {showLogin && <Login onClose={handleCloseLogin} onSwitchToRegister={handleSwitchToRegister} />}
                {showRegister && <Register onClose={handleCloseRegister} onSwitchToLogin={handleSwitchToLogin} />}
                <Dashboard />
              </>
            }
          />

          {/* Ruta para reset password */}
          <Route path="/reset-password" element={<ResetPassword />} />

          {/* Ruta para verificación de email (opcional) */}
          <Route path="/verify" element={<EmailVerification />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
