"""
JING-KIT: The Logistics Specialist

JING-KIT ensures field technicians arrive at every job with EXACTLY the 
right tools and parts. It generates:
- Precise tool lists with specifications
- OEM part numbers and alternatives
- Where to buy (stores, online)
- Cost estimates
- Shopping strategy

This agent runs in PARALLEL with JING-SCRIBE after JING-EYE completes
diagnosis, as both need the same input (brand/model/problem).

Usage:
    >>> from src.agents.kit import KitAgent
    >>> kit = KitAgent()
    >>> result = await kit.generate_kit(
    ...     brand="Moen",
    ...     model="Chateau 7400",
    ...     problem="cartridge failure",
    ...     repair_steps=scribe_result["repair_procedure"]
    ... )
    >>> print(result["parts_required"])
"""

import json
from typing import Any, Dict, List, Optional

from src.agents.base_agent import BaseAgent, AgentExecutionError, AgentValidationError
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class KitAgent(BaseAgent):
    """
    JING-KIT: Logistics specialist for tools and parts.
    
    Generates precise lists of tools and parts based on the diagnosis
    from JING-EYE and the procedure from JING-SCRIBE.
    """
    
    def __init__(self):
        """Initialize JING-KIT with qwen-plus model."""
        super().__init__(name="JING-KIT")
        logger.info("JING-KIT initialized (logistics specialist)")
    
    def _get_default_model(self) -> str:
        """KIT uses qwen-plus (good balance of cost and quality)."""
        return settings.QWEN_PLUS_MODEL
    
    async def generate_kit(
        self,
        brand: str,
        model: str,
        problem: str,
        object_type: Optional[str] = None,
        repair_steps: Optional[List[Dict[str, Any]]] = None,
        eye_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete kit list for the repair.
        
        Args:
            brand: Brand name (e.g., "Moen")
            model: Model number (e.g., "Chateau 7400")
            problem: Description of the problem
            object_type: Type of object (faucet, thermostat, etc.)
            repair_steps: Repair procedure from JING-SCRIBE (optional)
            eye_analysis: Analysis from JING-EYE (optional context)
        
        Returns:
            Structured kit list with tools, parts, consumables, costs
        
        Raises:
            AgentValidationError: If inputs are invalid
            AgentExecutionError: If generation fails
        """
        # ═══════════════════════════════════════════════════════════
        # VALIDATE INPUTS
        # ═══════════════════════════════════════════════════════════
        
        if not brand or not model:
            raise AgentValidationError("Brand and model are required")
        
        if not problem:
            raise AgentValidationError("Problem description is required")
        
        logger.info(f"JING-KIT generating kit for: {brand} {model} - {problem}")
        
        # ═══════════════════════════════════════════════════════════
        # BUILD PROMPT
        # ═══════════════════════════════════════════════════════════
        
        prompt = self._build_kit_prompt(
            brand=brand,
            model=model,
            problem=problem,
            object_type=object_type,
            repair_steps=repair_steps,
            eye_analysis=eye_analysis,
        )
        
        # ═══════════════════════════════════════════════════════════
        # CALL QWEN
        # ═══════════════════════════════════════════════════════════
        
        try:
            response_text = await self.call_qwen(
                user_message=prompt,
                temperature=0.2,  # Low for precise, factual output
                max_tokens=2500,  # Kit lists can be long
            )
        except Exception as e:
            logger.error(f"JING-KIT kit generation failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Kit generation failed: {e}") from e
        
        # ═══════════════════════════════════════════════════════════
        # PARSE AND VALIDATE
        # ═══════════════════════════════════════════════════════════
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JING-KIT returned invalid JSON: {response_text[:200]}...")
            raise AgentExecutionError(f"Invalid JSON from KIT: {e}") from e
        
        validated_result = self._validate_kit(result)
        
        logger.info(
            f"JING-KIT generated kit: "
            f"{len(validated_result['tools_required'])} tools, "
            f"{len(validated_result['parts_required'])} parts, "
            f"total cost: {validated_result['estimated_total_cost']['total']}"
        )
        
        return validated_result
    
    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute method required by BaseAgent. Delegates to generate_kit()."""
        return await self.generate_kit(
            brand=task_input.get("brand", ""),
            model=task_input.get("model", ""),
            problem=task_input.get("problem", ""),
            object_type=task_input.get("object_type"),
            repair_steps=task_input.get("repair_steps"),
            eye_analysis=task_input.get("eye_analysis"),
        )
    
    def _build_kit_prompt(
        self,
        brand: str,
        model: str,
        problem: str,
        object_type: Optional[str],
        repair_steps: Optional[List[Dict[str, Any]]],
        eye_analysis: Optional[Dict[str, Any]],
    ) -> str:
        """Build the prompt for kit generation."""
        parts = ["═══ KIT GENERATION REQUEST ═══\n"]
        
        parts.append(f"🏷️  BRAND: {brand}")
        parts.append(f"📋 MODEL: {model}")
        
        if object_type:
            parts.append(f"🔧 OBJECT TYPE: {object_type}")
        
        parts.append(f"\n⚠️  PROBLEM: {problem}")
        
        if eye_analysis:
            parts.append(f"\n👁️  JING-EYE ANALYSIS:")
            parts.append(f"   Object: {eye_analysis.get('object_identification', {}).get('object', 'N/A')}")
            parts.append(f"   Severity: {eye_analysis.get('overall_severity', 'N/A')}")
            parts.append(f"   Probable cause: {eye_analysis.get('probable_cause', 'N/A')}")
        
        if repair_steps:
            parts.append(f"\n🔧 REPAIR PROCEDURE ({len(repair_steps)} steps):")
            for step in repair_steps[:5]:  # Limit to first 5 steps for brevity
                parts.append(f"   {step.get('step_number', '?')}. {step.get('action', 'N/A')}")
            if len(repair_steps) > 5:
                parts.append(f"   ... and {len(repair_steps) - 5} more steps")
        
        parts.append("\n══════════════════════════════════")
        parts.append("\nGenerate a complete kit list in JSON format.")
        parts.append("Include tools, parts, consumables, costs, and shopping strategy.")
        parts.append("Follow your system prompt framework exactly.")
        parts.append("Remember: Assume standard van inventory. Only list specialized tools.")
        
        return "\n".join(parts)
    
    def _validate_kit(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that the kit has the required structure."""
        # Check top-level keys
        required_keys = ["tools_required", "parts_required", "estimated_total_cost"]
        for key in required_keys:
            if key not in result:
                raise AgentValidationError(f"Kit missing required key: {key}")
        
        # Validate tools_required is a list
        tools = result["tools_required"]
        if not isinstance(tools, list):
            raise AgentValidationError("tools_required must be a list")
        
        # Validate each tool
        for i, tool in enumerate(tools):
            if not isinstance(tool, dict):
                raise AgentValidationError(f"Tool {i} must be a dictionary")
            if "tool_name" not in tool or "specification" not in tool:
                raise AgentValidationError(f"Tool {i} missing tool_name or specification")
        
        # Validate parts_required is a list
        parts = result["parts_required"]
        if not isinstance(parts, list):
            raise AgentValidationError("parts_required must be a list")
        
        # Validate each part
        for i, part in enumerate(parts):
            if not isinstance(part, dict):
                raise AgentValidationError(f"Part {i} must be a dictionary")
            if "part_name" not in part:
                raise AgentValidationError(f"Part {i} missing part_name")
        
        # Validate estimated_total_cost
        cost = result["estimated_total_cost"]
        if not isinstance(cost, dict):
            raise AgentValidationError("estimated_total_cost must be a dictionary")
        
        if "total" not in cost:
            raise AgentValidationError("estimated_total_cost missing 'total'")
        
        # Ensure optional fields exist with defaults
        if "consumables" not in result:
            result["consumables"] = []
        
        if "safety_equipment" not in result:
            result["safety_equipment"] = []
        
        if "shopping_strategy" not in result:
            result["shopping_strategy"] = {
                "recommended_store": "Home Depot or Lowe's",
                "backup_options": [],
                "online_options": []
            }
        
        if "special_notes" not in result:
            result["special_notes"] = []
        
        if "van_inventory_check" not in result:
            result["van_inventory_check"] = []
        
        logger.debug("Kit validated successfully")
        
        return result
    
    def get_summary(self, kit: Dict[str, Any]) -> str:
        """Get a human-readable summary of the kit."""
        summary_parts = []
        
        summary_parts.append(f"Tools: {len(kit['tools_required'])}")
        summary_parts.append(f"Parts: {len(kit['parts_required'])}")
        summary_parts.append(f"Consumables: {len(kit['consumables'])}")
        
        total_cost = kit.get("estimated_total_cost", {}).get("total", "Unknown")
        summary_parts.append(f"Total cost: {total_cost}")
        
        if kit.get("shopping_strategy", {}).get("recommended_store"):
            summary_parts.append(f"Shop at: {kit['shopping_strategy']['recommended_store']}")
        
        return " | ".join(summary_parts)
    
    def format_shopping_list(self, kit: Dict[str, Any]) -> str:
        """
        Format the kit as a simple shopping list for the technician.
        
        Returns a plain text list that can be printed or sent via SMS.
        """
        lines = ["═══ JING SHOPPING LIST ═══\n"]
        
        # Parts
        if kit["parts_required"]:
            lines.append("📦 PARTS TO BUY:")
            for part in kit["parts_required"]:
                oem = part.get("oem_part_number", "N/A")
                lines.append(f"  • {part['part_name']} (P/N: {oem})")
                
                # Show first store option
                if part.get("where_to_buy"):
                    store = part["where_to_buy"][0]
                    lines.append(f"    → {store['store']}: {store['estimated_price']}")
            lines.append("")
        
        # Tools (only specialized ones)
        specialized_tools = [t for t in kit["tools_required"] if t.get("is_specialized")]
        if specialized_tools:
            lines.append("🔧 SPECIALIZED TOOLS:")
            for tool in specialized_tools:
                lines.append(f"  • {tool['tool_name']} ({tool['specification']})")
            lines.append("")
        
        # Consumables
        if kit["consumables"]:
            lines.append("📋 CONSUMABLES:")
            for item in kit["consumables"]:
                lines.append(f"  • {item['item']} ({item.get('specification', 'standard')})")
            lines.append("")
        
        # Total cost
        total = kit.get("estimated_total_cost", {}).get("total", "Unknown")
        lines.append(f"💰 ESTIMATED TOTAL: {total}")
        
        # Shopping strategy
        if kit.get("shopping_strategy", {}).get("recommended_store"):
            lines.append(f"\n🏪 SHOP AT: {kit['shopping_strategy']['recommended_store']}")
        
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# DEMO / TEST
# ═══════════════════════════════════════════════════════════════

async def _demo():
    """Demo JING-KIT with a realistic scenario."""
    kit_agent = KitAgent()
    
    print("\n" + "="*70)
    print("JING-KIT Logistics Demo")
    print("="*70)
    
    print("\n📋 Scenario: Moen Chateau 7400 faucet with cartridge failure")
    
    try:
        result = await kit_agent.generate_kit(
            brand="Moen",
            model="Chateau 7400",
            problem="cartridge failure causing drip from spout",
            object_type="kitchen faucet",
            repair_steps=[
                {"step_number": 1, "action": "Shut off water supply"},
                {"step_number": 2, "action": "Remove handle (Allen 3/32 screw)"},
                {"step_number": 3, "action": "Remove retaining clip"},
                {"step_number": 4, "action": "Extract old cartridge"},
                {"step_number": 5, "action": "Install new Moen 1225 cartridge"},
                {"step_number": 6, "action": "Reassemble and test"},
            ],
            eye_analysis={
                "object_identification": {
                    "object": "Kitchen faucet",
                    "brand": "Moen",
                    "model": "Chateau 7400"
                },
                "overall_severity": "moderate",
                "probable_cause": "Worn cartridge allowing water to bypass valve seal"
            }
        )
        
        print("\n✅ Kit generated successfully!")
        
        # Display results
        print(f"\n🔧 Tools Required ({len(result['tools_required'])}):")
        for tool in result["tools_required"]:
            specialized = " [SPECIALIZED]" if tool.get("is_specialized") else ""
            print(f"   • {tool['tool_name']} ({tool['specification']}){specialized}")
            print(f"     Purpose: {tool['purpose']}")
            if tool.get("alternative"):
                print(f"     Alternative: {tool['alternative']}")
        
        print(f"\n📦 Parts Required ({len(result['parts_required'])}):")
        for part in result["parts_required"]:
            print(f"   • {part['part_name']}")
            print(f"     OEM P/N: {part.get('oem_part_number', 'N/A')}")
            
            if part.get("compatible_alternatives"):
                print(f"     Alternatives:")
                for alt in part["compatible_alternatives"]:
                    print(f"       - {alt['brand']} {alt['part_number']} ({alt['quality_comparison']})")
            
            if part.get("where_to_buy"):
                print(f"     Where to buy:")
                for store in part["where_to_buy"][:2]:  # Show first 2 options
                    print(f"       - {store['store']}: {store['estimated_price']} ({store['availability']})")
        
        if result["consumables"]:
            print(f"\n📋 Consumables:")
            for item in result["consumables"]:
                print(f"   • {item['item']} ({item.get('specification', 'standard')})")
        
        if result["safety_equipment"]:
            print(f"\n🦺 Safety Equipment:")
            for equip in result["safety_equipment"]:
                required = "REQUIRED" if equip.get("required") else "recommended"
                print(f"   • {equip['equipment']} ({required}): {equip['reason']}")
        
        print(f"\n💰 Estimated Total Cost:")
        cost = result["estimated_total_cost"]
        print(f"   Parts: {cost.get('parts', 'N/A')}")
        print(f"   Consumables: {cost.get('consumables', 'N/A')}")
        print(f"   TOTAL: {cost.get('total', 'N/A')}")
        
        if result.get("shopping_strategy"):
            print(f"\n🏪 Shopping Strategy:")
            print(f"   Recommended: {result['shopping_strategy'].get('recommended_store', 'N/A')}")
            if result["shopping_strategy"].get("backup_options"):
                print(f"   Backup: {', '.join(result['shopping_strategy']['backup_options'])}")
        
        if result["special_notes"]:
            print(f"\n📝 Special Notes:")
            for note in result["special_notes"]:
                print(f"   • {note}")
        
        if result["van_inventory_check"]:
            print(f"\n✅ Van Inventory Check:")
            for check in result["van_inventory_check"]:
                print(f"   □ {check}")
        
        # Show shopping list format
        print(f"\n{'='*70}")
        print("SIMPLE SHOPPING LIST (for SMS/print):")
        print("="*70)
        print(kit_agent.format_shopping_list(result))
        
        # Show summary
        print(f"\n📋 Summary: {kit_agent.get_summary(result)}")
        
        # Show cost
        from src.services.qwen_client import get_qwen_client
        client = get_qwen_client()
        summary = client.get_cost_summary()
        print(f"\n💰 Cost of this kit generation: ${summary['total_cost']:.4f}")
        print(f"   Remaining budget: ${summary['remaining_budget']:.2f}")
        
    except Exception as e:
        print(f"\n❌ Kit generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    import asyncio
    asyncio.run(_demo())
