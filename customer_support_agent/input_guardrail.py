from agents import input_guardrail, RunContextWrapper, GuardrailFunctionOutput, Runner, ModelSettings
from agency_swarm import Agent
from openai.types.shared import Reasoning
from pydantic import BaseModel
import os

# Get config for company context
try:
    from onboarding_config import config
except ImportError:
    config = {}

# Define output type for the guardrail agent
class RelevanceCheckOutput(BaseModel):
    is_relevant: bool
    reasoning: str

# Get company context
company_name = config.get("company_name", "the company")
company_overview = config.get("company_overview", "")

# Determine model based on user selection
selected_model = config.get("model", "gpt-5")
guardrail_model = "gpt-5-nano" if selected_model == "gpt-5" else "gpt-4o-mini"

# Build guardrail agent parameters
guardrail_params = {
    "name": "Relevance Checker",
    "instructions": f"""You are a content relevance classifier for {company_name}.

Company Overview: {company_overview}

Your task is to determine if a user's question is relevant to customer support for {company_name}.

IMPORTANT RULES:
1. Only classify as IRRELEVANT (is_relevant: false) if the question is CLEARLY about something completely unrelated (e.g., "help me write an essay", "what's the weather", "solve this math problem", "who is the president of the United States")
2. Classify as RELEVANT (is_relevant: true) if:
   - It's about the company, products, or services
   - It's a follow-up question (e.g., "can you explain more?", "what do you mean?")
   - It's ambiguous or you're not sure
   - It could possibly be related to customer support
3. When in doubt, classify as RELEVANT (is_relevant: true)

Provide your classification with brief reasoning.""",
    "output_type": RelevanceCheckOutput,
    "model": guardrail_model,
}

# Add reasoning for gpt-5-nano
if selected_model == "gpt-5":
    guardrail_params["model_settings"] = ModelSettings(
        reasoning=Reasoning(
            effort="low",
            summary="auto",
        ),
    )

# Create guardrail agent with structured output
guardrail_agent = Agent(**guardrail_params)

@input_guardrail
async def relevance_guardrail(
    context: RunContextWrapper, 
    agent: Agent, 
    user_input: str | list[str]
) -> GuardrailFunctionOutput:
    """
    Validates that user input is relevant to customer support for the company.
    Only triggers if the question is clearly irrelevant to customer support.
    Does not trigger for follow-up questions or ambiguous queries.
    """
    
    try:
        # Run the guardrail agent to classify the input
        result = await Runner.run(guardrail_agent, user_input, context=context.context)
        
        # Check if the input is irrelevant
        if not result.final_output.is_relevant:
            return GuardrailFunctionOutput(
                output_info=f"I'm a customer support agent for {company_name}. I can only help with questions related to our products and services. Please ask a question related to {company_name}.",
                tripwire_triggered=True,
            )
        
        # Input is relevant, allow it through
        return GuardrailFunctionOutput(
            output_info="",
            tripwire_triggered=False,
        )
        
    except Exception as e:
        # If classification fails, allow the message through (fail open)
        print(f"Warning: Guardrail classification failed: {str(e)}")
        return GuardrailFunctionOutput(
            output_info="",
            tripwire_triggered=False,
        )

