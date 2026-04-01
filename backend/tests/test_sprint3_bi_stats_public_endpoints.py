import os
from pathlib import Path

import pytest
import requests


# Sprint 3 BI analytics public endpoint availability checks
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


def test_campaigns_stats_endpoint_is_routed(api_client):
    endpoint = "/api/campaigns/stats"
    response = api_client.get(f"{BASE_URL}{endpoint}")
    assert_not_404(response, endpoint)


def test_voice_campaigns_stats_endpoint_is_routed(api_client):
    endpoint = "/api/voice-campaigns/stats"
    response = api_client.get(f"{BASE_URL}{endpoint}")
    assert_not_404(response, endpoint)


def test_analytics_overview_endpoint_is_routed_for_regression(api_client):
    endpoint = "/api/analytics/overview"
    response = api_client.get(f"{BASE_URL}{endpoint}")
    assert_not_404(response, endpoint)
