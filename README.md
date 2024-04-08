# Team AI (TODO: Rename)

"Team AI" is an accelerator we use to pilot the use of Generative AI assistance for software delivery tasks beyond coding. 

This codebase provides the scaffolding to build a one-container web application that can act as an assistant to a software delivery team. You can plug in your own "knowledge pack", adapted to your organisation's and teams' needs.

![Overview](./docs/images/overview.png)

TODO: Add a demo gif

## Try it out
TODO:
- Remove the need for auth
- Have a "latest" tag on the image?

### With OpenAI

TODO:
- Add OpenAI GPT-4 with vision to config.yaml? 

```
git clone git@github.com:birgitta410/team-ai-community-knowledge-pack.git
docker run \
        -v ./tmp/team-ai-community-knowledge-pack:/app/teams \
        -e OPENAI_API_KEY=<your API KEY>
        -e TEAM_CONTENT_PATH=/app/teams \
        -e DOMAIN_NAME=team_openai \
        -e ENABLED_PROVIDERS=ollama \
        -e ENABLED_EMBEDDINGS_MODEL=ollama \
        -e ENABLED_VISION_MODEL=google-gemini \
        -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
        -p 8080:8080 \
        ghcr.io/birgitta410/team-ai:main
```

### With Ollama, locally
TODO:
- Local vision model?

```
git clone git@github.com:birgitta410/team-ai-community-knowledge-pack.git
docker run \
        -v ./tmp/team-ai-community-knowledge-pack:/app/teams \
        --env-file $pathToEnvFileWithOauthValues \
        -e TEAM_CONTENT_PATH=/app/teams \
        -e DOMAIN_NAME=team_local \
        -e ENABLED_PROVIDERS=ollama \
        -e ENABLED_EMBEDDINGS_MODEL=ollama \
        -e ENABLED_VISION_MODEL=google-gemini \
        -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
        -p 8080:8080 \
        ghcr.io/birgitta410/team-ai:main
```

## Why?

The product and tooling space around coding assistance is relatively mature, in the sense that it is possible to see value already today, and some of the products are already adopted in large enterprises.

However, when it comes to software delivery tasks other than coding, there is not much out there yet. Some of the incumbent vendors for the delivery toolchain (wikis, issue trackers, CI/CD products, ...) are working on adding AI to their toolchain, and their is the odd startup here or there that tries to tackle one of the task areas. There are also a bunch of products evolving that enable the sharing and monitoring of prompts in an organisation, which could be used to build a similar sandbox. But overall, it is hard to gather experience and data today about how AI can be used to assist a software delivery team in their day-to-day work.

**Team AI** provides a lean self-cloud-hosted sandbox to experiment, and to gather data and experience today that can inform strategy and tool choices for the future.

* Control the setup by deploying into your own infrastructure environment, instead of trusting a bleeding edge startup
* Use the models provided by your cloud provider of choice (AWS, Google Cloud, or Azure), instead of running a risk assessment for and creating contracts with a new vendor
* Add your own SSO for access control

## How?

- You can do the technical setup yourself, see below
- But, the devil is in the data and the practices
- Ask us about our consulting services to help you run your own pilot and shape a knowledge pack for your organisation

## Limited-by-design

For now, this is a one-container web application. Everything is baked into the container image you build, and everything happens in memory. The only persistence are the logs written by the application. This is by design, to keep the infrastructure setup as simple as possible, and reduce the barrier to experimentation. 

But of course, it comes with limitations:

- No database means you have to rebuild the image and redeploy the application every time you change the knowledge pack
- Users cannot edit and persist anything at runtime in the application
- User chat sessions are not persisted
- Limits to scalability, and to size of the knowledge packs, as everything needs to fit into memory

