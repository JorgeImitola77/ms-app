import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";

// Importación de tus páginas y componentes
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

// 🛡️ COMPONENTE GUARDIA: Protege las rutas privadas
const RutaPrivada = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth0();

  // Mientras Auth0 verifica si hay una sesión activa, mostramos algo de carga
  if (isLoading) return <div className="flex justify-center items-center h-screen">Cargando seguridad...</div>;
  
  // Si no está autenticado, lo devolvemos a la landing (o al /login)
  if (!isAuthenticated) return <Navigate to="/" />;

  // Si está autenticado, lo dejamos pasar al componente (Layout)
  return children;
};

export default function App() {
  const { isAuthenticated, getAccessTokenSilently } = useAuth0();

  // 🔑 EXTRAER EL TOKEN: Lo imprimimos en consola para que lo uses en Swagger
  useEffect(() => {
    const obtenerToken = async () => {
      if (isAuthenticated) {
        try {
          const accessToken = await getAccessTokenSilently();
          console.log("==== TOKEN PARA SWAGGER ====");
          console.log(accessToken);
          console.log("============================");
          
          // Opcional: Aquí podrías guardar el token en localStorage si lo necesitas para tus peticiones fetch/axios
          // localStorage.setItem("token_explorapp", accessToken);
        } catch (e) {
          console.error("Error obteniendo el token de Auth0", e);
        }
      }
    };
    obtenerToken();
  }, [isAuthenticated, getAccessTokenSilently]);

  return (
    <BrowserRouter>
      <Routes>
        {/* === RUTAS PÚBLICAS === */}
        <Route path="/" element={<Landing />} />
        
        {/* Nota: Si usas el Universal Login de Auth0, esta vista local de Login podría ser redundante, 
            pero puedes usarla para colocar el botón de loginWithRedirect() */}
        <Route path="/login" element={<Login />} />

        {/* === RUTAS PRIVADAS (PROTEGIDAS POR AUTH0) === */}
        <Route 
          path="/app" 
          element={
            <RutaPrivada>
              <Layout />
            </RutaPrivada>
          }
        >
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