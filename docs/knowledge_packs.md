
# Creating a Haiven knowledge pack

## Concept
The "secret sauce" to make Haiven work and be useful for your particular team lies in the prompts, and in the knowledge sources. They stay valuable for you regardless of what tool you plug them into.

### What happens when you execute a prompt

Every new chat session in a "plain" AI chatbot application is a new start - the AI doesn't remember that you're working on a software delivery team, what your domain is, your architecture, none of that. You don't want to repeat that every time you interact with the AI. Haiven therefore helps you set the context again and again with reusable context descriptions. This also makes prompts reusable across multiple teams and domains, by switching out those context descriptions.

The most common difference between teams or domains lies in their domain context, and their architecture and tech stack. Those are therefore the context descriptions that are used by most prompts. They reference those pieces of knowledge via the `{domain}` and `{architecture}` variables, depending on which domain is activated.

```mermaid
graph LR
    F[Team 1] --> D[Business Context]
    F[Team 1] --> E[Architecture and Tech Stack]
    G[Team 2] --> D
    G[Team 2] --> E
    D --> C[Prompts]
    E --> C
    C --> B[AI]
```

**Example**

Here is a simplified example of a prompt:
```
I am a team member in a software delivery team. Some context about the application we are building:

-----
CONTEXT DESCRIPTION:
{domain}
-----

... [ additional {user_input} etc, left out to keep the example short ] ...

With the context and my input, help me break this user flow down into user stories that can be implemented step by step by a delivery team.

```

With this approach, you can provide high level context to each prompt with a static, reusable text snippet, but then let the user provide the specific input for the task at hand in the UI.

```mermaid
graph TB
    subgraph Prompt[<b>Prompt</b>]
        
        BC[<b>Business Context</b>
        'We are building the basket functionality 
        of an ecommerce system.']
        
        UI[<b>User Input</b>
        'Here is what I know so far about 
        this user story: ...']
    end
    
```


## How to set up your "knowledge pack"

### Folder structure
Each team's knowledge pack needs to have the following folder structure:

```
+ knowledge-pack
    + prompts
        - system.md  <-- Global system message configuration
        + chat
            - prompt_1.md
            - prompt_2.md
            - prompt_3.md
    + contexts
        + team_1
            + embeddings
                - pdf_1.kb
                    - index.faiss
                    - index.pkl
                - pdf_1.md
                - document_1.kb
                    - index.faiss
                    - index.pkl
                - document_1.md
            - domain.md
            - architecture.md
            - another_knowledge_snippet.md
        + context_2
            + embeddings
                ...
            domain.md
            architecture.md
            ...
            
```

### 1. Configure the global system message (optional)

You can customize the global system message that's used for all chat interactions by creating a `system.md` file in the `prompts` directory of your knowledge pack. This system message sets the overall behavior and capabilities of the AI assistant.

If no `system.md` file is found, Haiven will use the default system message: "You are a helpful assistant powered by AI."

The system message is a critical component that shapes how the AI responds to all queries, so consider carefully what information and instructions to include. Good system messages typically include:

- The assistant's role and purpose
- Domain-specific knowledge or context
- Constraints or guidelines for responses
- Tone and style preferences

**Example system.md file:**
```
You are an AI assistant specialized in software development for e-commerce applications. 
You have expertise in React, Node.js, and microservices architecture.
When providing code examples, always include explanatory comments.
Focus on security best practices when discussing authentication or payment processing.
Maintain a professional but friendly tone in all responses.
```

### 2. Add and change contexts

The minimum of knowledge you should set up for prompts to work are the static context snippets for `domain.md` and `architecture.md`. These should describe the team's domain context and the team's architecture at a high level, in 2, maybe max 3 paragraphs.

These snippets will be included in every prompt that references them, so they will be a part of the prompt size every time! Therefore you should think about how to concisely describe the business context and architecture, and use the important key words to give the AI good pointers about what you're working on.

You can try and sanity check if the AI "understands" your knowledge by going into a chat conversation (e.g. by using the `/chat` route):

- Paste your knowledge snippet and ask the AI to summarize and elaborate on it in its own words. See if it makes sense. Adjust the snippet accordingly, e.g. add domain terminology explanations, or clarify the role of an architecture component.

- Ask the AI for a simple task in the context of your snippet (e.g. to write a user story or create a domain model with your business context, or to help you with a technical decision with your architecture snippet). See if it makes sense, adjust the snippet accordingly.

### 3. Add your own prompts

Create a markdown file and put it into the `prompts/chat` folder. Use one of the existing prompt files in that folder as an example to define the metadata. The new prompt will automatically be loaded into the sidebar menu and the dashboard.

**Prompt metadata**

Every prompt file has a frontmatter block that defines metadata about the prompt:

- `identifier`: A-unique-identifier (will not be visible to the users, but it helps to be human readable, for logging and debugging purposes)
- `title`: "Title of the prompt that will show up in the UI dropdowns"
- `system`: "System prompt" (optional)
- `categories`: `["category1", "category2"]` // provide a list of task categories where this prompt should show up. Valid values: "analysis", "coding", "testing", "architecture"
- `help_prompt_description`: "Describe to the user what the prompt does"
- `help_user_input`: "Describe for the user what type of input they need to give in order to get the best results from the prompt"
- `help_sample_input`: "Provide an example of what the user input could look like"

**Prompt content**

Inside of the prompt text, you can reference the static knowledge snippets that are defined in a team's `knowledge` folder. Use the `{domain}` and `{architecture}` variables to reference the business context and architecture snippets. Those two are the default knowledge snippets that are used in many of the prepared prompts. But you can add your own if you need to. E.g., you could add an additional snippet for "Frontend coding patterns". You can define the name of the reference variable in the metadata of the knowledge snippet file (see `domain.md` as an example)

**Writing "cards" prompts**

When you set the prompt metadata to `type: "cards"`, it will result in a "cards" interaction in the UI, so the results will be shown as separate cards. This requires that the prompt returns JSON, so you need to put those explicit instructions at the end of the prompt.

!! Note that the templating mechanism for the prompts treats `{` and `}` as special characters, so when you provide JSON examples, be sure to use `{{` and `}}`.

Here are a few conventions the UI can react to:
- `title` - will be displayed as the card title
- `summary` - will be displayed as the first text on the card
- other properties - will be dynamically rendered in "label: value" format after the `summary`
- `self-review` - if you instruct in the prompt to do a review of each of the returned results, the UI can show it as a review status on the cards. The code expects ✅ or 🤔 at the beginning of each `self-review` text value, to decide how to display it
- `hidden` - sometimes you want AI to "think through" something without showing those steps to the user. E.g., when you write a prompt that should ask the user questions, a common Chain-of-Thought pattern is to prompt the model to think about what they don't know, and THEN create the question. You can have it generate those into a property called `hidden`, which will not be displayed, but still contributes to the quality of the model's answer, just by generating it.

Example structure of a cards prompt:

```
## TASK
...

## CONTEXT
...
{user_input}
...

## INSTRUCTIONS
...

You will respond with only a valid JSON array of [...]. Each [...] will have the following schema:

{{
    "title": "...",
    "summary": "...",
    "self-review": "...",
}}
```

### 4. Add documents

The previous section only touched on one form of knowledge source, the context description text snippets.

The application also supports retrieval-augmented generation with a more advanced form of knowledge sources. Those can be used in 2 ways:
- Users can ask them questions directly on the **Chat with Haiven** section
- Users can use them to enhance their conversations - e.g., while they are using a prompt to prepare threat modelling, they could ask for additional relevant context from security or compliance documents.

#### Creating a knowledge source

You will find a utility CLI in the `[./cli](cli)` folder with more documentation.

The new documents will be accessible to the user in the "Documents" dropdowns in the application.
