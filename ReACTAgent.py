import json
import sys
import threading
import asyncio
from agent import PrivEscAgent
from llm import LLMHandler
from tools import PrivEscTools

class ReACTAgent:
    def __init__(self, ip_address, username, password):
        self.llm_handler = LLMHandler()
        self.scratchpad = []
        self.agent = PrivEscAgent(ip_address, username, password)
        self.tools = PrivEscTools()
        self.agent.connect()
        threading.Thread(target=asyncio.run, args=(self.main(),)).start()
        threading.Thread(target=self.interactive_prompt).start()

    async def main(self):
        await self.run_privilege_escalation()

    async def run_privilege_escalation(self):
        print("Starting privilege escalation...")
        initial_commands = ["id", "whoami", "netstat -tuln"]
        for command in initial_commands:
            result = await self.run_tool(command)
            interpretation = self.interpret_result(result['result'])
            print(f"Result:\n{result['result']}")
            print(f"Interpretation:\n{interpretation}")
            if not await self.confirm_proceed():
                return
        while True:
            next_command = await self.get_next_command()
            if next_command:
                result = await self.run_tool(next_command)
                interpretation = self.interpret_result(result['result'])
                print(f"Result:\n{result['result']}")
                print(f"Interpretation:\n{interpretation}")
                if not await self.confirm_proceed():
                    break
            else:
                break

    async def run_tool(self, tool_name):
        if tool_name in ["id", "whoami", "netstat -tuln"]:
            result = self.agent.run_custom_command(tool_name)
            return {"result": result}
        else:
            tool = self.tools.get_tool(tool_name)
            if not tool:
                raise ValueError(f"Tool {tool_name} not found")
            print(f"Running {tool_name}...")
            result = await self.tools.execute_tool(tool_name)
            return result

    def interpret_result(self, result):
        prompt = f"Analyze the following output and provide interpretation:\n{result}"
        response = self.llm_handler.generate_response(prompt)
        if response.startswith("Error:"):
            print(response)
            return "Interpretation not available due to error."
        return response

    async def get_next_command(self):
        prompt = f"Based on the current findings, what should be the next command to run?"
        response = self.llm_handler.generate_response(prompt)
        if response.startswith("Error:"):
            print(response)
            return None
        print(f"Next suggested command: {response}")
        user_response = input("Do you want to proceed with this command? (yes/no/next): ")
        if user_response.lower() == "yes":
            return response
        elif user_response.lower() == "next":
            return "next_command"
        else:
            return None

    async def confirm_proceed(self):
        user_response = input("Do you want to proceed with the next command? (yes/no/next): ")
        return user_response.lower() in ["yes", "next"]

    def interactive_prompt(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            user_input = input("Enter your command or ask a question: ")
            if user_input.lower() == "exit":
                print("Exiting interactive prompt...")
                break
            elif user_input.lower() == "next":
                print("Proceeding to the next command...")
                next_command = loop.run_until_complete(self.get_next_command())
                if next_command:
                    result = loop.run_until_complete(self.run_tool(next_command))
                    print(f"Result:\n{result['result']}")
                    interpretation = self.interpret_result(result['result'])
                    print(f"Interpretation:\n{interpretation}")
            else:
                print(f"You entered: {user_input}")
                if user_input in self.tools.list_tools():
                    result = loop.run_until_complete(self.run_tool(user_input))
                    print(f"Result:\n{result['result']}")
                    interpretation = self.interpret_result(result['result'])
                    print(f"Interpretation:\n{interpretation}")
                else:
                    response = self.llm_handler.generate_response(user_input)
                    if response.startswith("Error:"):
                        print(response)
                    else:
                        print(response)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 ReACTAgent.py <IP_ADDRESS> <USERNAME> <PASSWORD>")
        sys.exit(1)

    ip_address = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    react_agent = ReACTAgent(ip_address, username, password)
