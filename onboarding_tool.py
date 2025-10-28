from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from typing import Literal, Optional

load_dotenv()

class OnboardingTool(BaseTool):
    """
    Customizes the customer support agent based on your business requirements,
    response format preferences, and company-specific information before deployment.
    """
    
    # Agent Identity
    agent_name: str = Field(
        "Alex",
        description="Name of your customer support agent (e.g., 'Alex', 'Support Bot', 'Customer Care Agent')."
    )
    
    agent_description: str = Field(
        "Handles customer inquiries, provides assistance, and ensures excellent customer service.",
        description="Brief description of what your agent does. This will be shown to users."
    )

    # Business Context
    company_name: str = Field(
        "Agencii AI",
        description="Your company or product name."
    )
    
    company_overview: str = Field(
        "Agencii AI is a platform for building reliable AI agents on top of the OpenAI API. Users can create valuable solutions for their own or their clients' businesses.",
        description="Brief overview of your company, product, or service. This helps the agent understand what you do.",
        json_schema_extra={
            "ui:widget": "textarea",
        },
    )
    
    target_audience: str = Field(
        "Users who want to build AI agents for their own or their clients' businesses, developers, entrepreneurs, and businesses looking to automate with AI.",
        description="Who are your typical customers? This helps the agent understand user needs.",
        json_schema_extra={
            "ui:widget": "textarea",
        },
    )
    
    # Response Format Customization
    output_format: str = Field(
        "Provide clear, well-structured responses. Use the selected response structure and style. Include relevant examples when helpful.",
        description="Specific output format instructions for how the agent should structure its responses.",
        json_schema_extra={
            "ui:widget": "textarea",
        },
    )
    
    # Support Configuration
    support_contact: Optional[str] = Field(
        None,
        description="Support email, phone number, or contact information for escalations (optional)."
    )
    
    # Additional Knowledge
    additional_context: Optional[str] = Field(
        None,
        description="Any additional business context, policies, or information the agent should know.",
        json_schema_extra={
            "ui:widget": "textarea",
        },
    )
    
    # Knowledge Base Files
    knowledge_files: list[str] = Field(
        [],
        description="Upload FAQs, SOPs, product documentation, or other files the agent should reference.",
        json_schema_extra={
            "x-file-upload-path": "./customer_support_agent/files",
        },
    )
    
    # OpenAPI Schema for Support API
    openapi_schema: Optional[str] = Field(
        None,
        description="Paste your OpenAPI schema (JSON or YAML format) for creating support requests via API.",
        json_schema_extra={
            "ui:widget": "textarea",
        },
    )

    def run(self):
        """
        Saves the configuration as a Python file with a config object
        """
        import json

        tool_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(tool_dir, "onboarding_config.py")

        config = self.model_dump()

        try:
            # Generate Python code with the config as a dictionary
            # Convert JSON null to Python None
            json_str = json.dumps(config, indent=4)
            json_str = json_str.replace(': null', ': None').replace(': true', ': True').replace(': false', ': False')
            python_code = f"# Auto-generated onboarding configuration\n\nconfig = {json_str}\n"
            
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(python_code)
            return f"Configuration saved at: {config_path}\n\nYou can now import it with:\nfrom onboarding_config import config"
        except Exception as e:
            return f"Error writing config file: {str(e)}"

if __name__ == "__main__":
    # Test with default values
    tool = OnboardingTool(
        agent_name="Alex",
        agent_description="Handles customer inquiries, provides assistance, and ensures excellent customer service.",
        output_format="Provide clear, well-structured responses. Use the selected response structure and style. Include relevant examples when helpful.",
        company_name="Agencii AI",
        company_overview="Agencii AI is a platform for building reliable AI agents on top of the OpenAI API. Users can create valuable solutions for their own or their clients' businesses.",
        target_audience="Users who want to build AI agents for their own or their clients' businesses, developers, entrepreneurs, and businesses looking to automate with AI.",
        knowledge_files=[]
    )
    print(tool.run())

