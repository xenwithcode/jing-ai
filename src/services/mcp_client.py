"""
MCP Client for testing JING MCP server.

This demonstrates how external systems can interact with JING
through the MCP protocol.
"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.utils.logger import get_logger

logger = get_logger(__name__)


async def test_mcp_server():
    """Test the JING MCP server with various tool calls."""

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.services.mcp_server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("\n" + "=" * 70)
            print("JING MCP Server - Available Tools")
            print("=" * 70)
            for tool in tools.tools:
                print(f"\n  Tool: {tool.name}")
                print(f"   {tool.description[:120]}...")

            print("\n" + "=" * 70)
            print("Testing: jing_list_agents")
            print("=" * 70)
            result = await session.call_tool("jing_list_agents", {})
            data = json.loads(result.content[0].text)
            for agent in data["agents"]:
                print(f"  {agent['name']:20s} | {agent['role']:25s} | {agent['model']}")

            print("\n" + "=" * 70)
            print("Testing: jing_system_status")
            print("=" * 70)
            result = await session.call_tool("jing_system_status", {})
            data = json.loads(result.content[0].text)
            print(f"  Status: {data['status']}")
            print(f"  Budget: ${data['system']['budget']['remaining']:.2f} remaining")
            print(f"  Agents: {len(data['agents'])} registered")

            print("\n" + "=" * 70)
            print("Testing: jing_steward_budget")
            print("=" * 70)
            result = await session.call_tool(
                "jing_steward_budget",
                {
                    "diagnosis": "Moen Chateau 7400 cartridge failure - leaking from handle",
                    "parts": [
                        {
                            "item": "Moen 1225 Cartridge",
                            "quantity": 1,
                            "unit_price": 22.00,
                            "total": 22.00,
                        }
                    ],
                    "estimated_hours": 0.75,
                    "trade": "plumber",
                    "client_name": "Test Client",
                },
            )
            budget = json.loads(result.content[0].text)
            print(f"  Budget Total: {budget['result']['client_friendly_total']}")
            print(f"  Margin: {budget['result']['cost_breakdown']['margin_percentage']}%")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
