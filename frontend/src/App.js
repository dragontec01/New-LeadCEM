import "@/App.css";
import { useEffect } from "react";

const REAL_SYSTEM_URL = "https://app.whatcem.com/admin";

function App() {
  useEffect(() => {
    const timer = setTimeout(() => {
      window.location.replace(REAL_SYSTEM_URL);
    }, 1200);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="real-system-preview" data-testid="real-system-preview-container">
      <header className="real-system-header" data-testid="real-system-preview-header">
        <div>
          <h1 data-testid="real-system-preview-title">Vista previa del sistema real WhatCEM</h1>
          <p data-testid="real-system-preview-subtitle">
            Cargando directamente tu instancia: {REAL_SYSTEM_URL}
          </p>
        </div>
        <a
          data-testid="real-system-open-new-tab-link"
          href={REAL_SYSTEM_URL}
          target="_self"
          rel="noreferrer"
        >
          Entrar ahora
        </a>
      </header>

      <main className="real-system-frame-wrapper" data-testid="real-system-frame-wrapper">
        <div className="real-system-message" data-testid="real-system-redirect-message">
          Redirigiendo al sistema real para que puedas iniciar sesión con tus credenciales...
        </div>
      </main>
    </div>
  );
}

export default App;