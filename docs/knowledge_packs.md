
# Creating a Haiven knowledge pack

## Concept
The "secret sauce" to make Haiven work and be useful for your particular team lies in the prompts, and in the knowledge sources. They stay valuable for you regardless of what tool you plug them into.

### What happens when you execute a prompt

Every new chat session in a "plain" AI chatbot application is a new start - the AI doesn't remember that you're working on a software delivery team, what your domain is, your architecture, none of that. You don't want to repeat that every time you interact with the AI. Haiven therefore helps you set the context again and again with reusable context descriptions. This also makes prompts reusable across multiple teams and domains, by switching out those context descriptions.

The most common difference between teams or domains lies in their domain context, and their architecture and tech stack. Those are therefore the context descriptions that are used by most prompts. They reference those pieces of knowledge via the `{business}` and `{architecture}` variables, depending on which domain is activated.

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
{business}
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
+ team_name
    + prompts
        + chat
            - prompt_1.md
        + diagrams
            - prompt_2.md
        + brainstorming
            - prompt_3.md
    + team_1
        + knowledge
            + pdfs
                - pdf_1.kb
                    - index.faiss
                    - index.pkl
                - pdf_1.md
            + documents
                - document_1.kb
                    - index.faiss
                    - index.pkl
                - document_1.md
            - business_context.md
            - architecture.md
            - another_knowledge_snippet.md
```

### 1. Change "business_context" and "architecture" knowledge snippets

The minimum of knowledge you should set up for prompts to work are the static snippets for `business_context.md` and `architecture.md`. These should describe the team's domain context and the team's architecture at a high level, in 2, maybe max 3 paragraphs.

These snippets will be included in every prompt that references them, so they will be a part of the prompt size every time! Therefore you should think about how to concisely describe the business context and architecture, and use the important key words to give the AI good pointers about what you're working on.

You can try and sanity check if the AI "understands" your knowledge by going into a chat conversation (e.g. by using the `/chat` route):

- Paste your knowledge snippet and ask the AI to summarize and elaborate on it in its own words. See if it makes sense. Adjust the snippet accordingly, e.g. add domain terminology explanations, or clarify the role of an architecture component.

- Ask the AI for a simple task in the context of your snippet (e.g. to write a user story or create a domain model with your business context, or to help you with a technical decision with your architecture snippet). See if it makes sense, adjust the snippet accordingly.

### 2. Add your own prompts

#### Pick an interaction pattern

Haiven currently supports 3 different prompt interaction patterns: Chat, diagrams, or brainstorming.

Which interaction pattern to choose depends e.g. on what the user typically has available as input, at what level of detail, or how experienced a user is at a task.

- **Chat**: This is the most straightforward interaction with the AI - you start the user off with a prepared prompt and one piece of input from the user. This is a good choice if you expect that the user usually has a good description of their input ready, or you want to do something that doesn't need detailed input. E.g., a high level version of an artifact that you want to refine with the prompt.

- **Brainstorming**: This interaction pattern is turning the tables, the AI will ask the user questions, instead of the other way around. After a few questions, the AI will then provide an outcome based on the user's answers, and the user can continue the chat conversation if they want. This is a good choice if you want to help the user to fill in gaps, i.e. you want the AI to lead them through what input they need to create to get to their goal. It's also often more useful for users who have little experience with the task at hand, whereas it might be annoying for experts in the task. **!! this interaction pattern works best with models who are good at reasoning, like GPT-4. It might not work at all with some models.**

- **Diagrams**: In this interaction pattern, the user in put is not provided in form of text, but in form of an image. The image is then described by AI, and used as part of the prompt. This is useful if you expect that users have images describing their situation, rather than text. (E.g., an architecture diagram, or a user flow diagram).

#### Define the prompt

Create a markdown file and put it into the respective folder - `prompts/chat`, `prompts/diagrams`, or `prompts/brainstorming`. Use one of the existing prompt files in that folder as an example. This is especially important for the brainstorming prompts, as they have a specific structure that the AI expects.

**Prompt metadata**

Every prompt file has a frontmatter block that defines metadata about the prompt:

- `identifier`: A-unique-identifier (will not be visible to the users, but it helps to be human readable, for logging and debugging purposes)
- `title`: "Title of the prompt that will show up in the UI dropdowns"
- `system`: "System prompt" (optional)
- `categories`: `["category1", "category2"]` // provide a list of task categories where this prompt should show up. Valid values: "analysis", "coding", "testing", "architecture"
- `help_prompt_description`: "Describe to the user what the prompt does"
- `help_user_input`: "Describe for the user what type of input they need to give in order to get the best results from the prompt"

**Prompt content**

Inside of the prompt text, you can reference the static knowledge snippets that are defined in a team's `knowledge` folder. Use the `{business}` and `{architecture}` variables to reference the business context and architecture snippets. Those two are the default knowledge snippets that are used in many of the prepared prompts. But you can add your own if you need to. E.g., you could add an additional snippet for "Frontend coding patterns". You can define the name of the reference variable in the metadata of the knowledge snippet file (see `business_context.md` as an example)

### Add knowledge sources

The previous section only touched on one form of knowledge source, the context description text snippets.

The application also supports retrieval-augmented generation with a more advanced form of knowledge sources. Those can be used in 2 ways:
- Users can ask them questions directly on the **Knowledge Chat** tab
- Users can use them to enhance their chat conversations - e.g., while they are using a prompt to prepare threat modelling, they could ask for additional relevant context from security or compliance documents.

#### Deciding what knowledge sources to use



#### Creating a knowledge source

You will find a utility CLI in the `[./cli](cli)` folder with more documentation.
