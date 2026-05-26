import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth0 } from "@auth0/auth0-react";

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

const RutaPrivada = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth0();
  if (isLoading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
};

export default function App() {
  const { isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen bg-[#fafafa]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-brand-600 border-t-transparent animate-spin" />
          <p className="text-sm text-surface-500 font-body">Verificando sesión...</p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      {/* Rutas públicas — redirigen a /app si ya hay sesión activa */}
      <Route path="/" element={isAuthenticated ? <Navigate to="/app" replace /> : <Landing />} />
      <Route path="/login" element={isAuthenticated ? <Navigate to="/app" replace /> : <Login />} />

      {/* Rutas protegidas */}
      <Route path="/app" element={<RutaPrivada><Layout /></RutaPrivada>}>
        <Route index element={<Dashboard />} />
        <Route path="crear" element={<CrearPersona />} />
        <Route path="consultar" element={<ConsultarPersona />} />
        <Route path="modificar" element={<ModificarPersona />} />
        <Route path="borrar" element={<BorrarPersona />} />
        <Route path="logs" element={<Logs />} />
        <Route path="chat" element={<ChatRAG />} />
      </Route>
    </Routes>
  );
}
