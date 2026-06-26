"""Models for JING-KIT logistics results."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class ToolRequired(BaseModel):
    """A tool required for the repair."""

    tool_name: str = Field(..., description="Exact tool name")
    specification: str = Field(..., description="Size/type/caliber")
    purpose: str = Field(..., description="Why this tool is needed")
    procedure_step: Optional[str] = Field(None, description="Which step uses this tool")
    alternative: Optional[str] = Field(None, description="Alternative tool")
    alternative_risk: Optional[str] = Field(None, description="Risk of using alternative")
    is_specialized: bool = Field(False, description="Is this a specialized tool?")


class CompatibleAlternative(BaseModel):
    """Compatible alternative for a part."""

    brand: str
    part_number: str
    quality_comparison: Literal["OEM", "equivalent", "lower", "higher"]


class WhereToBuy(BaseModel):
    """Where to buy a part."""

    store: str = Field(..., description="Store name")
    section: Optional[str] = Field(None, description="Where in the store")
    estimated_price: str = Field(..., description="Price range")
    availability: Literal["in_stock", "special_order", "online_only"]


class PartRequired(BaseModel):
    """A replacement part required."""

    part_name: str
    oem_part_number: Optional[str] = Field(None, description="Manufacturer part number")
    description: str = Field(..., description="What this part does")
    compatible_alternatives: List[CompatibleAlternative] = Field(default_factory=list)
    where_to_buy: List[WhereToBuy] = Field(default_factory=list)
    quantity_needed: Union[str, int] = Field(1, description="Quantity needed")


class Consumable(BaseModel):
    """Consumable item needed."""

    item: str
    specification: Optional[str] = Field(None, description="Type/grade")
    purpose: Optional[str] = Field(None)
    estimated_quantity: str = Field(..., description="How much is needed")


class SafetyEquipment(BaseModel):
    """Safety equipment required."""

    equipment: str
    reason: str = Field(..., description="Why it's needed for this job")
    required: bool = Field(True)


class EstimatedTotalCost(BaseModel):
    """Estimated total cost breakdown."""

    parts: Optional[str] = Field(None, description="Parts price range")
    consumables: Optional[str] = Field(None, description="Consumables price range")
    total: str = Field(..., description="Total estimated cost")


class ShoppingStrategy(BaseModel):
    """Strategy for purchasing parts/tools."""

    recommended_store: str = Field(..., description="Best single store for this job")
    backup_options: List[str] = Field(default_factory=list)
    online_options: List[str] = Field(default_factory=list)


class KitList(BaseModel):
    """Complete kit list from JING-KIT."""

    tools_required: List[ToolRequired] = Field(..., min_length=1)
    parts_required: List[PartRequired] = Field(default_factory=list)
    consumables: List[Consumable] = Field(default_factory=list)
    safety_equipment: List[SafetyEquipment] = Field(default_factory=list)
    estimated_total_cost: EstimatedTotalCost
    shopping_strategy: ShoppingStrategy
    special_notes: List[str] = Field(default_factory=list)
    van_inventory_check: List[str] = Field(default_factory=list)

    def get_specialized_tools(self) -> List[ToolRequired]:
        """Get only specialized tools."""
        return [t for t in self.tools_required if t.is_specialized]

    def get_total_cost_range(self) -> str:
        """Get the total cost as a string."""
        return self.estimated_total_cost.total
