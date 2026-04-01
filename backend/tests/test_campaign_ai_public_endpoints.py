import os
from pathlib import Path

import pytest
import requests


# Campaign Builder AI + regression public endpoint existence checks
def _get_base_url() -> str:
    env_url = os.environ.get("REACT_APP_BACKEND_URL")
    if env_url:
        return env_url.rstrip("/")

    env_file = Path("/app/frontend/.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip().strip('"').rstrip("/")

    pytest.skip("REACT_APP_BACKEND_URL not found in env or /app/frontend/.env")


BASE_URL = _get_base_url()


@pytest.fixture
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def assert_not_404(response: requests.Response, endpoint: str):
    assert response.status_code != 404, f"Endpoint missing/unrouted on public URL: {endpoint}"


# AI validation/optimization feature endpoints
def test_validate_whatsapp_content_alias_exists(api_client):
    endpoint = "/api/campaigns/validate-whatsapp-content"
    response = api_client.post(f"{BASE_URL}{endpoint}", json={"content": "Hola {{1}}"})
    assert_not_404(response, endpoint)


def test_ai_optimize_content_exists(api_client):
    endpoint = "/api/campaigns/ai-optimize-content"
    payload = {
        "content": "Urgent limited time offer buy now",
        "whatsappChannelType": "whatsapp_unofficial",
        "messageType": "text",
        "objective": "Más respuestas",
        "tone": "profesional-cercano"
    }
    response = api_client.post(f"{BASE_URL}{endpoint}", json=payload)
    assert_not_404(response, endpoint)


def test_ai_generate_variations_exists(api_client):
    endpoint = "/api/campaigns/ai-generate-variations"
    payload = {
        "content": "Hola {{1}}, queremos compartirte novedades",
        "whatsappChannelType": "whatsapp_unofficial",
        "messageType": "text"
    }
    response = api_client.post(f"{BASE_URL}{endpoint}", json=payload)
    assert_not_404(response, endpoint)


def test_ai_recommend_schedule_exists(api_client):
    endpoint = "/api/campaigns/ai-recommend-schedule"
    payload = {
        "timezone": "America/Mexico_City",
        "audienceSize": 1200,
        "objective": "conversiones"
    }
    response = api_client.post(f"{BASE_URL}{endpoint}", json=payload)
    assert_not_404(response, endpoint)


# Regression flow endpoint availability (save draft + launch)
def test_create_campaign_exists_for_save_draft(api_client):
    endpoint = "/api/campaigns"
    payload = {
        "name": "TEST_Campaign_AI_Regression",
        "description": "TEST",
        "content": "Hola {{1}}",
        "whatsappChannelType": "whatsapp_unofficial",
        "campaignType": "immediate",
        "messageType": "text",
        "channelIds": [1],
        "segmentId": 1
    }
    response = api_client.post(f"{BASE_URL}{endpoint}", json=payload)
    assert_not_404(response, endpoint)


def test_start_campaign_exists_for_launch(api_client):
    endpoint = "/api/campaigns/1/start"
    response = api_client.post(f"{BASE_URL}{endpoint}", json={})
    assert_not_404(response, endpoint)
