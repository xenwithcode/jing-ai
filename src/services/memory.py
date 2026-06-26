"""
JING Memory Service - Persistent Memory for the Agent Society.

This service allows JING agents to remember past interactions,
client preferences, and historical job data. It transforms JING
from a stateless tool into a learning system.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.utils.logger import get_logger

logger = get_logger(__name__)

MEMORY_DIR = Path("data/memory")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

CLIENTS_FILE = MEMORY_DIR / "clients.json"
JOBS_FILE = MEMORY_DIR / "jobs.json"


class MemoryService:
    """Singleton service to manage persistent memory."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryService, cls).__new__(cls)
            cls._instance._initialize_files()
        return cls._instance

    def _initialize_files(self):
        if not CLIENTS_FILE.exists():
            CLIENTS_FILE.write_text("[]")
        if not JOBS_FILE.exists():
            JOBS_FILE.write_text("[]")

    def _read_json(self, file_path: Path) -> List[Dict]:
        try:
            return json.loads(file_path.read_text())
        except json.JSONDecodeError:
            return []

    def _write_json(self, file_path: Path, data: List[Dict]):
        file_path.write_text(json.dumps(data, indent=2, default=str))

    # ═══════════════════════════════════════════════════════════
    # CLIENT MEMORY
    # ═══════════════════════════════════════════════════════════

    def get_or_create_client(self, client_name: str, phone: Optional[str] = None) -> Dict:
        clients = self._read_json(CLIENTS_FILE)
        for client in clients:
            if client["name"].lower() == client_name.lower():
                return client

        new_client = {
            "id": f"client_{len(clients) + 1:04d}",
            "name": client_name,
            "phone": phone or "",
            "email": "",
            "address": "",
            "created_at": datetime.now().isoformat(),
            "total_jobs": 0,
            "total_spent": 0.0,
            "preferred_payment": "cash",
            "notes": [],
        }
        clients.append(new_client)
        self._write_json(CLIENTS_FILE, clients)
        logger.info(f"Created new client memory: {client_name}")
        return new_client

    def get_client_history(self, client_name: str) -> Dict[str, Any]:
        """Get all historical data for a client."""
        clients = self._read_json(CLIENTS_FILE)
        jobs = self._read_json(JOBS_FILE)

        client = None
        for c in clients:
            if c["name"].lower() == client_name.lower():
                client = c
                break

        if not client:
            return {"exists": False}

        client_jobs = [j for j in jobs if j.get("client_name", "").lower() == client_name.lower()]

        return {
            "exists": True,
            "client": client,
            "past_jobs": client_jobs[-5:],
            "total_jobs": client["total_jobs"],
            "total_spent": client["total_spent"],
            "preferred_payment": client.get("preferred_payment", "cash"),
        }

    def update_client_info(self, client_name: str, **kwargs) -> Optional[Dict]:
        clients = self._read_json(CLIENTS_FILE)
        for client in clients:
            if client["name"].lower() == client_name.lower():
                for key in ("phone", "email", "address"):
                    if key in kwargs:
                        client[key] = kwargs[key]
                self._write_json(CLIENTS_FILE, clients)
                return client
        return None

    # ══════════════════════════════════════════════════════════
    # JOB MEMORY
    # ═══════════════════════════════════════════════════════════

    def save_job(self, job_data: Dict[str, Any]):
        """Save a completed job to memory."""
        jobs = self._read_json(JOBS_FILE)

        job_record = {
            "job_id": job_data.get("job_id", f"job_{len(jobs) + 1:04d}"),
            "client_name": job_data.get("client_name", "Unknown"),
            "client_phone": job_data.get("client_phone", ""),
            "client_email": job_data.get("client_email", ""),
            "client_address": job_data.get("client_address", ""),
            "date": datetime.now().isoformat(),
            "diagnosis": job_data.get("diagnosis", ""),
            "description": job_data.get("description", ""),
            "status": job_data.get("status", "completed"),
            "trade": job_data.get("trade", "general"),
            "final_cost": job_data.get("final_cost", 0.0),
            "parts_cost": job_data.get("parts_cost", 0.0),
            "labor_cost": job_data.get("labor_cost", 0.0),
            "profit": job_data.get("profit", 0.0),
            "grade": job_data.get("grade", "C"),
            "duration_minutes": job_data.get("duration_minutes", 0),
        }

        jobs.append(job_record)
        self._write_json(JOBS_FILE, jobs)

        clients = self._read_json(CLIENTS_FILE)
        for client in clients:
            if client["name"].lower() == job_data.get("client_name", "").lower():
                client["total_jobs"] += 1
                client["total_spent"] += job_data.get("final_cost", 0.0)
                if job_data.get("client_phone"):
                    client["phone"] = job_data["client_phone"]
                if job_data.get("client_email"):
                    client["email"] = job_data["client_email"]
                if job_data.get("client_address"):
                    client["address"] = job_data["client_address"]
                break
        self._write_json(CLIENTS_FILE, clients)

        logger.info(f"Saved job memory: {job_record['job_id']}")

    def update_job_status(self, job_id: str, status: str) -> Optional[Dict]:
        jobs = self._read_json(JOBS_FILE)
        for job in jobs:
            if job["job_id"] == job_id:
                job["status"] = status
                self._write_json(JOBS_FILE, jobs)
                return job
        return None

    def get_all_jobs(self, trade: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        jobs = self._read_json(JOBS_FILE)
        if trade:
            jobs = [j for j in jobs if j.get("trade", "").lower() == trade.lower()]
        if status:
            jobs = [j for j in jobs if j.get("status", "").lower() == status.lower()]
        jobs.sort(key=lambda j: j.get("date", ""), reverse=True)
        return jobs

    def get_dashboard_stats(self, trade: Optional[str] = None) -> Dict[str, Any]:
        jobs = self._read_json(JOBS_FILE)
        clients = self._read_json(CLIENTS_FILE)

        if trade:
            jobs = [j for j in jobs if j.get("trade", "").lower() == trade.lower()]

        total_jobs = len(jobs)
        completed = [j for j in jobs if j.get("status") == "completed"]
        in_progress = [j for j in jobs if j.get("status") == "in-progress"]
        pending = [j for j in jobs if j.get("status") == "pending"]

        total_revenue = sum(j.get("final_cost", 0) for j in completed)
        total_profit = sum(j.get("profit", 0) for j in completed)
        total_parts = sum(j.get("parts_cost", 0) for j in completed)
        total_labor = sum(j.get("labor_cost", 0) for j in completed)
        avg_profit = total_profit / len(completed) if completed else 0
        avg_grade = (
            sum(ord(j.get("grade", "C")) for j in completed) / len(completed)
            if completed
            else ord("C")
        )
        avg_duration = (
            sum(j.get("duration_minutes", 0) for j in completed) / len(completed)
            if completed
            else 0
        )

        # Monthly revenue for chart
        monthly_revenue: Dict[str, float] = {}
        for j in jobs:
            try:
                month_key = j["date"][:7]
                monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + j.get(
                    "final_cost", 0
                )
            except (KeyError, IndexError):
                pass

        revenue_trend = [
            {"month": k, "revenue": round(v, 2)} for k, v in sorted(monthly_revenue.items())
        ]

        # Status distribution
        status_distribution = {
            "completed": len(completed),
            "in-progress": len(in_progress),
            "pending": len(pending),
        }

        return {
            "total_jobs": total_jobs,
            "total_clients": len(clients),
            "completed_jobs": len(completed),
            "in_progress_jobs": len(in_progress),
            "pending_jobs": len(pending),
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "total_parts_cost": round(total_parts, 2),
            "total_labor_cost": round(total_labor, 2),
            "average_profit": round(avg_profit, 2),
            "average_grade": chr(int(avg_grade)),
            "average_duration_minutes": round(avg_duration),
            "status_distribution": status_distribution,
            "revenue_trend": revenue_trend,
        }

    # ═══════════════════════════════════════════════════════════
    # DEMO DATA SEEDING
    # ═══════════════════════════════════════════════════════════

    def seed_demo_data(self, trade: str) -> int:
        """Seed rich demo data for a given trade. Returns number of jobs seeded."""
        import random

        random.seed(trade)

        demos = {
            "plumber": {
                "rate": (75, 120),
                "icon": "🔧",
                "jobs": [
                    {
                        "client_name": "Maria Garcia",
                        "client_phone": "+52 55 1234 5678",
                        "client_email": "maria.garcia@email.com",
                        "client_address": "234 Reforma Ave., Downtown, CDMX",
                        "description": "Hot water pipe leak repair",
                        "diagnosis": 'Loose connection in 3/4" copper elbow, worn gasket',
                        "status": "completed",
                        "final_cost": 2850.00,
                        "parts_cost": 850.00,
                        "labor_cost": 2000.00,
                        "profit": 950.00,
                        "grade": "A",
                        "duration_minutes": 120,
                    },
                    {
                        "client_name": "Carlos Lopez",
                        "client_phone": "+52 55 2345 6789",
                        "client_email": "carlos.lopez@email.com",
                        "client_address": "156 5 de Mayo St., Roma, CDMX",
                        "description": "Main drain unclogging",
                        "diagnosis": "Severe blockage from grease and solid waste buildup in 4m section",
                        "status": "completed",
                        "final_cost": 1800.00,
                        "parts_cost": 300.00,
                        "labor_cost": 1500.00,
                        "profit": 600.00,
                        "grade": "A",
                        "duration_minutes": 90,
                    },
                    {
                        "client_name": "Ana Martinez",
                        "client_phone": "+52 55 3456 7890",
                        "client_email": "ana.mtz@email.com",
                        "client_address": "890 Insurgentes Sur Ave., Del Valle, CDMX",
                        "description": "Tankless water heater installation",
                        "diagnosis": "Installation of 10L tankless water heater with copper connections and pressure valve",
                        "status": "completed",
                        "final_cost": 4200.00,
                        "parts_cost": 2200.00,
                        "labor_cost": 2000.00,
                        "profit": 1400.00,
                        "grade": "A",
                        "duration_minutes": 240,
                    },
                    {
                        "client_name": "Roberto Hernandez",
                        "client_phone": "+52 55 4567 8901",
                        "client_email": "roberto.hdz@email.com",
                        "client_address": "45 Cerro del Agua, Jardines del Pedregal, CDMX",
                        "description": "Toilet fill valve replacement",
                        "diagnosis": "Broken fill valve, uncalibrated float, worn flush button gasket",
                        "status": "in-progress",
                        "final_cost": 1200.00,
                        "parts_cost": 450.00,
                        "labor_cost": 750.00,
                        "profit": 400.00,
                        "grade": "B",
                        "duration_minutes": 60,
                    },
                    {
                        "client_name": "Sofia Ramirez",
                        "client_phone": "+52 55 5678 9012",
                        "client_email": "sofia.ramirez@email.com",
                        "client_address": "450 Reforma Ave., Cuauhtemoc, CDMX",
                        "description": "Water tank and pump installation",
                        "diagnosis": "Installation of 1100L water tank with 1/2 HP peripheral pump and PVC piping",
                        "status": "pending",
                        "final_cost": 6500.00,
                        "parts_cost": 3800.00,
                        "labor_cost": 2700.00,
                        "profit": 1800.00,
                        "grade": "",
                        "duration_minutes": 0,
                    },
                    {
                        "client_name": "Pedro Sanchez",
                        "client_phone": "+52 55 6789 0123",
                        "client_email": "pedro.sanchez@email.com",
                        "client_address": "12 Callejon del Agua, Xochimilco, CDMX",
                        "description": "Main water shut-off valve leak",
                        "diagnosis": "Rusted gate valve, won't close completely, constant drip",
                        "status": "completed",
                        "final_cost": 950.00,
                        "parts_cost": 350.00,
                        "labor_cost": 600.00,
                        "profit": 300.00,
                        "grade": "B",
                        "duration_minutes": 45,
                    },
                ],
            },
            "electrician": {
                "rate": (80, 160),
                "icon": "⚡",
                "jobs": [
                    {
                        "client_name": "Laura Torres",
                        "client_phone": "+52 55 1111 2222",
                        "client_email": "laura.torres@email.com",
                        "client_address": "567 Universidad Ave., Narvarte, CDMX",
                        "description": "Solar panel and backup system installation",
                        "diagnosis": "Installation of 300W solar panel, inverter, and battery bank for backup power",
                        "status": "completed",
                        "final_cost": 15000.00,
                        "parts_cost": 9500.00,
                        "labor_cost": 5500.00,
                        "profit": 4500.00,
                        "grade": "A",
                        "duration_minutes": 480,
                    },
                    {
                        "client_name": "Jorge Mendoza",
                        "client_phone": "+52 55 2222 3333",
                        "client_email": "jorge.mendoza@email.com",
                        "client_address": "78 16 de Septiembre St., San Angel, CDMX",
                        "description": "Short circuit in main breaker panel",
                        "diagnosis": "100A thermal-magnetic breaker damaged by overload, burned AWG 2 wiring",
                        "status": "completed",
                        "final_cost": 3200.00,
                        "parts_cost": 1200.00,
                        "labor_cost": 2000.00,
                        "profit": 1100.00,
                        "grade": "A",
                        "duration_minutes": 180,
                    },
                    {
                        "client_name": "Diana Flores",
                        "client_phone": "+52 55 3333 4444",
                        "client_email": "diana.flores@email.com",
                        "client_address": "234 Blvd. de las Luces, Satelite, EDOMEX",
                        "description": "Full office LED lighting installation",
                        "diagnosis": "Installation of 24 recessed LED fixtures on 4 independent circuits with dimmers",
                        "status": "completed",
                        "final_cost": 8800.00,
                        "parts_cost": 4800.00,
                        "labor_cost": 4000.00,
                        "profit": 2600.00,
                        "grade": "A",
                        "duration_minutes": 360,
                    },
                    {
                        "client_name": "Miguel Angel Ruiz",
                        "client_phone": "+52 55 4444 5555",
                        "client_email": "ma.ruiz@email.com",
                        "client_address": "56 Privada del Angel, Lomas de Chapultepec, CDMX",
                        "description": "Second floor outlet failure",
                        "diagnosis": "AWG 12 wiring with melted insulation from overheating in 3 outlets",
                        "status": "in-progress",
                        "final_cost": 2100.00,
                        "parts_cost": 600.00,
                        "labor_cost": 1500.00,
                        "profit": 700.00,
                        "grade": "B",
                        "duration_minutes": 120,
                    },
                    {
                        "client_name": "Patricia Vega",
                        "client_phone": "+52 55 5555 6666",
                        "client_email": "paty.vega@email.com",
                        "client_address": "89 Calle de la Luz, Condesa, CDMX",
                        "description": "Grounding system and lightning rod installation",
                        "diagnosis": "Grounding system with 5/8 copperweld rod and Franklin-type lightning rod",
                        "status": "pending",
                        "final_cost": 7500.00,
                        "parts_cost": 4200.00,
                        "labor_cost": 3300.00,
                        "profit": 2100.00,
                        "grade": "",
                        "duration_minutes": 0,
                    },
                    {
                        "client_name": "Fernando Ortega",
                        "client_phone": "+52 55 6666 7777",
                        "client_email": "fortega@email.com",
                        "client_address": "33 Av. de los Electricistas, Industrial, CDMX",
                        "description": "5HP pump motor repair",
                        "diagnosis": "Burned starter coil, blown 50uF electrolytic capacitor, worn bearings",
                        "status": "completed",
                        "final_cost": 3800.00,
                        "parts_cost": 1800.00,
                        "labor_cost": 2000.00,
                        "profit": 1200.00,
                        "grade": "B",
                        "duration_minutes": 200,
                    },
                ],
            },
            "hvac": {
                "rate": (85, 175),
                "icon": "❄️",
                "jobs": [
                    {
                        "client_name": "Ricardo Paredes",
                        "client_phone": "+52 55 7777 8888",
                        "client_email": "ricardo.paredes@email.com",
                        "client_address": "123 Av. Clima, Polanco, CDMX",
                        "description": "2-ton mini-split corrective maintenance",
                        "diagnosis": "Saturated air filter, frozen evaporator coil, R-22 refrigerant 30% low",
                        "status": "completed",
                        "final_cost": 2800.00,
                        "parts_cost": 800.00,
                        "labor_cost": 2000.00,
                        "profit": 900.00,
                        "grade": "A",
                        "duration_minutes": 150,
                    },
                    {
                        "client_name": "Veronica Campos",
                        "client_phone": "+52 55 8888 9999",
                        "client_email": "vero.campos@email.com",
                        "client_address": "56 Calle del Fresno, Jardines del Pedregal, CDMX",
                        "description": "5-ton central AC system installation",
                        "diagnosis": "Installation of York 5-ton condensing unit, air handler, ductwork, and smart thermostat",
                        "status": "completed",
                        "final_cost": 35000.00,
                        "parts_cost": 22000.00,
                        "labor_cost": 13000.00,
                        "profit": 9000.00,
                        "grade": "A",
                        "duration_minutes": 960,
                    },
                    {
                        "client_name": "Gabriel Nunez",
                        "client_phone": "+52 55 9999 0000",
                        "client_email": "gabriel.nunez@email.com",
                        "client_address": "789 Blvd. del Aire, Santa Fe, CDMX",
                        "description": "Condensing unit won't start",
                        "diagnosis": "Deteriorated 35uF start capacitor, welded contactor, blown thermal fuses",
                        "status": "completed",
                        "final_cost": 1800.00,
                        "parts_cost": 650.00,
                        "labor_cost": 1150.00,
                        "profit": 550.00,
                        "grade": "B",
                        "duration_minutes": 90,
                    },
                    {
                        "client_name": "Alejandra Cruz",
                        "client_phone": "+52 55 0000 1111",
                        "client_email": "ale.cruz@email.com",
                        "client_address": "23 Privada de la Brisa, Del Valle, CDMX",
                        "description": "Evaporator unit refrigerant leak",
                        "diagnosis": "Evaporator coil spiral leak from corrosion, complete R-410A charge loss",
                        "status": "in-progress",
                        "final_cost": 4500.00,
                        "parts_cost": 2800.00,
                        "labor_cost": 1700.00,
                        "profit": 1300.00,
                        "grade": "C",
                        "duration_minutes": 200,
                    },
                    {
                        "client_name": "Humberto Rios",
                        "client_phone": "+52 55 1112 1314",
                        "client_email": "humberto.rios@email.com",
                        "client_address": "67 Calle del Calor, Escandon, CDMX",
                        "description": "Preventive maintenance for 3 mini-splits",
                        "diagnosis": "Deep cleaning of 3 units, refrigerant recharge, electrical check, and thermostat calibration",
                        "status": "pending",
                        "final_cost": 3200.00,
                        "parts_cost": 600.00,
                        "labor_cost": 2600.00,
                        "profit": 1100.00,
                        "grade": "",
                        "duration_minutes": 0,
                    },
                    {
                        "client_name": "Silvia Mendez",
                        "client_phone": "+52 55 1415 1617",
                        "client_email": "silvia.mendez@email.com",
                        "client_address": "90 Av. de los Vientos, Lindavista, CDMX",
                        "description": "Thermostat not triggering heating system",
                        "diagnosis": "Digital thermostat misprogrammed, shorted 24VAC control wire, damaged boiler relay",
                        "status": "completed",
                        "final_cost": 1600.00,
                        "parts_cost": 550.00,
                        "labor_cost": 1050.00,
                        "profit": 500.00,
                        "grade": "A",
                        "duration_minutes": 80,
                    },
                ],
            },
        }

        data = demos.get(trade.lower())
        if not data:
            logger.warning(f"No demo data for trade: {trade}")
            return 0

        existing_jobs = self._read_json(JOBS_FILE)
        existing_ids = {j.get("job_id") for j in existing_jobs}
        existing_clients = self._read_json(CLIENTS_FILE)
        count = 0

        hourly_rate = sum(data["rate"]) / 2
        days_ago = len(data["jobs"])

        for i, job in enumerate(data["jobs"]):
            job_id = f"demo_{trade}_{i + 1:02d}"
            if job_id in existing_ids:
                continue

            job_date = (datetime.now() - timedelta(days=days_ago - i)).isoformat()

            record = {
                "job_id": job_id,
                "client_name": job["client_name"],
                "client_phone": job["client_phone"],
                "client_email": job["client_email"],
                "client_address": job["client_address"],
                "date": job_date,
                "diagnosis": job["diagnosis"],
                "description": job["description"],
                "status": job["status"],
                "trade": trade,
                "final_cost": job["final_cost"],
                "parts_cost": job["parts_cost"],
                "labor_cost": job["labor_cost"],
                "profit": job["profit"],
                "grade": job["grade"],
                "duration_minutes": job["duration_minutes"],
                "hourly_rate": hourly_rate,
                "is_demo": True,
            }

            existing_jobs.append(record)

            client = None
            for c in existing_clients:
                if c["name"].lower() == job["client_name"].lower():
                    client = c
                    break

            if not client:
                client = {
                    "id": f"client_{len(existing_clients) + 1:04d}",
                    "name": job["client_name"],
                    "phone": job["client_phone"],
                    "email": job["client_email"],
                    "address": job["client_address"],
                    "created_at": datetime.now().isoformat(),
                    "total_jobs": 0,
                    "total_spent": 0.0,
                    "preferred_payment": "cash",
                    "notes": [],
                }
                existing_clients.append(client)

            client["email"] = job["client_email"]
            client["address"] = job["client_address"]
            client["total_jobs"] += 1
            client["total_spent"] += job["final_cost"]

            count += 1

        self._write_json(JOBS_FILE, existing_jobs)
        self._write_json(CLIENTS_FILE, existing_clients)

        logger.info(f"Seeded {count} demo jobs for trade '{trade}'")
        return count

    # ═══════════════════════════════════════════════════════════
    # AGENT CONTEXT RETRIEVAL
    # ═══════════════════════════════════════════════════════════

    def get_context_for_steward(self, client_name: str, trade: str) -> str:
        history = self.get_client_history(client_name)

        if not history["exists"]:
            return "This is a new client. No historical data available."

        context = f"Client {client_name} has done {history['total_jobs']} jobs with us. "
        context += f"Total historical spend: ${history['total_spent']:.2f}. "
        context += f"They prefer to pay via {history['preferred_payment']}. "

        if history["past_jobs"]:
            avg_profit = sum(j.get("profit", 0) for j in history["past_jobs"]) / len(
                history["past_jobs"]
            )
            context += f"Average profit on their past jobs: ${avg_profit:.2f}. "

        return context

    def get_context_for_kit(self, trade: str, recent_jobs: int = 10) -> str:
        jobs = self._read_json(JOBS_FILE)[-recent_jobs:]
        similar_jobs = [j for j in jobs if trade.lower() in j.get("diagnosis", "").lower()]

        if not similar_jobs:
            return f"No recent history for {trade} jobs."

        context = f"Based on {len(similar_jobs)} recent {trade} jobs: "
        most_common_parts = {}
        for job in similar_jobs:
            parts = job.get("diagnosis", "").lower()
            for word in parts.split():
                word = word.strip(",.!?;:")
                if len(word) > 3:
                    most_common_parts[word] = most_common_parts.get(word, 0) + 1

        common = sorted(most_common_parts.items(), key=lambda x: -x[1])[:5]
        if common:
            context += f"Most frequent issues: {', '.join(w for w, _ in common)}. "

        avg_duration = sum(j.get("duration_minutes", 0) for j in similar_jobs) / len(similar_jobs)
        context += f"Average job duration: {avg_duration:.0f} minutes. "
        avg_grade = sum(ord(j.get("grade", "C")) for j in similar_jobs) / len(similar_jobs)
        context += f"Average job grade: {chr(int(avg_grade))}. "

        return context


# Singleton instance
memory_service = MemoryService()
