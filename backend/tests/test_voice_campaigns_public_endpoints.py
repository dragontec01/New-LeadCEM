import os
from pathlib import Path

import pytest
import requests


# Voice-campaigns public endpoint existence checks
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


def test_voice_campaigns_get_exists(api_client):
    endpoint = "/api/voice-campaigns"
    response = api_client.get(f"{BASE_URL}{endpoint}")
    assert_not_404(response, endpoint)


def test_voice_campaigns_post_exists(api_client):
    endpoint = "/api/voice-campaigns"
    payload = {
        "name": "TEST_VoiceCampaign",
        "description": "TEST",
        "prompt": "Hola {{contact_name}}",
        "twilioConnectionId": 1,
        "contactIds": [1],
        "aiProvider": "openai",
        "aiModel": "gpt-4o-mini"
    }
    response = api_client.post(f"{BASE_URL}{endpoint}", json=payload)
    assert_not_404(response, endpoint)


def test_voice_campaigns_start_exists(api_client):
    endpoint = "/api/voice-campaigns/1/start"
    response = api_client.post(f"{BASE_URL}{endpoint}", json={"contactIds": [1], "twilioConnectionId": 1})
    assert_not_404(response, endpoint)


def test_voice_campaigns_calls_exists(api_client):
    endpoint = "/api/voice-campaigns/1/calls"
    response = api_client.get(f"{BASE_URL}{endpoint}")
    assert_not_404(response, endpoint)


def test_voice_campaigns_test_call_exists(api_client):
    endpoint = "/api/voice-campaigns/test-call"
    payload = {
        "twilioConnectionId": 1,
        "to": "+10000000000",
        "prompt": "TEST prompt"
    }
    response = api_client.post(f"{BASE_URL}{endpoint}", json=payload)
    assert_not_404(response, endpoint)
