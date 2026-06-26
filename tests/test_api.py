from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.testclient import TestClient

from src.api.main import app


@pytest.fixture
def mock_orchestrator():
    mock = MagicMock()
    mock.get_status.return_value = {
        "status": "operational",
        "budget": {"total": 40.0, "used": 0.0, "remaining": 40.0},
        "agents": {
            "JING-MASTER": "available",
            "JING-EYE": "available",
            "JING-SCRIBE": "available",
            "JING-KIT": "available",
            "JING-VOICE": "available",
            "JING-FOREMAN": "available",
            "JING-STEWARD": "available",
        },
        "models": {
            "qwen-max": "qwen-max",
            "qwen-vl-max": "qwen-vl-max",
            "qwen-plus": "qwen-plus",
            "qwen-audio": "qwen-audio",
        },
    }
    return mock


@pytest.fixture
def mock_qwen_for_api():
    mock = MagicMock()
    mock.health_check = AsyncMock(return_value=True)
    mock.get_cost_summary.return_value = {
        "total_cost": 0.0,
        "remaining_budget": 40.0,
        "call_count": 0,
        "calls_by_model": {},
    }
    mock.get_remaining_budget.return_value = 40.0
    return mock


class TestHealthEndpoint:
    @patch("src.api.main.get_orchestrator")
    @patch("src.api.routes.health.get_orchestrator")
    @patch("src.api.routes.health.get_qwen_client")
    def test_health_returns_200(
        self,
        mock_health_qwen,
        mock_health_orch,
        mock_main_orch,
        mock_orchestrator,
        mock_qwen_for_api,
    ):
        mock_health_orch.return_value = mock_orchestrator
        mock_main_orch.return_value = mock_orchestrator
        mock_health_qwen.return_value = mock_qwen_for_api

        with TestClient(app) as client:
            response = client.get("/health")

        assert response.status_code == 200

    @patch("src.api.main.get_orchestrator")
    @patch("src.api.routes.health.get_orchestrator")
    @patch("src.api.routes.health.get_qwen_client")
    def test_health_returns_operational(
        self,
        mock_health_qwen,
        mock_health_orch,
        mock_main_orch,
        mock_orchestrator,
        mock_qwen_for_api,
    ):
        mock_health_orch.return_value = mock_orchestrator
        mock_main_orch.return_value = mock_orchestrator
        mock_health_qwen.return_value = mock_qwen_for_api

        with TestClient(app) as client:
            response = client.get("/health")
            data = response.json()

        assert data["status"] == "operational"
        assert data["qwen_api"] is True
        assert "version" in data
        assert "budget" in data
        assert "agents" in data

    @patch("src.api.main.get_orchestrator")
    @patch("src.api.routes.health.get_orchestrator")
    @patch("src.api.routes.health.get_qwen_client")
    def test_health_structure(
        self,
        mock_health_qwen,
        mock_health_orch,
        mock_main_orch,
        mock_orchestrator,
        mock_qwen_for_api,
    ):
        mock_health_orch.return_value = mock_orchestrator
        mock_main_orch.return_value = mock_orchestrator
        mock_health_qwen.return_value = mock_qwen_for_api

        with TestClient(app) as client:
            response = client.get("/health")
            data = response.json()

        assert set(data.keys()) == {"status", "version", "budget", "agents", "qwen_api"}
        assert data["budget"]["remaining"] == 40.0
        assert "JING-MASTER" in data["agents"]


class TestStatusEndpoint:
    @patch("src.api.main.get_orchestrator")
    @patch("src.api.routes.health.get_orchestrator")
    @patch("src.api.routes.health.get_qwen_client")
    def test_status_returns_200(
        self,
        mock_health_qwen,
        mock_health_orch,
        mock_main_orch,
        mock_orchestrator,
        mock_qwen_for_api,
    ):
        mock_health_orch.return_value = mock_orchestrator
        mock_main_orch.return_value = mock_orchestrator
        mock_health_qwen.return_value = mock_qwen_for_api

        with TestClient(app) as client:
            response = client.get("/status")

        assert response.status_code == 200

    @patch("src.api.main.get_orchestrator")
    @patch("src.api.routes.health.get_orchestrator")
    @patch("src.api.routes.health.get_qwen_client")
    def test_status_returns_operational(
        self,
        mock_health_qwen,
        mock_health_orch,
        mock_main_orch,
        mock_orchestrator,
        mock_qwen_for_api,
    ):
        mock_health_orch.return_value = mock_orchestrator
        mock_main_orch.return_value = mock_orchestrator
        mock_health_qwen.return_value = mock_qwen_for_api

        with TestClient(app) as client:
            response = client.get("/status")
            data = response.json()

        assert data["status"] == "operational"
        assert "budget" in data
        assert "agents" in data
        assert "models" in data


class TestCORSHeaders:
    @patch("src.api.main.get_orchestrator")
    @patch("src.api.routes.health.get_orchestrator")
    @patch("src.api.routes.health.get_qwen_client")
    def test_cors_headers_present(
        self,
        mock_health_qwen,
        mock_health_orch,
        mock_main_orch,
        mock_orchestrator,
        mock_qwen_for_api,
    ):
        mock_health_orch.return_value = mock_orchestrator
        mock_main_orch.return_value = mock_orchestrator
        mock_health_qwen.return_value = mock_qwen_for_api

        with TestClient(app) as client:
            response = client.get(
                "/health",
                headers={"Origin": "http://localhost"},
            )

        # CORSMiddleware with allow_origins=["*"] echoes the Origin header
        assert response.headers.get("access-control-allow-origin") == "http://localhost"

    @patch("src.api.main.get_orchestrator")
    @patch("src.api.routes.health.get_orchestrator")
    @patch("src.api.routes.health.get_qwen_client")
    def test_cors_allows_all_methods(
        self,
        mock_health_qwen,
        mock_health_orch,
        mock_main_orch,
        mock_orchestrator,
        mock_qwen_for_api,
    ):
        mock_health_orch.return_value = mock_orchestrator
        mock_main_orch.return_value = mock_orchestrator
        mock_health_qwen.return_value = mock_qwen_for_api

        with TestClient(app) as client:
            response = client.options(
                "/health",
                headers={"Origin": "http://example.com", "Access-Control-Request-Method": "GET"},
            )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://example.com"
        assert "access-control-allow-methods" in response.headers

    @patch("src.api.main.get_orchestrator")
    @patch("src.api.routes.health.get_orchestrator")
    @patch("src.api.routes.health.get_qwen_client")
    def test_cors_allows_all_origins(
        self,
        mock_health_qwen,
        mock_health_orch,
        mock_main_orch,
        mock_orchestrator,
        mock_qwen_for_api,
    ):
        mock_health_orch.return_value = mock_orchestrator
        mock_main_orch.return_value = mock_orchestrator
        mock_health_qwen.return_value = mock_qwen_for_api

        with TestClient(app) as client:
            response = client.get(
                "/health",
                headers={"Origin": "https://evil.com"},
            )

        # With allow_origins=["*"], the request origin is echoed back
        assert response.headers.get("access-control-allow-origin") == "https://evil.com"
