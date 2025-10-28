from agents import ModelSettings
from agency_swarm import Agent
from agency_swarm.tools import ToolFactory
from openai.types.shared import Reasoning
import os
from dotenv import load_dotenv

load_dotenv()

# Import onboarding configuration
try:
    from onboarding_config import config
except ImportError:
    raise ImportError(
        "Onboarding configuration not found. Please run 'python onboarding_tool.py' "
        "to generate the configuration file before using this agent."
    )

current_dir = os.path.dirname(os.path.abspath(__file__))
instructions_path = os.path.join(current_dir, "instructions.md")

def render_instructions():
    """Render instructions with config values"""
    with open(instructions_path, "r") as file:
        instructions = file.read()
    
    # Format instructions with config values
    instructions = instructions.format(
        agent_name=config["agent_name"],
        company_name=config["company_name"],
        output_format=config["output_format"],
        support_contact=config.get("support_contact") or "the support team",
        additional_context=config.get("additional_context") or ""
    )
    
    return instructions

def load_openapi_tools():
    """Load OpenAPI schema from config and convert to tools with Bearer authentication"""
    tools = []
    
    # Get schema from config
    schema_content = config.get("openapi_schema")
    if not schema_content:
        return tools
    
    # Clean the schema content (strip whitespace)
    schema_content = schema_content.strip()
    
    # Get API key from environment
    api_key = os.getenv("CUSTOMER_SUPPORT_API_KEY")
    
    try:
        # Prepare headers with Bearer authentication if API key is available
        headers = None
        if api_key:
            headers = {'Authorization': f'Bearer {api_key}'}
        
        # Convert schema to tools using ToolFactory
        schema_tools = ToolFactory.from_openapi_schema(
            schema_content,
            headers=headers,
            strict=False
        )
        
        tools.extend(schema_tools)
        
    except Exception as e:
        print(f"Warning: Failed to load OpenAPI schema: {str(e)}")
    
    return tools

# Load OpenAPI tools
openapi_tools = load_openapi_tools()

# Build agent parameters
customer_support_agent = Agent(
    name=config["agent_name"],
    description=config["agent_description"],
    instructions=render_instructions(),
    tools_folder="./tools",
    files_folder="./files",
    model="gpt-5",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            effort="low",
            summary="auto",
        ),
    ),
    tools=openapi_tools if openapi_tools else []
)

