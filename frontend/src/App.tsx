
import './App.css'
import DashboardPrincipal from './pages/DashboardPrincipal/DashboardPrincipal'
import Login from './pages/Login/Login'
import Register from './pages/Register/Register'
import Dashboard from './pages/DashboardPublic/DashboardPublic'
import MapComponent from './components/map/MapComponent'
import Navbar from './components/navbar/Navbar'

function App() {

  return (
    <>
      <Navbar />
      {/* <DashboardPrincipal /> */}
      {/* <Login /> */}
      {/* <Register /> */}
      <Dashboard />
      {/* <MapComponent latitude={40.73061} longitude={-73.935242} /> */}
      
      
    </>


  )
}

export default App
