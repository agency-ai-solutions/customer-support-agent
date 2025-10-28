from dotenv import load_dotenv
from agency_swarm import Agency

from customer_support_agent import customer_support_agent
from onboarding_config import config

import asyncio
import os

load_dotenv()

def render_shared_instructions():
    """Render shared instructions with config values"""
    shared_instructions_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shared_instructions.md")
    
    with open(shared_instructions_path, "r") as file:
        shared = file.read()
    
    shared = shared.format(
        company_overview=config["company_overview"],
        target_audience=config["target_audience"]
    )
    
    return shared

# do not remove this method, it is used in the main.py file to deploy the agency (it has to be a method)
def create_agency(load_threads_callback=None):
    agency = Agency(
        customer_support_agent,
        communication_flows=[],
        name="CustomerSupportAgency",
        shared_instructions=render_shared_instructions(),
        load_threads_callback=load_threads_callback,
    )

    return agency

if __name__ == "__main__":
    agency = create_agency()

    # test 1 message
    # async def main():
    #     response = await agency.get_response("Hello, how are you?")
    #     print(response)
    # asyncio.run(main())

    # run in terminal
    agency.terminal_demo()
