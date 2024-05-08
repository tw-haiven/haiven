# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from fastapi import Request
from fastapi.responses import StreamingResponse

from shared.llm_config import LLMConfig
from shared.chats import JSONChat


def get_threat_modelling_prompt(dataFlow, assets, userBase):
    return f"""
You are a member of a software engineering team.

# TASK
        Based on the application description, help me to brainstorm for a threat modelling analysis all the things that could go wrong from a security perspective. Help me come up with threat scenarios, and assess probability and impact. Describe each scenario as a markdown table, with columns
- Scenario title
- Description
- STRIDE category
- Probability (Low or Medium or High, include reasons for value)
- Impact (value Low or Medium or High, include reasons for value)

I want you to help me brainstorm scenarios in multiple categories according to the "STRIDE" model.
- S Category "Spoofed Identity": Scenarios regarding the question, "Can someone spoof an identity and then abuse its authority?" based on my application description.
- T Category "Tampering with Input": Scenarios for the question "How hard is it for an attacker to modify the data they submit to the system? Can they break a trust boundary and modify the code which runs as part of your system?"
- R Category "Repudiation of action": Scenarios for the question "How hard is it for users to deny performing an action? What evidence does the system collect to help you to prove otherwise?" Non-repudiation refers to the ability of a system to ensure people are accountable for their actions.
- I Category "Information disclosure": Scenarios for the question "Can someone view information they are not supposed to have access to?" Information disclosure threats involve the exposure or interception of information to unauthorised individuals.
- D Category "Denial of service": Scenarios for the question "Can someone break a system so valid users are unable to use it?" Denial of service attacks work by flooding, wiping or otherwise breaking a particular service or system.
- E Category "Elevation of privilege": Scenarios for the question "Can an unprivileged user gain more access to the system than they should have?" Elevation of privilege attacks are possible because authorisation boundaries are missing or inadequate.

# CONTEXT
Here is my input that describes my application:

Users using the application - consider this when you assess the probability and impact: 
=> {userBase}

Assets I want to protect - consider this in particular when you assess the impact of a scenario:
=> {assets}

How data flows through the application: 
=> {dataFlow}

# INSTRUCTIONS
You will create at least one scenario for each category. Give me at least 10 scenarios.

You will respond with only a valid JSON array of scenario objects. Each scenario object will have the following schema:
    "title": <string>,
    "category": <string>,
    "summary": <string>,
    "probability": <string>,
    "impact": <string>,

Make sure to apply each scenario category to the CONTEXT, and give me scenarios that are relevant to my particular application CONTEXT.

    
    """


def enable_threat_modelling(app):
    @app.get("/api/threat-modelling")
    def threat_modelling(request: Request):
        dataFlow = request.query_params.get("dataFlow")
        assets = request.query_params.get("assets")
        userBase = request.query_params.get("userBase")

        json_chat = JSONChat(LLMConfig("mock", 0.5))
        return StreamingResponse(
            json_chat.run(get_threat_modelling_prompt(dataFlow, assets, userBase)),
            media_type="text/event-stream",
            headers={
                "Connection": "keep-alive",
                "Content-Encoding": "none",  # Necessary for the stream to work across the Next rewrite
            },
        )
