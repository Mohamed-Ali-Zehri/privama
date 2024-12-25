from langchain.prompts import PromptTemplate, ChatPromptTemplate
from pydantic import Field, BaseModel
from llm import LLMHandler  # Adjusted import to align with your setup
from agent import create_agent  # Adjusted import to align with your setup
from tools import PrivEscTools  # Adjusted import to align with your setup

# Load the LLM model
model = LLMHandler()

# Define the tools
tools = [PrivEscTools()]

# Define the prompt for the first agent: "Research the Industry or the Company"
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert market research assistant. "
            "Your task is to research the industry and segment the company is working in. "
            "Identify the company’s key offerings, strategic focus areas (e.g., operations, supply chain, customer experience, etc.). "
            "Respond with a detailed report with all the information gathered. A vision and product information on the industry should be fine as well. "
            "Make sure to use the tavily_search_results_json tool for information.",
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Create the research agent
research_agent = create_agent(model, tools, prompt)

# Invoke the research agent and get the response
response = research_agent.invoke({"input": "This is the company ABC Steel"})
print(type(response["output"]))
print(response)

# Function to simulate interaction and learning
def simulate_interaction():
    print("Welcome to the market research assistant!")
    while True:
        user_input = input("Enter your research query or type 'exit' to quit: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        response = research_agent.invoke({"input": user_input})
        print(f"Response: {response['output']}")
        feedback = input("Did this answer your question? (yes/no) ")
        if feedback.lower() == 'no':
            detailed_feedback = input("Please provide details on what was missing: ")
            # Here you can implement logic to store feedback for learning
            print("Thank you for your feedback. I'll learn from this!")

# Start the interaction simulation
simulate_interaction()
