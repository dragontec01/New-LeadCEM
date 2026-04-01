from datetime import datetime, timezone
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from pymongo import ReturnDocument
from starlette.middleware.cors import CORSMiddleware


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="WhatCEM Sandbox API")
api_router = APIRouter(prefix="/api")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def next_sequence(sequence_name: str) -> int:
    counter = await db.counters.find_one_and_update(
        {"name": sequence_name},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
        projection={"_id": 0, "value": 1},
    )
    return int(counter["value"])


def default_lead_rules() -> dict[str, Any]:
    return {
        "companyId": 1,
        "mode": "round_robin",
        "notifyOnAssign": True,
        "onlyAvailableAgents": False,
        "preferredChannelType": "whatsapp_twilio",
        "fallbackChannelType": "whatsapp_gupshup",
        "notificationTemplate": "Nuevo lead asignado: {{contact_name}}",
        "updatedAt": now_iso(),
    }


async def get_campaign_stats() -> dict[str, Any]:
    campaigns = await db.campaigns.find({}, {"_id": 0}).to_list(1000)
    total = len(campaigns)
    drafts = len([c for c in campaigns if c.get("status") == "draft"])
    running = len([c for c in campaigns if c.get("status") == "running"])
    sent = len([c for c in campaigns if c.get("status") == "sent"])
    return {
        "totalCampaigns": total,
        "draftCampaigns": drafts,
        "runningCampaigns": running,
        "sentCampaigns": sent,
        "deliveryRate": 94 if total else 0,
        "responseRate": 37 if total else 0,
    }


async def get_voice_stats() -> dict[str, Any]:
    voice_campaigns = await db.voice_campaigns.find({}, {"_id": 0}).to_list(1000)
    calls = await db.voice_calls.find({}, {"_id": 0}).to_list(1000)
    total = len(voice_campaigns)
    started = len([c for c in voice_campaigns if c.get("status") == "running"])
    completed_calls = len([c for c in calls if c.get("status") == "completed"])
    return {
        "totalCampaigns": total,
        "startedCampaigns": started,
        "totalCalls": len(calls),
        "completedCalls": completed_calls,
        "connectionRate": 61 if calls else 0,
    }


class StatusCheckCreate(BaseModel):
    client_name: str


class StatusCheck(BaseModel):
    id: str
    client_name: str
    timestamp: str


@api_router.get("/")
async def root() -> dict[str, str]:
    return {"message": "WhatCEM sandbox API online"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input_data: StatusCheckCreate) -> StatusCheck:
    status_obj = StatusCheck(
        id=str(await next_sequence("status_checks")),
        client_name=input_data.client_name,
        timestamp=now_iso(),
    )
    await db.status_checks.insert_one(status_obj.model_dump())
    return status_obj


@api_router.get("/status")
async def get_status_checks() -> list[dict[str, Any]]:
    return await db.status_checks.find({}, {"_id": 0}).to_list(1000)


@api_router.get("/lead-assignment/rules")
async def get_lead_assignment_rules() -> dict[str, Any]:
    rules = await db.lead_assignment_rules.find_one({"companyId": 1}, {"_id": 0})
    if not rules:
        rules = default_lead_rules()
        await db.lead_assignment_rules.insert_one(rules.copy())
    return rules


@api_router.post("/lead-assignment/rules")
async def save_lead_assignment_rules(payload: dict[str, Any]) -> dict[str, Any]:
    saved = {
        **default_lead_rules(),
        **payload,
        "companyId": 1,
        "updatedAt": now_iso(),
    }
    await db.lead_assignment_rules.replace_one({"companyId": 1}, saved.copy(), upsert=True)
    return saved


@api_router.get("/lead-assignment/events")
async def get_lead_assignment_events() -> list[dict[str, Any]]:
    return await db.lead_assignment_events.find({}, {"_id": 0}).sort("timestamp", -1).to_list(100)


@api_router.post("/lead-assignment/conversations/{conversation_id}/assign-next")
async def assign_next_lead(conversation_id: int) -> dict[str, Any]:
    assign_state = await db.lead_assignment_state.find_one({"companyId": 1}, {"_id": 0})
    next_index = ((assign_state or {}).get("nextIndex", 0) + 1) % 4
    agents = [
        {"id": 101, "name": "Sofía"},
        {"id": 102, "name": "Mateo"},
        {"id": 103, "name": "Valeria"},
        {"id": 104, "name": "Daniel"},
    ]
    assignee = agents[next_index]

    await db.lead_assignment_state.replace_one(
        {"companyId": 1},
        {"companyId": 1, "nextIndex": next_index, "updatedAt": now_iso()},
        upsert=True,
    )

    event = {
        "id": await next_sequence("lead_assignment_event"),
        "conversationId": conversation_id,
        "assignedToUserId": assignee["id"],
        "assignedToName": assignee["name"],
        "channelType": "whatsapp_gupshup",
        "notificationStatus": "delivered",
        "timestamp": now_iso(),
    }
    await db.lead_assignment_events.insert_one(event.copy())
    return event


@api_router.post("/lead-assignment/notifications/test")
async def test_assignment_notification(payload: dict[str, Any]) -> dict[str, Any]:
    phone = payload.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="phone es requerido")

    event = {
        "id": await next_sequence("lead_notification_event"),
        "phone": phone,
        "provider": payload.get("provider", "whatsapp_gupshup"),
        "message": payload.get("message", "Test de notificación de asignación"),
        "status": "sent",
        "timestamp": now_iso(),
    }
    await db.notification_events.insert_one(event.copy())
    return {"success": True, **event}


@api_router.get("/lead-assignment/metrics")
async def get_lead_assignment_metrics(days: int = Query(default=7)) -> dict[str, Any]:
    events = await db.lead_assignment_events.find({}, {"_id": 0}).to_list(1000)
    delivered = len([e for e in events if e.get("notificationStatus") == "delivered"])
    top_agents: dict[str, int] = {}
    for event in events:
        key = event.get("assignedToName", "Sin agente")
        top_agents[key] = top_agents.get(key, 0) + 1

    ranking = [
        {"agentName": agent, "assignments": count}
        for agent, count in sorted(top_agents.items(), key=lambda item: item[1], reverse=True)
    ]
    return {
        "days": days,
        "totalAssignments": len(events),
        "deliveryRate": round((delivered / len(events)) * 100, 2) if events else 0,
        "sentNotifications": delivered,
        "failedNotifications": max(len(events) - delivered, 0),
        "byProvider": [{"provider": "whatsapp_gupshup", "count": len(events)}],
        "topAgents": ranking[:5],
    }


@api_router.post("/lead-assignment/auto-assign-pending")
async def auto_assign_pending(payload: dict[str, Any]) -> dict[str, Any]:
    pending_ids = payload.get("pendingConversationIds") or [3201, 3202, 3203]
    assigned = []
    for conversation_id in pending_ids:
        assigned.append(await assign_next_lead(int(conversation_id)))
    return {"assignedCount": len(assigned), "assignments": assigned}


@api_router.post("/channel-connections")
async def create_channel_connection(payload: dict[str, Any]) -> dict[str, Any]:
    channel_type = payload.get("channelType")
    if not channel_type:
        raise HTTPException(status_code=400, detail="channelType es requerido")

    connection = {
        "id": await next_sequence("channel_connections"),
        "channelType": channel_type,
        "accountId": payload.get("accountId", "sandbox"),
        "accountName": payload.get("accountName", "Sandbox Connection"),
        "status": payload.get("status", "active"),
        "connectionData": payload.get("connectionData", {}),
        "createdAt": now_iso(),
    }
    await db.channel_connections.insert_one(connection.copy())
    return connection


@api_router.get("/voice-campaigns")
async def list_voice_campaigns() -> list[dict[str, Any]]:
    return await db.voice_campaigns.find({}, {"_id": 0}).sort("createdAt", -1).to_list(100)


@api_router.post("/voice-campaigns")
async def create_voice_campaign(payload: dict[str, Any]) -> dict[str, Any]:
    campaign = {
        "id": await next_sequence("voice_campaigns"),
        "name": payload.get("name", "Voice Campaign Sandbox"),
        "description": payload.get("description", ""),
        "prompt": payload.get("prompt", "Hola, te llamamos de WhatCEM"),
        "status": "draft",
        "twilioConnectionId": payload.get("twilioConnectionId"),
        "contactIds": payload.get("contactIds", []),
        "aiProvider": payload.get("aiProvider", "openai"),
        "aiModel": payload.get("aiModel", "gpt-4o-mini"),
        "createdAt": now_iso(),
    }
    await db.voice_campaigns.insert_one(campaign.copy())
    return campaign


@api_router.post("/voice-campaigns/{campaign_id}/start")
async def start_voice_campaign(campaign_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    campaign = await db.voice_campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Voice campaign no encontrada")

    await db.voice_campaigns.update_one(
        {"id": campaign_id}, {"$set": {"status": "running", "startedAt": now_iso()}}
    )
    simulated_calls = [
        {
            "id": await next_sequence("voice_calls"),
            "campaignId": campaign_id,
            "to": "+520000000001",
            "status": "completed",
            "durationSec": 68,
            "timestamp": now_iso(),
        }
    ]
    if payload.get("contactIds"):
        simulated_calls.append(
            {
                "id": await next_sequence("voice_calls"),
                "campaignId": campaign_id,
                "to": "+520000000002",
                "status": "completed",
                "durationSec": 54,
                "timestamp": now_iso(),
            }
        )

    if simulated_calls:
        await db.voice_calls.insert_many([call.copy() for call in simulated_calls])

    return {
        "campaignId": campaign_id,
        "status": "running",
        "callsQueued": len(simulated_calls),
        "message": "Campaña de voz iniciada en modo sandbox",
    }


@api_router.get("/voice-campaigns/{campaign_id}/calls")
async def get_voice_campaign_calls(campaign_id: int) -> list[dict[str, Any]]:
    return await db.voice_calls.find({"campaignId": campaign_id}, {"_id": 0}).to_list(200)


@api_router.post("/voice-campaigns/test-call")
async def run_voice_test_call(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "success": True,
        "to": payload.get("to", "+520000000000"),
        "provider": "twilio",
        "status": "queued",
        "timestamp": now_iso(),
    }


@api_router.get("/voice-campaigns/stats")
async def voice_campaigns_stats() -> dict[str, Any]:
    return await get_voice_stats()


@api_router.post("/campaigns/validate-whatsapp-content")
async def validate_whatsapp_content(payload: dict[str, Any]) -> dict[str, Any]:
    content = payload.get("content", "")
    variables = [piece for piece in content.split("{{") if "}}" in piece]
    return {
        "valid": bool(content.strip()),
        "issues": [] if content.strip() else ["El contenido está vacío"],
        "variableCount": len(variables),
    }


@api_router.post("/campaigns/ai-optimize-content")
async def ai_optimize_content(payload: dict[str, Any]) -> dict[str, Any]:
    base_text = payload.get("content", "")
    optimized = f"{base_text.strip()} ✅ Mensaje optimizado para WhatsApp con CTA claro."
    return {
        "optimizedContent": optimized.strip(),
        "rationale": "Se reforzó claridad, urgencia y cierre comercial.",
    }


@api_router.post("/campaigns/ai-generate-variations")
async def ai_generate_variations(payload: dict[str, Any]) -> dict[str, Any]:
    content = payload.get("content", "Hola {{1}}")
    variations = [
        {"label": "A", "content": f"{content} ¿Te gustaría más información hoy?"},
        {"label": "B", "content": f"{content} Tenemos cupos limitados para esta semana."},
    ]
    return {"variations": variations}


@api_router.post("/campaigns/ai-recommend-schedule")
async def ai_recommend_schedule(payload: dict[str, Any]) -> dict[str, Any]:
    timezone_name = payload.get("timezone", "America/Mexico_City")
    return {
        "recommendedAt": "2026-04-02T18:30:00",
        "timezone": timezone_name,
        "reason": "Horario con mejor tasa histórica de apertura y respuesta en sandbox.",
    }


@api_router.post("/campaigns")
async def create_campaign(payload: dict[str, Any]) -> dict[str, Any]:
    campaign = {
        "id": await next_sequence("campaigns"),
        "name": payload.get("name", "Campaña Sandbox"),
        "description": payload.get("description", ""),
        "content": payload.get("content", ""),
        "campaignType": payload.get("campaignType", "immediate"),
        "messageType": payload.get("messageType", "text"),
        "whatsappChannelType": payload.get("whatsappChannelType", "whatsapp_gupshup"),
        "channelIds": payload.get("channelIds", []),
        "segmentId": payload.get("segmentId"),
        "status": "draft",
        "createdAt": now_iso(),
    }
    await db.campaigns.insert_one(campaign.copy())
    return campaign


@api_router.post("/campaigns/{campaign_id}/start")
async def start_campaign(campaign_id: int) -> dict[str, Any]:
    existing = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    await db.campaigns.update_one(
        {"id": campaign_id}, {"$set": {"status": "running", "startedAt": now_iso()}}
    )
    return {"campaignId": campaign_id, "status": "running"}


@api_router.get("/campaigns/stats")
async def campaigns_stats() -> dict[str, Any]:
    return await get_campaign_stats()


@api_router.get("/analytics/overview")
async def analytics_overview() -> dict[str, Any]:
    campaign_stats = await get_campaign_stats()
    voice_stats = await get_voice_stats()
    return {
        "generatedAt": now_iso(),
        "whatsapp": campaign_stats,
        "voice": voice_stats,
        "insights": [
            "Las campañas con CTA corto convierten mejor.",
            "Voice IA tiene pico de conexión entre 17:00 y 19:00.",
        ],
    }


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client() -> None:
    client.close()