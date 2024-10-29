# ADR 4: Improve structured output (JSON) parsing reliability without framework help

(Written with the help of a Haiven prompt and Anthropic's Claude)

## Decision Summary
We will improve the structured JSON output responses and parsing of those responses with some small adjustments ourselves rather than adopting a structured output framework like Instructor or Guidance AI.

## Context
- Some of our features require reliable JSON responses from LLM models, to show the responses in a structured way on the UI (e.g. our scenario cards)
- Current implementation experiences occasional failures when models return JSON with additional text (e.g., "Here is your JSON: ..." or markdown code blocks). This has so far even prevented us from switching to gpt-4o.
- Local models often don't even return any JSON.
- We are currently using Langchain's `BaseChatModel` as an AI API client SDK
- Streaming capability is critical for the user experience, so the application needs to handle partial JSON responses in the frontend to show progressive updates

### Business Impact
- Unreliable JSON parsing leads to failed requests and poor user experience.
- This is limiting the number of models we can support
- Any solution needs to maintain the current streaming capabilities which are important for user engagement

## Options Considered

### Option 1: Do Nothing

#### Consequences
✅ Pros:
- No development effort required
- Current system works most of the time

❌ Cons:
- Continued occasional failures
- Cannot move to gpt-4o as it seems to do the wrapping thing a lot
- Poor user experience when failures occur

### Option 2: Adopt Instructor


#### Consequences

✅ Pros:
- More structured approach to response handling
- Built-in retry mechanisms might even make local models more usable
- Type safety with response validation

❌ Cons:
- Requires refactoring of existing code (wraps itself around the client SDK, and we call that in multiple places at the moment)
- Documentation doesn't seem very comprehensive, especially for streaming
- [Puzzle] Is a framework TOO strict for what we want to do? They require creating pydantic objects for each response type, would that increase our implementation efforts whenever we introduce new prompt types?
- As part of our spike we were unsure how to best forward the streamed JSON to the frontend, when we would have the new intermediate step of the partial objects
- Additional dependency to maintain
- Retry mechanism does not (and cannot) work with streaming

### Option 3: Implement some small custom improvements (Chosen)
- Look for expected starting characters ([, {) in responses before starting the stream to the frontend -> Strip any preceding text
- Improve our prompts with some additional instructions about leaving out wrapping text, etc

#### Consequences
✅ Pros:
- Minimal code changes required (and we have some previous code from another project)
- Maintains full control over the implementation
- Can be tailored to our specific needs
- No additional dependencies
- Works with existing streaming setup

❌ Cons:
- Need to maintain our own parsing logic
- May need ongoing adjustments as model behaviors change, could become a bottomless chore
- No additional benefits like retries (though retries cannot work in combination with streaming, so no framework would help us with that anyway)
- Might still not be a good enough solution for local models
