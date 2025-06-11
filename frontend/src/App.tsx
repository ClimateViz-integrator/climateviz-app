import "./App.css";
import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import Dashboard from "./pages/DashboardPublic/DashboardPublic";
import Navbar from "./components/navbar/Navbar";
import ResetPassword from "./components/reset_password/ResetPassword"; // Nuevo componente

function App() {
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  const handleOpenLogin = () => setShowLogin(true);
  const handleCloseLogin = () => setShowLogin(false);

  const handleOpenRegister = () => setShowRegister(true);
  const handleCloseRegister = () => setShowRegister(false);

  return (
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
              {showLogin && <Login onClose={handleCloseLogin} />}
              {showRegister && <Register onClose={handleCloseRegister} />}
              <Dashboard />
            </>
          } 
        />
        
        {/* Ruta para reset password */}
        <Route path="/reset-password" element={<ResetPassword />} />
        
        {/* Ruta para verificación de email (opcional) */}
        <Route path="/verify" element={<div>Email verification page</div>} />
      </Routes>
    </Router>
  );
}

export default App;
