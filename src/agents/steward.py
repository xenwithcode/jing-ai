"""
JING-STEWARD: The Financial Guardian

JING-STEWARD is the trusted financial advisor of the artisan's guild.
It manages the complete financial lifecycle of every job:

1. BEFORE the job: Generates professional budgets with transparent pricing
2. AFTER the job: Creates detailed financial summaries with insights

Most artisans are brilliant with tools but struggle with numbers. JING-STEWARD
changes that by providing:
- Fair, profitable pricing
- Professional budget documents
- Real-time cost tracking
- Post-job financial analysis
- Performance benchmarking

Usage:
    >>> from src.agents.steward import StewardAgent
    >>> steward = StewardAgent()
    
    # Generate budget before job
    >>> budget = await steward.generate_budget(
    ...     diagnosis="Moen Chateau 7400 cartridge failure",
    ...     parts_cost=22.00,
    ...     estimated_hours=0.5,
    ...     trade="plumber"
    ... )
    
    # Generate financial summary after job
    >>> summary = await steward.generate_financial_summary(
    ...     budget=budget,
    ...     actual_parts_cost=30.00,
    ...     actual_hours=0.83,
    ...     amount_charged=160.00
    ... )
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.agents.base_agent import BaseAgent, AgentExecutionError, AgentValidationError
from src.utils.config import settings
from src.services.memory import memory_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


TRADE_RATES = {
    "plumber": {"min": 75, "avg": 100, "max": 150},
    "electrician": {"min": 80, "avg": 110, "max": 160},
    "hvac": {"min": 85, "avg": 120, "max": 175},
    "appliance": {"min": 70, "avg": 95, "max": 130},
    "handyman": {"min": 60, "avg": 80, "max": 100},
    "general": {"min": 60, "avg": 85, "max": 120},
}


class StewardAgent(BaseAgent):
    """
    JING-STEWARD: Financial guardian of the artisan's guild.
    
    Handles all financial aspects of a job:
    - Budget generation before work begins
    - Financial summary after work completion
    - Performance tracking and insights
    """
    
    def __init__(self):
        super().__init__(name="JING-STEWARD")
        logger.info("JING-STEWARD initialized (financial guardian)")
    
    def _get_default_model(self) -> str:
        return settings.QWEN_PLUS_MODEL
    
    # ═══════════════════════════════════════════════════════════
    # MODE 1: BUDGET GENERATION
    # ═══════════════════════════════════════════════════════════
    
    async def generate_budget(
        self,
        diagnosis: str,
        parts: Optional[List[Dict[str, Any]]] = None,
        tools: Optional[List[str]] = None,
        estimated_hours: Optional[float] = None,
        trade: str = "general",
        client_name: Optional[str] = None,
        urgency: str = "normal",
        eye_analysis: Optional[Dict[str, Any]] = None,
        kit_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a professional budget for a job.
        
        Args:
            diagnosis: Description of the problem
            parts: List of parts with costs (from JING-KIT)
            tools: List of tools needed
            estimated_hours: Estimated labor hours
            trade: Type of trade
            client_name: Client name (or "New Client")
            urgency: Job urgency (critical, high, normal, low)
            eye_analysis: Full analysis from JING-EYE
            kit_result: Full result from JING-KIT
        
        Returns:
            Complete budget structure ready for PDF generation
        """
        logger.info(f"JING-STEWARD generating budget for: {diagnosis[:50]}...")
        
        if not parts and kit_result:
            parts = []
            for part in kit_result.get("parts_required", []):
                price = 0.0
                if part.get("where_to_buy"):
                    price_str = part["where_to_buy"][0].get("estimated_price", "$0")
                    try:
                        import re
                        numbers = re.findall(r'\d+', price_str)
                        if numbers:
                            price = float(numbers[0])
                    except:
                        price = 0.0
                
                parts.append({
                    "item": part.get("part_name", "Unknown part"),
                    "quantity": 1,
                    "unit_price": price,
                    "total": price,
                })
        
        if not estimated_hours:
            estimated_hours = 1.0
        
        parts_total = sum(p.get("total", 0) for p in (parts or []))
        
        # ═══════════════════════════════════════════════════════════
        # RETRIEVE MEMORY CONTEXT
        # ═══════════════════════════════════════════════════════════
        
        memory_context = ""
        if client_name and client_name != "New Client":
            memory_context = memory_service.get_context_for_steward(client_name, trade)
            logger.info(f"Retrieved memory context for {client_name}")
        
        prompt = self._build_budget_prompt(
            diagnosis=diagnosis,
            parts=parts,
            parts_total=parts_total,
            tools=tools,
            estimated_hours=estimated_hours,
            trade=trade,
            client_name=client_name,
            urgency=urgency,
            memory_context=memory_context,
        )
        
        try:
            response_text = await self.call_qwen(
                user_message=prompt,
                temperature=0.3,
                max_tokens=2500,
            )
        except Exception as e:
            logger.error(f"JING-STEWARD budget generation failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Budget generation failed: {e}") from e
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JING-STEWARD returned invalid JSON: {response_text[:200]}...")
            raise AgentExecutionError(f"Invalid JSON from STEWARD: {e}") from e
        
        validated_result = self._validate_budget(result)
        
        logger.info(
            f"JING-STEWARD generated budget: "
            f"${validated_result['cost_breakdown']['total_rounded']}, "
            f"margin: {validated_result['cost_breakdown']['margin_percentage']}%"
        )
        
        return validated_result
    
    def _build_budget_prompt(
        self,
        diagnosis: str,
        parts: Optional[List[Dict[str, Any]]],
        parts_total: float,
        tools: Optional[List[str]],
        estimated_hours: float,
        trade: str,
        client_name: Optional[str],
        urgency: str,
        memory_context: str = "",
    ) -> str:
        lines = ["═══ BUDGET GENERATION REQUEST ═══\n"]
        
        lines.append(f"🔍 DIAGNOSIS: {diagnosis}")
        lines.append(f"🔧 TRADE: {trade}")
        lines.append(f"⏱️  ESTIMATED HOURS: {estimated_hours}")
        lines.append(f"⚡ URGENCY: {urgency}")
        
        if client_name:
            lines.append(f"👤 CLIENT: {client_name}")
        
        if parts:
            lines.append(f"\n📦 PARTS (${parts_total:.2f} total):")
            for part in parts:
                lines.append(
                    f"   • {part.get('item', 'Unknown')}: "
                    f"${part.get('unit_price', 0):.2f} × {part.get('quantity', 1)}"
                )
        
        if tools:
            lines.append(f"\n🛠️  TOOLS: {', '.join(tools[:5])}")
        
        rates = TRADE_RATES.get(trade, TRADE_RATES["general"])
        lines.append(f"\n💰 TRADE RATE GUIDANCE ({trade}):")
        lines.append(f"   Min: ${rates['min']}/h | Avg: ${rates['avg']}/h | Max: ${rates['max']}/h")
        
        if urgency == "critical":
            lines.append("\n⚠️  CRITICAL URGENCY: Apply +50% emergency premium")
        elif urgency == "high":
            lines.append("\n⚡ HIGH URGENCY: Apply +25% premium")
        
        if memory_context:
            lines.append(f"\n CLIENT MEMORY & HISTORY:")
            lines.append(f"   {memory_context}")
            lines.append(f"   Use this history to adjust pricing (e.g., offer loyalty discount if they are a repeat client).")
        
        lines.append("\n══════════════════════════════════")
        lines.append("\nGenerate a professional budget in JSON format.")
        lines.append("Rules:")
        lines.append("- Include 20-35% profit margin (never below 15%)")
        lines.append("- Round total to clean number")
        lines.append("- Include 8% tax unless specified otherwise")
        lines.append("- Be transparent with client-friendly descriptions")
        lines.append("- Protect the artisan's financial health")
        
        return "\n".join(lines)
    
    def _validate_budget(self, result: Dict[str, Any]) -> Dict[str, Any]:
        required_keys = ["budget_metadata", "cost_breakdown", "payment_terms", "financial_health"]
        for key in required_keys:
            if key not in result:
                raise AgentValidationError(f"Budget missing required key: {key}")
        
        cb = result["cost_breakdown"]
        if "total_rounded" not in cb:
            cb["total_rounded"] = round(cb.get("total", 0) / 5) * 5
        
        margin = cb.get("margin_percentage", 0)
        if margin < 15:
            logger.warning(f"Budget margin {margin}% is below recommended 15%")
        
        if "client_info" not in result:
            result["client_info"] = {"name": "New Client", "address": None, "contact": None}
        
        if "job_description" not in result:
            result["job_description"] = {
                "summary": result.get("budget_metadata", {}).get("job_title", "Repair job"),
                "scope": [],
                "exclusions": [],
                "estimated_duration": "1 hour",
            }
        
        if "warranty" not in result:
            result["warranty"] = {
                "parts_warranty": "Manufacturer warranty",
                "labor_warranty": "90 days",
                "void_conditions": [],
            }
        
        if "client_friendly_total" not in result:
            result["client_friendly_total"] = f"${cb['total_rounded']:.2f}"
        
        logger.debug("Budget validated successfully")
        return result
    
    # ═══════════════════════════════════════════════════════════
    # MODE 2: FINANCIAL SUMMARY
    # ═══════════════════════════════════════════════════════════
    
    async def generate_financial_summary(
        self,
        budget: Dict[str, Any],
        actual_parts_cost: float,
        actual_hours: float,
        amount_charged: float,
        client_name: str = "Client",
        job_title: Optional[str] = None,
        extra_costs: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a financial summary after job completion.
        
        Args:
            budget: Original budget from generate_budget()
            actual_parts_cost: Actual cost of parts used
            actual_hours: Actual hours worked
            amount_charged: Final amount charged to client
            client_name: Client name
            job_title: Job title/description
            extra_costs: Any additional costs incurred
        
        Returns:
            Complete financial summary with insights and chart data
        """
        logger.info(f"JING-STEWARD generating financial summary for: {job_title}")
        
        prompt = self._build_summary_prompt(
            budget=budget,
            actual_parts_cost=actual_parts_cost,
            actual_hours=actual_hours,
            amount_charged=amount_charged,
            client_name=client_name,
            job_title=job_title,
            extra_costs=extra_costs,
        )
        
        try:
            response_text = await self.call_qwen(
                user_message=prompt,
                temperature=0.3,
                max_tokens=2500,
            )
        except Exception as e:
            logger.error(f"JING-STEWARD summary generation failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Summary generation failed: {e}") from e
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JING-STEWARD returned invalid JSON: {response_text[:200]}...")
            raise AgentExecutionError(f"Invalid JSON from STEWARD: {e}") from e
        
        validated_result = self._validate_summary(result)
        
        logger.info(
            f"JING-STEWARD generated summary: "
            f"profit ${validated_result['profitability']['gross_profit']}, "
            f"grade {validated_result['profitability']['profitability_grade']}"
        )
        
        # ═══════════════════════════════════════════════════════════
        # SAVE TO PERSISTENT MEMORY
        # ═══════════════════════════════════════════════════════════
        
        memory_service.save_job({
            "client_name": client_name,
            "diagnosis": job_title or "",
            "final_cost": amount_charged,
            "profit": validated_result["profitability"]["gross_profit"],
            "grade": validated_result["profitability"]["profitability_grade"],
            "duration_minutes": int(actual_hours * 60),
        })
        
        logger.info(f"Job saved to persistent memory for {client_name}")
        
        return validated_result
    
    def _build_summary_prompt(
        self,
        budget: Dict[str, Any],
        actual_parts_cost: float,
        actual_hours: float,
        amount_charged: float,
        client_name: str,
        job_title: Optional[str],
        extra_costs: Optional[List[Dict[str, Any]]],
    ) -> str:
        lines = ["═══ FINANCIAL SUMMARY REQUEST ═══\n"]
        
        budget_total = budget.get("cost_breakdown", {}).get("total_rounded", 0)
        budget_parts = budget.get("cost_breakdown", {}).get("parts_subtotal", 0)
        budget_hours = budget.get("cost_breakdown", {}).get("labor", {}).get("estimated_hours", 0)
        
        lines.append("📋 ORIGINAL BUDGET:")
        lines.append(f"   Total: ${budget_total:.2f}")
        lines.append(f"   Parts: ${budget_parts:.2f}")
        lines.append(f"   Hours: {budget_hours}")
        
        lines.append("\n📊 ACTUAL RESULTS:")
        lines.append(f"   Amount charged: ${amount_charged:.2f}")
        lines.append(f"   Actual parts cost: ${actual_parts_cost:.2f}")
        lines.append(f"   Actual hours: {actual_hours}")
        
        if job_title:
            lines.append(f"\n🔧 JOB: {job_title}")
        
        lines.append(f"👤 CLIENT: {client_name}")
        
        if extra_costs:
            lines.append("\n💸 EXTRA COSTS:")
            for cost in extra_costs:
                lines.append(f"   • {cost.get('item', 'Unknown')}: ${cost.get('amount', 0):.2f}")
                if cost.get('reason'):
                    lines.append(f"     Reason: {cost['reason']}")
        
        parts_variance = actual_parts_cost - budget_parts
        hours_variance = actual_hours - budget_hours
        total_variance = amount_charged - budget_total
        
        lines.append("\n📈 VARIANCES:")
        lines.append(f"   Parts: ${parts_variance:+.2f}")
        lines.append(f"   Hours: {hours_variance:+.2f}")
        lines.append(f"   Total: ${total_variance:+.2f}")
        
        lines.append("\n══════════════════════════════════")
        lines.append("\nGenerate a comprehensive financial summary in JSON format.")
        lines.append("Include:")
        lines.append("- Profitability analysis with A-F grade")
        lines.append("- Performance metrics (time, cost, margin efficiency)")
        lines.append("- Actionable insights (what went well, what to improve)")
        lines.append("- Chart data for visualization (cost breakdown, budget vs actual)")
        lines.append("- Celebration message if job was profitable")
        
        return "\n".join(lines)
    
    def _validate_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        required_keys = ["job_info", "profitability", "chart_data"]
        for key in required_keys:
            if key not in result:
                raise AgentValidationError(f"Summary missing required key: {key}")
        
        if "comparison" not in result:
            result["comparison"] = {
                "budgeted_total": 0,
                "actual_total": 0,
                "variance": 0,
                "variance_percentage": 0,
                "variance_reason": "N/A",
            }
        
        if "cost_analysis" not in result:
            result["cost_analysis"] = {
                "parts_budgeted": 0,
                "parts_actual": 0,
                "parts_variance": 0,
                "labor_hours_budgeted": 0,
                "labor_hours_actual": 0,
                "labor_hours_variance": 0,
                "extra_costs": [],
            }
        
        if "performance_metrics" not in result:
            result["performance_metrics"] = {
                "time_efficiency": "on",
                "cost_efficiency": "on",
                "margin_vs_target": "at",
                "overall_score": 75,
                "score_label": "Good",
            }
        
        if "insights" not in result:
            result["insights"] = {
                "what_went_well": [],
                "what_to_improve": [],
                "pricing_recommendation": "Continue current pricing strategy",
                "red_flags": [],
            }
        
        if "celebration_message" not in result:
            result["celebration_message"] = ""
        
        logger.debug("Financial summary validated successfully")
        return result
    
    # ═══════════════════════════════════════════════════════════
    # EXECUTE (required by BaseAgent)
    # ═══════════════════════════════════════════════════════════
    
    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        mode = task_input.get("mode", "budget")
        
        if mode == "budget":
            return await self.generate_budget(
                diagnosis=task_input.get("diagnosis", ""),
                parts=task_input.get("parts"),
                tools=task_input.get("tools"),
                estimated_hours=task_input.get("estimated_hours"),
                trade=task_input.get("trade", "general"),
                client_name=task_input.get("client_name"),
                urgency=task_input.get("urgency", "normal"),
                eye_analysis=task_input.get("eye_analysis"),
                kit_result=task_input.get("kit_result"),
            )
        elif mode == "summary":
            return await self.generate_financial_summary(
                budget=task_input.get("budget", {}),
                actual_parts_cost=task_input.get("actual_parts_cost", 0),
                actual_hours=task_input.get("actual_hours", 0),
                amount_charged=task_input.get("amount_charged", 0),
                client_name=task_input.get("client_name", "Client"),
                job_title=task_input.get("job_title"),
                extra_costs=task_input.get("extra_costs"),
            )
        else:
            raise AgentValidationError(f"Unknown mode: {mode}")
    
    def get_budget_summary(self, budget: Dict[str, Any]) -> str:
        cb = budget.get("cost_breakdown", {})
        fh = budget.get("financial_health", {})
        
        return (
            f"Total: {budget.get('client_friendly_total', 'N/A')} | "
            f"Margin: {cb.get('margin_percentage', 0)}% | "
            f"Risk: {fh.get('risk_level', 'unknown')} | "
            f"Effective rate: ${fh.get('effective_hourly_rate', 0):.2f}/h"
        )
    
    def get_summary_highlights(self, summary: Dict[str, Any]) -> str:
        p = summary.get("profitability", {})
        pm = summary.get("performance_metrics", {})
        
        return (
            f"Profit: ${p.get('gross_profit', 0):.2f} | "
            f"Margin: {p.get('net_margin_percentage', 0):.1f}% | "
            f"Grade: {p.get('profitability_grade', 'N/A')} | "
            f"Score: {pm.get('overall_score', 0)}/100 ({pm.get('score_label', 'N/A')})"
        )


async def _demo():
    """Demo JING-STEWARD with both modes."""
    steward = StewardAgent()
    
    print("\n" + "="*70)
    print("JING-STEWARD Financial Demo")
    print("="*70)
    
    print("\n📋 MODE 1: Budget Generation")
    print("-" * 70)
    print("\nScenario: Moen Chateau 7400 faucet repair")
    
    try:
        budget = await steward.generate_budget(
            diagnosis="Moen Chateau 7400 cartridge failure causing drip",
            parts=[
                {"item": "Moen 1225 Cartridge", "quantity": 1, "unit_price": 22.00, "total": 22.00},
                {"item": "Replacement O-rings", "quantity": 1, "unit_price": 6.00, "total": 6.00},
            ],
            tools=["Allen key 3/32", "Needle-nose pliers"],
            estimated_hours=0.75,
            trade="plumber",
            client_name="John Smith",
            urgency="normal",
        )
        
        print("\n✅ Budget generated successfully!")
        
        print(f"\n📄 BUDGET #{budget['budget_metadata']['budget_number']}")
        print(f"   Client: {budget['client_info']['name']}")
        print(f"   Job: {budget['job_description']['summary']}")
        
        cb = budget['cost_breakdown']
        print(f"\n💰 COST BREAKDOWN:")
        print(f"   Parts: ${cb['parts_subtotal']:.2f}")
        print(f"   Labor: ${cb['labor']['total']:.2f} ({cb['labor']['estimated_hours']}h × ${cb['labor']['hourly_rate']}/h)")
        print(f"   Subtotal: ${cb['subtotal']:.2f}")
        print(f"   Margin ({cb['margin_percentage']}%): ${cb['margin_amount']:.2f}")
        print(f"   Tax ({cb['tax_percentage']}%): ${cb['tax_amount']:.2f}")
        print(f"   ─────────────────────────")
        print(f"   TOTAL: {budget['client_friendly_total']}")
        
        print(f"\n📊 FINANCIAL HEALTH:")
        fh = budget['financial_health']
        print(f"   Effective rate: ${fh['effective_hourly_rate']:.2f}/h")
        print(f"   Margin: {fh['profit_margin_percentage']}%")
        print(f"   Risk: {fh['risk_level']}")
        
        print(f"\n📝 Summary: {steward.get_budget_summary(budget)}")
        
    except Exception as e:
        print(f"\n❌ Budget generation failed: {e}")
        import traceback
        traceback.print_exc()
        budget = None
    
    if budget:
        print("\n" + "="*70)
        print("\n📊 MODE 2: Financial Summary (After Job)")
        print("-" * 70)
        
        try:
            summary = await steward.generate_financial_summary(
                budget=budget,
                actual_parts_cost=30.00,
                actual_hours=0.83,
                amount_charged=budget['cost_breakdown']['total_rounded'],
                client_name="John Smith",
                job_title=budget['budget_metadata']['job_title'],
                extra_costs=[
                    {
                        "item": "Additional O-ring kit",
                        "amount": 2.00,
                        "reason": "Original kit insufficient for complete seal",
                    }
                ],
            )
            
            print("\n✅ Financial summary generated!")
            
            p = summary['profitability']
            print(f"\n💰 PROFITABILITY:")
            print(f"   Revenue: ${p['gross_revenue']:.2f}")
            print(f"   Costs: ${p['direct_costs']:.2f}")
            print(f"   Profit: ${p['gross_profit']:.2f}")
            print(f"   Margin: {p['net_margin_percentage']:.1f}%")
            print(f"   Rate: ${p['effective_hourly_rate']:.2f}/h")
            print(f"   Grade: {p['profitability_grade']}")
            
            pm = summary['performance_metrics']
            print(f"\n📈 SCORE: {pm['overall_score']}/100 ({pm['score_label']})")
            
            if summary.get('celebration_message'):
                print(f"\n🎉 {summary['celebration_message']}")
            
            print(f"\n📝 Summary: {steward.get_summary_highlights(summary)}")
            
        except Exception as e:
            print(f"\n❌ Summary generation failed: {e}")
            import traceback
            traceback.print_exc()
    
    from src.services.qwen_client import get_qwen_client
    client = get_qwen_client()
    cost_summary = client.get_cost_summary()
    print(f"\n💰 Total cost: ${cost_summary['total_cost']:.4f}")
    print(f"   Remaining: ${cost_summary['remaining_budget']:.2f}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    import asyncio
    asyncio.run(_demo())
