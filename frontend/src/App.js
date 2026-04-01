import "@/App.css";

const REAL_SYSTEM_URL = "https://app.whatcem.com/admin";

function App() {
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
          target="_blank"
          rel="noreferrer"
        >
          Abrir en pestaña nueva
        </a>
      </header>

      <main className="real-system-frame-wrapper" data-testid="real-system-frame-wrapper">
        <iframe
          data-testid="real-system-iframe"
          src={REAL_SYSTEM_URL}
          title="WhatCEM Sistema Real"
          className="real-system-frame"
          allow="clipboard-read; clipboard-write"
        />
      </main>
    </div>
  );
}

export default App;