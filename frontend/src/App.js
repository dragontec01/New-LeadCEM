import { useEffect, useState } from "react";
import "@/App.css";
import axios from "axios";
import {
  BrowserRouter,
  Navigate,
  NavLink,
  Route,
  Routes,
  useNavigate,
} from "react-router-dom";
import { Toaster, toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API,
  headers: { "Content-Type": "application/json" },
});

const metricCards = [
  { key: "totalAssignments", label: "Asignaciones", testid: "lead-metric-total-assignments" },
  { key: "deliveryRate", label: "Entrega %", testid: "lead-metric-delivery-rate" },
  { key: "sentNotifications", label: "Enviadas", testid: "lead-metric-sent-notifications" },
  { key: "failedNotifications", label: "Fallidas", testid: "lead-metric-failed-notifications" },
];

const NavItem = ({ to, label, testid }) => (
  <NavLink
    to={to}
    data-testid={testid}
    className={({ isActive }) =>
      `sandbox-nav-link ${isActive ? "sandbox-nav-link-active" : ""}`
    }
  >
    {label}
  </NavLink>
);

const HomePage = () => (
  <section className="sandbox-grid" data-testid="home-dashboard-section">
    <Card data-testid="home-overview-card">
      <CardHeader>
        <CardTitle className="text-2xl">Sandbox WhatCEM Modernizado</CardTitle>
      </CardHeader>
      <CardContent>
        <p data-testid="home-overview-description" className="text-sm text-muted-foreground">
          Vista previa funcional para validar Sprint 1 y Sprint 2 en Emergent.
        </p>
      </CardContent>
    </Card>
    <Card data-testid="home-sprint-status-card">
      <CardHeader>
        <CardTitle className="text-xl">Estado de Sprints</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-3 text-sm" data-testid="home-sprint-status-list">
          <li>✅ Sprint 1: Ruleta de asignación + notificación WhatsApp (sandbox).</li>
          <li>✅ Sprint 2: Campañas IA WhatsApp + Voice IA (sandbox).</li>
          <li>🟡 Sprint 3 Fase 1: BI operativo consolidado.</li>
        </ul>
      </CardContent>
    </Card>
  </section>
);

const LeadAssignmentPage = () => {
  const [rules, setRules] = useState(null);
  const [metrics, setMetrics] = useState({});
  const [events, setEvents] = useState([]);
  const [testPhone, setTestPhone] = useState("+5215512345678");

  const load = async () => {
    try {
      const [rulesRes, metricsRes, eventsRes] = await Promise.all([
        api.get("/lead-assignment/rules"),
        api.get("/lead-assignment/metrics?days=30"),
        api.get("/lead-assignment/events"),
      ]);
      setRules(rulesRes.data);
      setMetrics(metricsRes.data);
      setEvents(eventsRes.data);
    } catch (error) {
      toast.error("No pudimos cargar Lead Router IA");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const saveRules = async () => {
    try {
      await api.post("/lead-assignment/rules", rules);
      toast.success("Reglas guardadas correctamente");
      await load();
    } catch {
      toast.error("No se pudieron guardar las reglas");
    }
  };

  const testNotification = async () => {
    try {
      await api.post("/lead-assignment/notifications/test", {
        phone: testPhone,
        message: "Prueba de notificación de asignación",
      });
      toast.success("Notificación de prueba enviada");
    } catch {
      toast.error("Falló la notificación de prueba");
    }
  };

  const autoAssign = async () => {
    try {
      await api.post("/lead-assignment/auto-assign-pending", {
        pendingConversationIds: [2001, 2002, 2003],
      });
      toast.success("Conversaciones asignadas automáticamente");
      await load();
    } catch {
      toast.error("No se pudo ejecutar la asignación automática");
    }
  };

  return (
    <section className="sandbox-grid" data-testid="lead-assignment-page">
      <Card data-testid="lead-rules-card">
        <CardHeader>
          <CardTitle className="text-xl">Reglas de Ruleta</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm">Modo</label>
            <Input
              data-testid="lead-rules-mode-input"
              value={rules?.mode || ""}
              onChange={(e) => setRules((prev) => ({ ...prev, mode: e.target.value }))}
            />
          </div>
          <div>
            <label className="text-sm">Canal fallback</label>
            <Input
              data-testid="lead-rules-fallback-input"
              value={rules?.fallbackChannelType || ""}
              onChange={(e) =>
                setRules((prev) => ({ ...prev, fallbackChannelType: e.target.value }))
              }
            />
          </div>
          <Button data-testid="lead-rules-save-button" onClick={saveRules}>
            Guardar reglas
          </Button>
        </CardContent>
      </Card>

      <Card data-testid="lead-kpi-card">
        <CardHeader>
          <CardTitle className="text-xl">KPIs Operativos (30 días)</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4">
          {metricCards.map((item) => (
            <div className="sandbox-metric" key={item.key} data-testid={item.testid}>
              <span>{item.label}</span>
              <strong>{metrics[item.key] ?? 0}</strong>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card data-testid="lead-actions-card">
        <CardHeader>
          <CardTitle className="text-xl">Acciones rápidas</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input
            data-testid="lead-test-phone-input"
            value={testPhone}
            onChange={(e) => setTestPhone(e.target.value)}
          />
          <div className="flex flex-wrap gap-3">
            <Button data-testid="lead-test-notification-button" onClick={testNotification}>
              Probar notificación
            </Button>
            <Button data-testid="lead-auto-assign-button" variant="outline" onClick={autoAssign}>
              Auto asignar pendientes
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card data-testid="lead-events-card">
        <CardHeader>
          <CardTitle className="text-xl">Eventos recientes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2" data-testid="lead-events-list">
            {events.length === 0 && <p className="text-sm text-muted-foreground">Sin eventos aún.</p>}
            {events.map((event) => (
              <div key={event.id} className="sandbox-list-row" data-testid={`lead-event-row-${event.id}`}>
                <span>{event.assignedToName || "Agente"}</span>
                <span>Conversación #{event.conversationId}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </section>
  );
};

const CampaignsPage = () => {
  const navigate = useNavigate();
  const [content, setContent] = useState("Hola {{1}}, tenemos una propuesta para ti");
  const [optimized, setOptimized] = useState("");
  const [variations, setVariations] = useState([]);
  const [schedule, setSchedule] = useState(null);
  const [campaignId, setCampaignId] = useState(null);

  const optimize = async () => {
    const { data } = await api.post("/campaigns/ai-optimize-content", {
      content,
      whatsappChannelType: "whatsapp_gupshup",
      messageType: "text",
      objective: "Más respuestas",
      tone: "profesional-cercano",
    });
    setOptimized(data.optimizedContent);
    toast.success("Contenido optimizado con IA");
  };

  const generateVariations = async () => {
    const { data } = await api.post("/campaigns/ai-generate-variations", {
      content,
      whatsappChannelType: "whatsapp_gupshup",
      messageType: "text",
    });
    setVariations(data.variations || []);
    toast.success("Variaciones A/B generadas");
  };

  const recommendSchedule = async () => {
    const { data } = await api.post("/campaigns/ai-recommend-schedule", {
      timezone: "America/Mexico_City",
      audienceSize: 1200,
      objective: "conversiones",
    });
    setSchedule(data);
    toast.success("Horario recomendado listo");
  };

  const saveDraft = async () => {
    const { data } = await api.post("/campaigns", {
      name: "Campaña Sprint2 Sandbox",
      description: "Flujo de validación Sprint 2",
      content: optimized || content,
      whatsappChannelType: "whatsapp_gupshup",
      campaignType: "immediate",
      messageType: "text",
      channelIds: [1],
      segmentId: 1,
    });
    setCampaignId(data.id);
    toast.success(`Borrador #${data.id} guardado`);
  };

  const launchCampaign = async () => {
    if (!campaignId) {
      toast.error("Primero guarda borrador");
      return;
    }
    await api.post(`/campaigns/${campaignId}/start`, {});
    toast.success("Campaña lanzada");
  };

  return (
    <section className="sandbox-grid" data-testid="campaigns-page">
      <Card data-testid="campaign-ai-builder-card">
        <CardHeader>
          <CardTitle className="text-xl">Campaign Builder IA</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            data-testid="campaign-content-input"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
          <div className="flex flex-wrap gap-2">
            <Button data-testid="campaign-optimize-button" onClick={optimize}>
              Optimizar contenido
            </Button>
            <Button data-testid="campaign-variations-button" variant="outline" onClick={generateVariations}>
              Generar A/B
            </Button>
            <Button data-testid="campaign-schedule-button" variant="outline" onClick={recommendSchedule}>
              Recomendar horario
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button data-testid="campaign-save-draft-button" onClick={saveDraft}>
              Guardar borrador
            </Button>
            <Button data-testid="campaign-launch-button" variant="secondary" onClick={launchCampaign}>
              Lanzar campaña
            </Button>
            <Button
              data-testid="campaign-dashboard-open-voice-ai-button"
              variant="ghost"
              onClick={() => navigate("/campaigns/voice")}
            >
              Ir a Voice AI
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card data-testid="campaign-optimized-card">
        <CardHeader>
          <CardTitle className="text-xl">Resultado IA</CardTitle>
        </CardHeader>
        <CardContent>
          <p data-testid="campaign-optimized-content" className="text-sm">
            {optimized || "Aquí verás la versión optimizada"}
          </p>
        </CardContent>
      </Card>

      <Card data-testid="campaign-variations-card">
        <CardHeader>
          <CardTitle className="text-xl">Variaciones</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2" data-testid="campaign-variations-list">
          {variations.length === 0 && <p className="text-sm text-muted-foreground">Sin variaciones aún.</p>}
          {variations.map((item) => (
            <div key={item.label} className="sandbox-list-row" data-testid={`campaign-variation-${item.label}`}>
              <strong>{item.label}</strong>
              <span>{item.content}</span>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card data-testid="campaign-schedule-card">
        <CardHeader>
          <CardTitle className="text-xl">Horario recomendado</CardTitle>
        </CardHeader>
        <CardContent>
          <p data-testid="campaign-recommendation-time" className="text-sm">
            {schedule?.recommendedAt || "Sin recomendación todavía"}
          </p>
        </CardContent>
      </Card>
    </section>
  );
};

const VoiceCampaignsPage = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [stats, setStats] = useState({});

  const loadVoice = async () => {
    const [campaignsRes, statsRes] = await Promise.all([
      api.get("/voice-campaigns"),
      api.get("/voice-campaigns/stats"),
    ]);
    setCampaigns(campaignsRes.data);
    setStats(statsRes.data);
  };

  useEffect(() => {
    loadVoice();
  }, []);

  const createVoiceCampaign = async () => {
    await api.post("/voice-campaigns", {
      name: "Voice Sprint2 Sandbox",
      prompt: "Hola {{contact_name}}, te llamamos de WhatCEM",
      twilioConnectionId: 1,
      contactIds: [1],
      aiProvider: "openai",
      aiModel: "gpt-4o-mini",
    });
    toast.success("Campaña de voz creada");
    await loadVoice();
  };

  const startVoiceCampaign = async () => {
    if (!campaigns[0]?.id) {
      toast.error("Crea una campaña primero");
      return;
    }
    await api.post(`/voice-campaigns/${campaigns[0].id}/start`, {
      contactIds: [1],
      twilioConnectionId: 1,
    });
    toast.success("Campaña de voz iniciada");
    await loadVoice();
  };

  return (
    <section className="sandbox-grid" data-testid="voice-campaigns-page">
      <Card data-testid="voice-actions-card">
        <CardHeader>
          <CardTitle className="text-xl">Voice AI Outbound</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button data-testid="voice-create-campaign-button" onClick={createVoiceCampaign}>
            Crear campaña de voz
          </Button>
          <Button data-testid="voice-start-campaign-button" variant="outline" onClick={startVoiceCampaign}>
            Iniciar campaña
          </Button>
        </CardContent>
      </Card>

      <Card data-testid="voice-stats-card">
        <CardHeader>
          <CardTitle className="text-xl">KPIs Voice IA</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4">
          <div className="sandbox-metric" data-testid="voice-stat-total-campaigns">
            <span>Campañas</span>
            <strong>{stats.totalCampaigns ?? 0}</strong>
          </div>
          <div className="sandbox-metric" data-testid="voice-stat-connection-rate">
            <span>Connection Rate</span>
            <strong>{stats.connectionRate ?? 0}%</strong>
          </div>
        </CardContent>
      </Card>

      <Card data-testid="voice-campaigns-list-card">
        <CardHeader>
          <CardTitle className="text-xl">Listado de campañas de voz</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2" data-testid="voice-campaigns-list">
          {campaigns.length === 0 && <p className="text-sm text-muted-foreground">No hay campañas aún.</p>}
          {campaigns.map((campaign) => (
            <div
              key={campaign.id}
              className="sandbox-list-row"
              data-testid={`voice-campaign-row-${campaign.id}`}
            >
              <strong>{campaign.name}</strong>
              <span>{campaign.status}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </section>
  );
};

const AnalyticsPage = () => {
  const [campaignStats, setCampaignStats] = useState({});
  const [voiceStats, setVoiceStats] = useState({});
  const [overview, setOverview] = useState(null);

  const loadAnalytics = async () => {
    const [campaignsRes, voiceRes, overviewRes] = await Promise.all([
      api.get("/campaigns/stats"),
      api.get("/voice-campaigns/stats"),
      api.get("/analytics/overview"),
    ]);
    setCampaignStats(campaignsRes.data);
    setVoiceStats(voiceRes.data);
    setOverview(overviewRes.data);
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  return (
    <section className="sandbox-grid" data-testid="analytics-page">
      <Card data-testid="analytics-bi-whatsapp-card">
        <CardHeader>
          <CardTitle className="text-xl">BI WhatsApp</CardTitle>
        </CardHeader>
        <CardContent>
          <p data-testid="analytics-whatsapp-total-campaigns">Campañas: {campaignStats.totalCampaigns ?? 0}</p>
          <p data-testid="analytics-whatsapp-delivery-rate">Entrega: {campaignStats.deliveryRate ?? 0}%</p>
        </CardContent>
      </Card>

      <Card data-testid="analytics-bi-voice-card">
        <CardHeader>
          <CardTitle className="text-xl">BI Voice IA</CardTitle>
        </CardHeader>
        <CardContent>
          <p data-testid="analytics-voice-total-campaigns">Campañas: {voiceStats.totalCampaigns ?? 0}</p>
          <p data-testid="analytics-voice-connection-rate">Conexión: {voiceStats.connectionRate ?? 0}%</p>
        </CardContent>
      </Card>

      <Card data-testid="analytics-overview-card">
        <CardHeader>
          <CardTitle className="text-xl">Overview Ejecutivo</CardTitle>
        </CardHeader>
        <CardContent>
          <p data-testid="analytics-overview-generated-at" className="text-sm text-muted-foreground">
            Actualizado: {overview?.generatedAt || "--"}
          </p>
          <ul className="mt-3 space-y-2 text-sm" data-testid="analytics-overview-insights">
            {(overview?.insights || []).map((insight) => (
              <li key={insight}>{insight}</li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </section>
  );
};

const Shell = () => (
  <div className="sandbox-app" data-testid="whatcem-sandbox-app">
    <aside className="sandbox-sidebar" data-testid="main-sidebar">
      <h1 className="text-2xl font-semibold" data-testid="app-title">
        WhatCEM Sandbox
      </h1>
      <p className="text-sm text-muted-foreground" data-testid="app-subtitle">
        Preview Sprints 1-2
      </p>
      <nav className="mt-6 flex flex-col gap-2" data-testid="main-navigation">
        <NavItem to="/" label="Inicio" testid="nav-home-link" />
        <NavItem to="/settings/lead-assignment" label="Lead Router IA" testid="nav-lead-router-link" />
        <NavItem to="/campaigns" label="Campañas IA" testid="nav-campaigns-link" />
        <NavItem to="/campaigns/voice" label="Voice AI" testid="nav-voice-link" />
        <NavItem to="/analytics" label="Analytics BI" testid="nav-analytics-link" />
      </nav>
    </aside>

    <main className="sandbox-main" data-testid="main-content">
      <div className="sandbox-badge" data-testid="sandbox-mocked-badge">
        Sandbox de validación interna (integraciones externas simuladas)
      </div>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/settings/lead-assignment" element={<LeadAssignmentPage />} />
        <Route path="/campaigns" element={<CampaignsPage />} />
        <Route path="/campaigns/voice" element={<VoiceCampaignsPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </main>
  </div>
);

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Shell />
      </BrowserRouter>
      <Toaster richColors position="top-right" />
    </div>
  );
}

export default App;
