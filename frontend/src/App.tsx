import "./App.css";

import { useState } from "react";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import Dashboard from "./pages/DashboardPublic/DashboardPublic";
import Navbar from "./components/navbar/Navbar";

function App() {
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  const handleOpenLogin = () => setShowLogin(true);
  const handleCloseLogin = () => setShowLogin(false);

  const handleOpenRegister = () => setShowRegister(true);
  const handleCloseRegister = () => setShowRegister(false);

  return (
    <>
      <Navbar
        onLoginClick={handleOpenLogin}
        onRegisterClick={handleOpenRegister}
      />
      {showLogin && <Login onClose={handleCloseLogin} />}
      {showRegister && <Register onClose={handleCloseRegister} />}
      <Dashboard />
    </>
  );
}

export default App;
