import os
from pathlib import Path

import pytest
import requests


# Lead-assignment + channel-connections public endpoint existence checks
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


def test_lead_assignment_rules_get_exists(api_client):
    endpoint = "/api/lead-assignment/rules"
    response = api_client.get(f"{BASE_URL}{endpoint}")
    assert_not_404(response, endpoint)


def test_lead_assignment_rules_post_exists(api_client):
    endpoint = "/api/lead-assignment/rules"
    payload = {
        "mode": "round_robin",
        "notifyOnAssign": True,
        "onlyAvailableAgents": False,
        "preferredChannelType": "whatsapp_twilio",
        "fallbackChannelType": "whatsapp_gupshup",
        "notificationTemplate": "TEST_Notification"
    }
    response = api_client.post(f"{BASE_URL}{endpoint}", json=payload)
    assert_not_404(response, endpoint)


def test_lead_assignment_events_get_exists(api_client):
    endpoint = "/api/lead-assignment/events"
    response = api_client.get(f"{BASE_URL}{endpoint}")
    assert_not_404(response, endpoint)


def test_assign_next_exists(api_client):
    endpoint = "/api/lead-assignment/conversations/1/assign-next"
    response = api_client.post(f"{BASE_URL}{endpoint}", json={})
    assert_not_404(response, endpoint)


def test_notifications_test_exists(api_client):
    endpoint = "/api/lead-assignment/notifications/test"
    response = api_client.post(f"{BASE_URL}{endpoint}", json={"phone": "+10000000000", "message": "TEST"})
    assert_not_404(response, endpoint)


def test_channel_connections_post_exists_for_gupshup(api_client):
    endpoint = "/api/channel-connections"
    payload = {
        "channelType": "whatsapp_gupshup",
        "accountId": "TEST_SOURCE",
        "accountName": "TEST_Gupshup",
        "connectionData": {
            "source": "TEST_SOURCE",
            "appName": "TEST_APP",
            "apiKey": "TEST_KEY",
            "endpointUrl": "https://api.gupshup.io/wa/api/v1/msg"
        },
        "status": "active"
    }
    response = api_client.post(f"{BASE_URL}{endpoint}", json=payload)
    assert_not_404(response, endpoint)
