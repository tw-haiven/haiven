### Interaction mode: Agent Chat

This interaction mode uses AWS Bedrock Agent Chat to provide a conversational interface to the user. The user can ask questions and the agent will respond with answers. The agent uses knowledge bases created from set of documents.

**Benefits:**
- Ease of doing RAG : The agent provides a easy to use inteface for RAG based interactions with custom knowledge bases.
- Scalable: AWS Bedrock Knowledge Bases make it easy to use custom data sources to create knowledge bases for agents. Adding new files and syncing the knowledge base is easy and does not require redoplyment or code change. Additionally these knowledge bases are powered by powerful vector databases which are scalable.
- Customization: Agents can benifit from many featues like Actions, Guardrails and fine-tuned prompts to provide a more customized experience to the user.

**Risks and caveats:**
- Infrastructure: Currently only works with AWS. A knowdge base needs to be created in AWS Bedrock before using this interaction mode. There is cost attached to creating and mainting the knowledge base in AWS.
- Data privacy: The data used to create the knowledge base is stored in AWS. The data is not shared with any third party but is stored in AWS.

**How to use:**
- Make sure to create a knowledge base in AWS Bedrock in the same region as other foundational models.
- Create aleast one agent in AWS Bedrock and add the knowledge base to the agent.
- Ensure that account that runs the app has `read` and `invoke_agent` permissions on the agents.
- For every agent there needs to be a `PREPARED` alias in AWS.
- The app single alias per agent.
- Multiple agent and agent alias pairs are allowed.
- The agentIds are stored as comma seperated values in the enviornment variable `ENABLED_AGENT_IDS`.
- The corresponding agentAliasIds are also stored as CSV (in same sequence) in the enviornment variable `ENABLED_AGENT_ALIAS_IDS`.