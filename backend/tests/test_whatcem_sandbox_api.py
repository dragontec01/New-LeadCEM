"""
WhatCEM Sandbox API Tests - Sprint 1, 2, 3 Endpoints
Tests Lead Assignment, Campaign AI, Voice Campaigns, and Analytics BI endpoints
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndRoot:
    """Basic API health checks"""
    
    def test_api_root_returns_online_message(self):
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "WhatCEM sandbox API online" in data["message"]


class TestLeadAssignmentEndpoints:
    """Sprint 1: Lead Assignment / Lead Router IA endpoints"""
    
    def test_get_lead_assignment_rules(self):
        response = requests.get(f"{BASE_URL}/api/lead-assignment/rules")
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data
        assert "companyId" in data
        assert "notifyOnAssign" in data
        assert "preferredChannelType" in data
        assert "fallbackChannelType" in data
    
    def test_post_lead_assignment_rules(self):
        payload = {
            "mode": "round_robin",
            "notifyOnAssign": True,
            "fallbackChannelType": "whatsapp_gupshup"
        }
        response = requests.post(f"{BASE_URL}/api/lead-assignment/rules", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "round_robin"
        assert data["notifyOnAssign"] == True
        
        # Verify persistence with GET
        get_response = requests.get(f"{BASE_URL}/api/lead-assignment/rules")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["mode"] == "round_robin"
    
    def test_get_lead_assignment_events(self):
        response = requests.get(f"{BASE_URL}/api/lead-assignment/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_post_notifications_test(self):
        payload = {
            "phone": "+5215512345678",
            "message": "Test notification from pytest"
        }
        response = requests.post(f"{BASE_URL}/api/lead-assignment/notifications/test", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "phone" in data
        assert data["status"] == "sent"
    
    def test_post_notifications_test_requires_phone(self):
        payload = {"message": "Test without phone"}
        response = requests.post(f"{BASE_URL}/api/lead-assignment/notifications/test", json=payload)
        assert response.status_code == 400
    
    def test_post_auto_assign_pending(self):
        payload = {"pendingConversationIds": [9001, 9002]}
        response = requests.post(f"{BASE_URL}/api/lead-assignment/auto-assign-pending", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "assignedCount" in data
        assert "assignments" in data
        assert data["assignedCount"] == 2
    
    def test_get_lead_assignment_metrics(self):
        response = requests.get(f"{BASE_URL}/api/lead-assignment/metrics?days=30")
        assert response.status_code == 200
        data = response.json()
        assert "days" in data
        assert data["days"] == 30
        assert "totalAssignments" in data
        assert "deliveryRate" in data
        assert "sentNotifications" in data
        assert "failedNotifications" in data
        assert "byProvider" in data
        assert "topAgents" in data


class TestCampaignAIEndpoints:
    """Sprint 2: Campaign AI WhatsApp endpoints"""
    
    def test_post_validate_whatsapp_content(self):
        payload = {"content": "Hola {{1}}, tenemos una oferta para ti"}
        response = requests.post(f"{BASE_URL}/api/campaigns/validate-whatsapp-content", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert data["valid"] == True
        assert "variableCount" in data
        assert data["variableCount"] >= 1
    
    def test_post_validate_whatsapp_content_empty(self):
        payload = {"content": ""}
        response = requests.post(f"{BASE_URL}/api/campaigns/validate-whatsapp-content", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == False
        assert len(data["issues"]) > 0
    
    def test_post_ai_optimize_content(self):
        payload = {
            "content": "Hola {{1}}, tenemos una propuesta",
            "whatsappChannelType": "whatsapp_gupshup",
            "messageType": "text",
            "objective": "Más respuestas",
            "tone": "profesional-cercano"
        }
        response = requests.post(f"{BASE_URL}/api/campaigns/ai-optimize-content", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "optimizedContent" in data
        assert "rationale" in data
        assert len(data["optimizedContent"]) > len(payload["content"])
    
    def test_post_ai_generate_variations(self):
        payload = {
            "content": "Hola {{1}}, tenemos una oferta",
            "whatsappChannelType": "whatsapp_gupshup",
            "messageType": "text"
        }
        response = requests.post(f"{BASE_URL}/api/campaigns/ai-generate-variations", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "variations" in data
        assert len(data["variations"]) >= 2
        for variation in data["variations"]:
            assert "label" in variation
            assert "content" in variation
    
    def test_post_ai_recommend_schedule(self):
        payload = {
            "timezone": "America/Mexico_City",
            "audienceSize": 1200,
            "objective": "conversiones"
        }
        response = requests.post(f"{BASE_URL}/api/campaigns/ai-recommend-schedule", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "recommendedAt" in data
        assert "timezone" in data
        assert "reason" in data
    
    def test_post_create_campaign(self):
        payload = {
            "name": "TEST_Campaign_Pytest",
            "description": "Test campaign from pytest",
            "content": "Hola {{1}}, mensaje de prueba",
            "whatsappChannelType": "whatsapp_gupshup",
            "campaignType": "immediate",
            "messageType": "text",
            "channelIds": [1],
            "segmentId": 1
        }
        response = requests.post(f"{BASE_URL}/api/campaigns", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "TEST_Campaign_Pytest"
        assert data["status"] == "draft"
        
        # Store campaign ID for start test
        return data["id"]
    
    def test_post_start_campaign(self):
        # First create a campaign
        create_payload = {
            "name": "TEST_Campaign_Start_Pytest",
            "content": "Test content",
            "whatsappChannelType": "whatsapp_gupshup"
        }
        create_response = requests.post(f"{BASE_URL}/api/campaigns", json=create_payload)
        assert create_response.status_code == 200
        campaign_id = create_response.json()["id"]
        
        # Start the campaign
        start_response = requests.post(f"{BASE_URL}/api/campaigns/{campaign_id}/start", json={})
        assert start_response.status_code == 200
        data = start_response.json()
        assert data["campaignId"] == campaign_id
        assert data["status"] == "running"
    
    def test_post_start_campaign_not_found(self):
        response = requests.post(f"{BASE_URL}/api/campaigns/99999/start", json={})
        assert response.status_code == 404
    
    def test_get_campaigns_stats(self):
        response = requests.get(f"{BASE_URL}/api/campaigns/stats")
        assert response.status_code == 200
        data = response.json()
        assert "totalCampaigns" in data
        assert "draftCampaigns" in data
        assert "runningCampaigns" in data
        assert "sentCampaigns" in data
        assert "deliveryRate" in data
        assert "responseRate" in data


class TestVoiceCampaignEndpoints:
    """Sprint 2: Voice AI Campaign endpoints"""
    
    def test_get_voice_campaigns(self):
        response = requests.get(f"{BASE_URL}/api/voice-campaigns")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_post_create_voice_campaign(self):
        payload = {
            "name": "TEST_Voice_Campaign_Pytest",
            "description": "Test voice campaign",
            "prompt": "Hola {{contact_name}}, te llamamos de WhatCEM",
            "twilioConnectionId": 1,
            "contactIds": [1, 2],
            "aiProvider": "openai",
            "aiModel": "gpt-4o-mini"
        }
        response = requests.post(f"{BASE_URL}/api/voice-campaigns", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "TEST_Voice_Campaign_Pytest"
        assert data["status"] == "draft"
        assert data["aiProvider"] == "openai"
    
    def test_post_start_voice_campaign(self):
        # First create a voice campaign
        create_payload = {
            "name": "TEST_Voice_Start_Pytest",
            "prompt": "Test prompt"
        }
        create_response = requests.post(f"{BASE_URL}/api/voice-campaigns", json=create_payload)
        assert create_response.status_code == 200
        campaign_id = create_response.json()["id"]
        
        # Start the voice campaign
        start_payload = {"contactIds": [1], "twilioConnectionId": 1}
        start_response = requests.post(f"{BASE_URL}/api/voice-campaigns/{campaign_id}/start", json=start_payload)
        assert start_response.status_code == 200
        data = start_response.json()
        assert data["campaignId"] == campaign_id
        assert data["status"] == "running"
        assert "callsQueued" in data
    
    def test_post_start_voice_campaign_not_found(self):
        response = requests.post(f"{BASE_URL}/api/voice-campaigns/99999/start", json={})
        assert response.status_code == 404
    
    def test_get_voice_campaign_calls(self):
        # First create and start a voice campaign to generate calls
        create_payload = {"name": "TEST_Voice_Calls_Pytest", "prompt": "Test"}
        create_response = requests.post(f"{BASE_URL}/api/voice-campaigns", json=create_payload)
        campaign_id = create_response.json()["id"]
        
        # Start to generate simulated calls
        requests.post(f"{BASE_URL}/api/voice-campaigns/{campaign_id}/start", json={"contactIds": [1]})
        
        # Get calls
        response = requests.get(f"{BASE_URL}/api/voice-campaigns/{campaign_id}/calls")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_post_voice_test_call(self):
        payload = {"to": "+520000000000"}
        response = requests.post(f"{BASE_URL}/api/voice-campaigns/test-call", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["provider"] == "twilio"
        assert data["status"] == "queued"
    
    def test_get_voice_campaigns_stats(self):
        response = requests.get(f"{BASE_URL}/api/voice-campaigns/stats")
        assert response.status_code == 200
        data = response.json()
        assert "totalCampaigns" in data
        assert "startedCampaigns" in data
        assert "totalCalls" in data
        assert "completedCalls" in data
        assert "connectionRate" in data


class TestAnalyticsBIEndpoints:
    """Sprint 3 Phase 1: Analytics BI endpoints"""
    
    def test_get_analytics_overview(self):
        response = requests.get(f"{BASE_URL}/api/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        assert "generatedAt" in data
        assert "whatsapp" in data
        assert "voice" in data
        assert "insights" in data
        
        # Validate whatsapp stats structure
        assert "totalCampaigns" in data["whatsapp"]
        assert "deliveryRate" in data["whatsapp"]
        
        # Validate voice stats structure
        assert "totalCampaigns" in data["voice"]
        assert "connectionRate" in data["voice"]
        
        # Validate insights
        assert isinstance(data["insights"], list)


class TestChannelConnections:
    """Channel connection endpoints"""
    
    def test_post_create_channel_connection(self):
        payload = {
            "channelType": "whatsapp_gupshup",
            "accountId": "test_sandbox",
            "accountName": "Test Sandbox Connection",
            "status": "active",
            "connectionData": {"apiKey": "test_key"}
        }
        response = requests.post(f"{BASE_URL}/api/channel-connections", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["channelType"] == "whatsapp_gupshup"
        assert data["status"] == "active"
    
    def test_post_create_channel_connection_requires_type(self):
        payload = {"accountId": "test"}
        response = requests.post(f"{BASE_URL}/api/channel-connections", json=payload)
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
