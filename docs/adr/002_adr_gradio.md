# ADR 2: Use Gradio as UI framework

## Context

We need a framework to implement the user interface.

Our requirements:

- A simple, but user-friendly UI
- Ability to customise the style a bit in a way that it looks professional (for Marketing reasons)
- Adding more UI should be possible with relatively low effort
  - This should be a tool for teams, not their half-time job to implement fancy UI when they want to extend it
  - Adding UI is easy to learn for people who do not know the framework
- Easy to integrate with LLM services
- Good support for chat conversations in the style of GenAI-powered chatbots
- OAuth integration for authentication
- Low number of concurrent users (if we expect this to be used either in demo contexts, or by a small number of teams)
- Ability to deploy it as a web application to different deployment targets (Google Cloud Run, etc)

History:

The codebase was originally copied from a team who was hosting it on Huggingface. Huggingface has integration for Gradio, so it was the obvious choice. As the application is progressing from an experimentation and demo context to a "can we package this as an accelerator and give it to clients" use case, we needed to revisit the UI decision and see if Gradio is flexible enough for that new context.

Options:

1. Stick with Gradio - built as a UI framework to easily experiment and prototype in the AI/ML space. Python, Svelte under the hood. Quick to get things done, but some limits in customisation and "fancy" UI features.
2. Streamlit - also built in Python, also meant for lightweight experimentation; but when attempting to migrate parts of the Gradio to Streamlit to get a feeling for what's different, there didn't seem to be many obvious advantages over Gradio, and we would have had to figure out again how to do OAuth integration etc etc. Also, deployment documentation seemed very focussed on deploying this to the Streamlit PaaS, whereas we want to be independent of the deployment target and just treat it is a web application. Therefore not sure if it's worth the effort. TODO: Check in with GPT Wizards about their experience with Streamlit.
3. React

## Decision

Option 1. Use Gradio

## Consequences

- Easy to extend with new UI elements
- Great integration with all things machine learning, including LLMs
- Sufficient level of style customisation is possible
- Can be hooked into FastAPI and then be treated and deployed like any FastAPI web application, including OAuth integration etc
- Certain level of control and access to request and session objects is possible, but limited
- LLM integration is excellently supported in the Python ecosystem, so it is an advantage to use a Python-based framework.

Trade-offs:

- It is NOT optimised for fancy UIs, and does not offer a lot of configuration and control options that we might be used to from other web application stacks
- We expect fewer people in the target audience to be familiar with Python than people who are familiar with JavaScript and React, so there might be a bit of a barrier for customisation. However, with an existing codebase to start from, this trade-off is accepted for now.
- Gradio uses Svelte under the hood and is mostly server-side-rendered. Therefore there are not a lot of options to keep state of chat conversations in the frontend, and we need to store some session state on the server side, which complicates the infrastructure setup a bit.