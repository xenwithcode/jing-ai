import json
from unittest.mock import patch

import pytest

from src.services.memory import MemoryService


@pytest.fixture(autouse=True)
def reset_memory_singleton():
    MemoryService._instance = None


@pytest.fixture
def memory_service(tmp_path):
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    clients_file = memory_dir / "clients.json"
    jobs_file = memory_dir / "jobs.json"

    with patch("src.services.memory.MEMORY_DIR", memory_dir):
        with patch("src.services.memory.CLIENTS_FILE", clients_file):
            with patch("src.services.memory.JOBS_FILE", jobs_file):
                service = MemoryService()
                service._test_clients = clients_file
                service._test_jobs = jobs_file
                yield service


class TestMemoryServiceSingleton:
    def test_singleton_pattern(self):
        MemoryService._instance = None
        s1 = MemoryService()
        s2 = MemoryService()
        assert s1 is s2

    def test_singleton_across_reset(self):
        MemoryService._instance = None
        s1 = MemoryService()
        MemoryService._instance = None
        s2 = MemoryService()
        assert s1 is not s2


class TestGetOrCreateClient:
    def test_creates_new_client(self, memory_service):
        client = memory_service.get_or_create_client("Alice", phone="555-0101")
        assert client["name"] == "Alice"
        assert client["phone"] == "555-0101"
        assert client["total_jobs"] == 0
        assert client["total_spent"] == 0.0
        assert client["id"].startswith("client_")

    def test_returns_existing_client(self, memory_service):
        first = memory_service.get_or_create_client("Bob")
        second = memory_service.get_or_create_client("Bob")
        assert first == second
        assert first["name"] == "Bob"

    def test_case_insensitive_lookup(self, memory_service):
        memory_service.get_or_create_client("Charlie")
        found = memory_service.get_or_create_client("charlie")
        assert found["name"] == "Charlie"

    def test_saves_to_file(self, memory_service):
        memory_service.get_or_create_client("Diana")
        data = json.loads(memory_service._test_clients.read_text())
        assert any(c["name"] == "Diana" for c in data)


class TestSaveJob:
    def test_saves_job_to_file(self, memory_service):
        memory_service.save_job(
            {
                "client_name": "Eve",
                "diagnosis": "Leaky faucet",
                "final_cost": 150.00,
                "profit": 75.00,
                "grade": "A",
                "duration_minutes": 45,
            }
        )
        jobs = json.loads(memory_service._test_jobs.read_text())
        assert len(jobs) == 1
        assert jobs[0]["client_name"] == "Eve"

    def test_save_job_updates_client_stats(self, memory_service):
        memory_service.get_or_create_client("Frank")
        memory_service.save_job(
            {
                "client_name": "Frank",
                "final_cost": 200.00,
                "diagnosis": "Wiring repair",
                "profit": 80.00,
                "grade": "B+",
                "duration_minutes": 120,
            }
        )
        client = memory_service.get_or_create_client("Frank")
        assert client["total_jobs"] == 1
        assert client["total_spent"] == 200.00

    def test_save_job_multiple_jobs_accumulates(self, memory_service):
        memory_service.get_or_create_client("Grace")
        for i in range(3):
            memory_service.save_job(
                {
                    "client_name": "Grace",
                    "final_cost": 100.00,
                    "diagnosis": f"Job {i}",
                    "profit": 50.00,
                    "grade": "B",
                    "duration_minutes": 30,
                }
            )
        client = memory_service.get_or_create_client("Grace")
        assert client["total_jobs"] == 3
        assert client["total_spent"] == 300.00

    def test_save_job_defaults(self, memory_service):
        memory_service.save_job({"client_name": "Heidi"})
        jobs = json.loads(memory_service._test_jobs.read_text())
        assert jobs[0]["diagnosis"] == ""
        assert jobs[0]["final_cost"] == 0.0
        assert jobs[0]["grade"] == "C"
        assert jobs[0]["duration_minutes"] == 0


class TestGetClientHistory:
    def test_history_for_existing_client(self, memory_service):
        memory_service.get_or_create_client("Ivan")
        memory_service.save_job(
            {
                "client_name": "Ivan",
                "final_cost": 300.00,
                "diagnosis": "HVAC repair",
                "profit": 150.00,
                "grade": "A",
                "duration_minutes": 90,
            }
        )
        history = memory_service.get_client_history("Ivan")
        assert history["exists"] is True
        assert history["total_jobs"] == 1
        assert history["total_spent"] == 300.00
        assert len(history["past_jobs"]) == 1

    def test_history_for_nonexistent_client(self, memory_service):
        history = memory_service.get_client_history("NonExistent")
        assert history["exists"] is False

    def test_history_case_insensitive(self, memory_service):
        memory_service.get_or_create_client("Judy")
        memory_service.save_job(
            {
                "client_name": "Judy",
                "final_cost": 100.00,
                "diagnosis": "Test",
                "profit": 50.00,
                "grade": "B",
                "duration_minutes": 30,
            }
        )
        history = memory_service.get_client_history("judy")
        assert history["exists"] is True

    def test_history_returns_last_5_jobs(self, memory_service):
        memory_service.get_or_create_client("Karl")
        for i in range(10):
            memory_service.save_job(
                {
                    "client_name": "Karl",
                    "final_cost": float(i),
                    "diagnosis": f"Job {i}",
                    "profit": float(i * 0.5),
                    "grade": "B",
                    "duration_minutes": 30,
                }
            )
        history = memory_service.get_client_history("Karl")
        assert len(history["past_jobs"]) <= 5


class TestGetContextForSteward:
    def test_new_client_context(self, memory_service):
        context = memory_service.get_context_for_steward("NewClient", "plumber")
        assert "new client" in context.lower()
        assert "no historical data" in context.lower()

    def test_returning_client_context(self, memory_service):
        memory_service.get_or_create_client("Leo")
        memory_service.save_job(
            {
                "client_name": "Leo",
                "final_cost": 400.00,
                "diagnosis": "Pipe repair",
                "profit": 200.00,
                "grade": "A",
                "duration_minutes": 60,
            }
        )
        context = memory_service.get_context_for_steward("Leo", "plumber")
        assert "Leo" in context
        assert "1 jobs" in context
        assert "$400" in context

    def test_context_includes_avg_profit(self, memory_service):
        memory_service.get_or_create_client("Maria")
        memory_service.save_job(
            {
                "client_name": "Maria",
                "final_cost": 200.00,
                "diagnosis": "Fix sink",
                "profit": 100.00,
                "grade": "A",
                "duration_minutes": 45,
            }
        )
        context = memory_service.get_context_for_steward("Maria", "plumber")
        assert "average profit" in context.lower()

    def test_context_includes_payment_preference(self, memory_service):
        memory_service.get_or_create_client("Nathan")
        context = memory_service.get_context_for_steward("Nathan", "general")
        assert "pay via" in context.lower()
