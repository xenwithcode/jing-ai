"""Artisan Dashboard endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.agents.steward import StewardAgent
from src.services.memory import memory_service
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class StatusUpdate(BaseModel):
    status: str


class SeedRequest(BaseModel):
    trade: str = "plumber"


class AskRequest(BaseModel):
    question: str
    trade: Optional[str] = None


@router.get("/artisan/dashboard")
async def get_dashboard(trade: Optional[str] = Query(None)):
    """Get aggregate dashboard statistics for the artisan."""
    stats = memory_service.get_dashboard_stats(trade=trade)
    return {"success": True, "data": stats}


@router.get("/artisan/jobs")
async def get_jobs(
    trade: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    """Get all jobs, optionally filtered by trade and/or status."""
    jobs = memory_service.get_all_jobs(trade=trade, status=status)
    stats = memory_service.get_dashboard_stats(trade=trade)
    return {
        "success": True,
        "data": {
            "jobs": jobs,
            "total": len(jobs),
            "stats": stats,
        },
    }


@router.patch("/artisan/jobs/{job_id}/status")
async def update_job_status(job_id: str, body: StatusUpdate):
    """Update the status of a job."""
    valid = {"pending", "in-progress", "completed"}
    if body.status not in valid:
        raise HTTPException(
            status_code=400, detail=f"Status must be one of: {', '.join(sorted(valid))}"
        )

    job = memory_service.update_job_status(job_id, body.status)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {"success": True, "data": job}


@router.get("/artisan/steward-suggestion")
async def get_steward_suggestion(trade: Optional[str] = Query(None)):
    """Get detailed multi-category suggestions from JING-STEWARD based on dashboard data."""
    stats = memory_service.get_dashboard_stats(trade=trade)
    jobs = memory_service.get_all_jobs(trade=trade)

    context_lines = [
        "═══ ARTISAN BUSINESS ANALYSIS ═══\n",
        "📊 DASHBOARD OVERVIEW:",
        f"   Trade: {trade or 'All Trades'}",
        f"   Total jobs: {stats['total_jobs']}",
        f"   Completed: {stats['completed_jobs']}",
        f"   In progress: {stats['in_progress_jobs']}",
        f"   Pending: {stats['pending_jobs']}",
        f"   Total clients: {stats['total_clients']}",
        "\n💰 FINANCIAL SNAPSHOT:",
        f"   Total revenue: ${stats['total_revenue']}",
        f"   Total profit: ${stats['total_profit']}",
        f"   Total parts cost: ${stats['total_parts_cost']}",
        f"   Total labor cost: ${stats['total_labor_cost']}",
        f"   Average profit per job: ${stats['average_profit']}",
        f"   Average grade: {stats['average_grade']}",
        f"   Average duration: {stats['average_duration_minutes']} min",
        "\n📈 PERFORMANCE TRENDS:",
    ]

    if jobs:
        completed_jobs = [j for j in jobs if j.get("status") == "completed"]
        grades = [j.get("grade", "C") for j in completed_jobs]
        profits = [j.get("profit", 0) for j in completed_jobs]
        durations = [j.get("duration_minutes", 0) for j in completed_jobs]

        context_lines.append(f"   Recent grades: {', '.join(grades[-10:])}")
        if len(profits) >= 2:
            recent_avg = sum(profits[-3:]) / min(3, len(profits))
            early_avg = sum(profits[:3]) / min(3, len(profits))
            trend = (
                "📈 improving"
                if recent_avg > early_avg
                else "📉 declining"
                if recent_avg < early_avg
                else "➡️ stable"
            )
            context_lines.append(
                f"   Profit trend: {trend} (recent avg ${recent_avg:.0f} vs early avg ${early_avg:.0f})"
            )
        if durations:
            avg_dur = sum(durations) / len(durations)
            context_lines.append(f"   Avg job duration: {avg_dur:.0f} min")

        top_clients = sorted(
            [(j.get("client_name", "Unknown"), j.get("final_cost", 0)) for j in completed_jobs],
            key=lambda x: -x[1],
        )[:3]
        if top_clients:
            context_lines.append("\n🏆 TOP CLIENTS BY REVENUE:")
            for name, rev in top_clients:
                context_lines.append(f"   • {name}: ${rev:.2f}")

    if stats["revenue_trend"]:
        months = stats["revenue_trend"]
        if len(months) >= 2:
            growth = (
                (months[-1]["revenue"] - months[0]["revenue"]) / max(months[0]["revenue"], 1)
            ) * 100
            context_lines.append(f"\n📅 REVENUE GROWTH: {growth:+.1f}% over {len(months)} months")

    context_lines.append("\n💼 CLIENT INSIGHTS:")
    context_lines.append(f"   Total clients served: {stats['total_clients']}")
    if stats["total_clients"] > 0 and stats["total_jobs"] > 0:
        context_lines.append(
            f"   Repeat business rate: {stats['completed_jobs']}/{stats['total_clients']} jobs per client"
        )
    context_lines.append(
        f"   Average revenue per client: ${stats['total_revenue'] / max(stats['total_clients'], 1):.2f}"
    )

    context_lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    context = "\n".join(context_lines)

    prompt = f"""You are JING-STEWARD, the world's most insightful AI financial advisor for tradespeople. You have access to this artisan's complete business data.

Analyze the following business data and provide THREE distinct, actionable suggestions across different areas (pricing, efficiency, growth, client relationships, operations, etc.).

{context}

Requirements:
1. Each suggestion MUST be specific and data-driven (reference actual numbers from the data)
2. Each suggestion must have a clear category label
3. Be encouraging but honest — celebrate wins AND flag concerns
4. Write naturally, as if you're a seasoned business coach talking to a fellow tradesperson

Respond ONLY with valid JSON in this exact format:
{{
  "business_health": "A brief 1-sentence overall health assessment (e.g., 'Your plumbing business is thriving with strong margins and consistent A-grade work.')",
  "focus_priority": "One word category the artisan should focus on most: pricing, efficiency, growth, clients, or operations",
  "suggestions": [
    {{
      "category": "pricing",
      "title": "Short catchy title (e.g., 'Raise Your Emergency Rates')",
      "suggestion": "Detailed explanation of the suggestion with specific data references (2-3 sentences)",
      "reason": "Why this matters for their specific business (1-2 sentences)",
      "action": "A concrete, specific next step they can take TODAY (1-2 sentences)",
      "potential_impact": "What improvement they can expect (e.g., '+15% monthly profit')"
    }}
  ]
}}"""

    steward = StewardAgent()
    try:
        result = await steward.call_qwen_json(
            model=steward.model,
            user_message=prompt,
            system="You are JING-STEWARD, an expert financial advisor for tradespeople. Analyze data deeply and respond ONLY with valid JSON.",
            temperature=0.4,
            max_tokens=2000,
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Steward suggestion failed: {e}")
        return {
            "success": True,
            "data": {
                "business_health": "Your business has solid fundamentals with room to grow.",
                "focus_priority": "pricing",
                "suggestions": [
                    {
                        "category": "pricing",
                        "title": "Optimize Your Pricing Strategy",
                        "suggestion": f"Based on your data, you're averaging ${stats['average_profit']:.0f} profit per job with a {stats['average_grade']} grade. Consider adjusting your rates to capture more value from high-quality work.",
                        "reason": "Many tradespeople underprice their services, especially when they consistently deliver A-grade work like you do.",
                        "action": "Review your last 5 invoices and increase your labor rate by 10-15% for new quotes this week.",
                        "potential_impact": f"+${(stats['average_profit'] * 0.15):.0f} extra profit per job on average",
                    },
                    {
                        "category": "efficiency",
                        "title": "Reduce Job Duration Variance",
                        "suggestion": f"Your average job takes {stats['average_duration_minutes']} minutes. Look for patterns in jobs that run over estimate to tighten efficiency.",
                        "reason": "Time is your most valuable asset — every hour saved is billable capacity for another job.",
                        "action": "Track which job types consistently run over estimate and create prep checklists for those specific scenarios.",
                        "potential_impact": "20-30% fewer overtime hours and more jobs completed per week",
                    },
                    {
                        "category": "growth",
                        "title": "Leverage Your Best Clients for Referrals",
                        "suggestion": f"You've served {stats['total_clients']} clients. Your top clients by revenue are valuable referral sources that you haven't fully tapped.",
                        "reason": "Referral customers have a higher lifetime value and lower acquisition cost than any marketing channel.",
                        "action": "Text your top 3 clients a thank-you note and ask if they know anyone who needs your services — offer a $50 discount for referrals.",
                        "potential_impact": "3-5 new high-quality leads per month with zero marketing spend",
                    },
                ],
            },
        }


@router.post("/artisan/ask")
async def ask_jing(body: AskRequest):
    """Ask JING-STEWARD any business question — get AI-powered advice with data context."""
    trade = body.trade
    stats = memory_service.get_dashboard_stats(trade=trade)
    jobs = memory_service.get_all_jobs(trade=trade)

    context_lines = [
        f"═══ ARTISAN BUSINESS DATA (Trade: {trade or 'All'}) ═══",
        f"Total jobs: {stats['total_jobs']} ({stats['completed_jobs']} completed, {stats['in_progress_jobs']} in progress, {stats['pending_jobs']} pending)",
        f"Total clients: {stats['total_clients']}",
        f"Total revenue: ${stats['total_revenue']}",
        f"Total profit: ${stats['total_profit']}",
        f"Total parts cost: ${stats['total_parts_cost']}",
        f"Total labor cost: ${stats['total_labor_cost']}",
        f"Average profit/job: ${stats['average_profit']}",
        f"Average grade: {stats['average_grade']}",
        f"Average duration: {stats['average_duration_minutes']} min",
    ]

    if jobs:
        completed_jobs = [j for j in jobs if j.get("status") == "completed"]
        context_lines.append("\nTop clients by revenue:")
        top = sorted(
            [(j.get("client_name", "?"), j.get("final_cost", 0)) for j in completed_jobs],
            key=lambda x: -x[1],
        )[:5]
        for name, rev in top:
            context_lines.append(f"  • {name}: ${rev:.2f}")

        context_lines.append(
            f"\nRecent job grades: {', '.join([j.get('grade', 'C') for j in completed_jobs[-8:]])}"
        )

    context = "\n".join(context_lines)

    prompt = f"""You are JING-STEWARD, a master business advisor for tradespeople. You have a warm, mentor-like tone and give practical, actionable advice.

=== ARTISAN BUSINESS DATA ===
{context}

=== ARTISAN'S QUESTION ===
{body.question}

=== INSTRUCTIONS ===
Answer the artisan's question conversationally using the data above.
Rules:
- Be specific, reference actual numbers from their data
- Give practical, actionable advice a tradesperson can use TODAY
- Keep it concise but thorough (3-5 paragraphs)
- Use a warm, mentor-like tone — you're their AI business partner
- If the data doesn't fully answer the question, acknowledge that and give your best advice
- Format naturally with short paragraphs (no markdown, no JSON)"""

    steward = StewardAgent()
    try:
        response = await steward.call_qwen(
            model=steward.model,
            user_message=prompt,
            temperature=0.5,
            max_tokens=1500,
        )
        return {"success": True, "data": {"answer": response.strip()}}
    except Exception as e:
        logger.error(f"Ask JING failed: {e}")
        return {
            "success": True,
            "data": {
                "answer": "Great question! Based on your business data, here's my advice:\n\n"
                f"1. **Pricing**: Your average profit per job is ${stats['average_profit']:.0f}. "
                f"Consider a 10-15% rate increase — even a small bump can significantly impact your bottom line.\n\n"
                f"2. **Efficiency**: Your average job time is {stats['average_duration_minutes']} minutes. "
                f"Track which tasks take longest and create prep routines to cut waste.\n\n"
                f"3. **Growth**: You've served {stats['total_clients']} great clients. "
                "A simple referral program could bring consistent new business with zero marketing cost.\n\n"
                "Want me to dive deeper into any of these areas? Just ask!"
            },
        }


@router.post("/artisan/seed-demo")
async def seed_demo_data(body: SeedRequest):
    """Seed demo job data for a specific trade (hackathon demo use)."""
    count = memory_service.seed_demo_data(body.trade)
    if count == 0:
        return {
            "success": True,
            "message": f"Demo data already exists for {body.trade}",
            "seeded": 0,
        }
    return {
        "success": True,
        "message": f"Seeded {count} demo jobs for {body.trade}",
        "seeded": count,
    }
