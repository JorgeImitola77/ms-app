import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Landing from './pages/landing'
import Login from './pages/Login'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import CrearPersona from './pages/CrearPersona'
import ConsultarPersona from './pages/ConsultarPersona'
import ModificarPersona from './pages/ModificarPersona'
import BorrarPersona from './pages/BorrarPersona'
import Logs from './pages/Logs'
import ChatRAG from './pages/ChatRAG'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />

        {/* App (authenticated) */}
        <Route path="/app" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="crear" element={<CrearPersona />} />
          <Route path="consultar" element={<ConsultarPersona />} />
          <Route path="modificar" element={<ModificarPersona />} />
          <Route path="borrar" element={<BorrarPersona />} />
          <Route path="logs" element={<Logs />} />
          <Route path="chat" element={<ChatRAG />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
