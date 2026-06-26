import asyncio
from src.agents.base_agent import BaseAgent

class TestAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="JING-TEST")

    async def execute(self, task_input):
        response = await self.call_qwen("Say 'Hello from JING!'")
        return {"message": response}

async def main():
    agent = TestAgent()
    result = await agent.execute({})
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
