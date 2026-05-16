import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import { Auth0Provider } from "@auth0/auth0-react";
import './index.css';

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Auth0Provider
      domain="dev-i1aenfwhn0il1ty6.us.auth0.com"
      clientId="iVNnme8tydK9kasEUHCvzlzOuqNEJcow"
      
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: "https://api.explorapp",
      }}
    >
      <App />
    </Auth0Provider>
  </StrictMode>
);