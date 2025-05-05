![Build status](https://github.com/tw-haiven/haiven/actions/workflows/main.yml/badge.svg)

# Haiven team assistant

[Thoughtworks](https://thoughtworks.com) is a global software consultancy working for a wide range of clients. We're using Haiven as an **accelerator** to offer our clients a **lean way to pilot the use of AI assistance for software delivery teams** while the market of products is still busy and evolving.

## What is it?

A **sandbox to lower the barrier to experiment** with the use of Generative AI assistance for software delivery **tasks beyond coding**. 

- Simple one-container deployment --> **easy to deploy** in your environment
- Integratable with the 3 big cloud provider's model services (Azure OpenAI, Google Gemini, AWS Bedrock) --> choose your existing cloud provider of choice to alleviate at least some of the **data confidentiality concerns** that currently limit many enterprise's choice of product and tool usage
- Separation of application and **"knowledge pack"** to plug in and change your own prompts and domain information --> **customize** to your team, and potential to **reuse** what you develop in the knowledge pack in other AI tools

## What is it NOT?

- A product
- A fully fleshed out and scalable tool

## Why?

[More on the why here](docs/why.md), in particular these two questions:
* Why would you use it?
* How does it compare to...?

# Overview

![Overview](./docs/images/overview.png)

Haiven lets you codify your practices and knowledge and make it available to an AI assistant, to surface it to team members just-in-time when they are working on a task.

![Overview in more detail](./docs/images/overview_more_details.png)

## Quickest way to try it out

*Disclaimer: As the majority of developers in Thoughtworks are using MacOS, all shell-related instructions are currently only build for and tested on MacOS.*

You can run the application with the public sample knowledge pack `haiven-sample-knowledge-pack`, which is very rudimentary. Or, if you work at Thoughtworks, you can request access to our private knowledge pack `haiven-tw-demo-knowledge-pack` [via this form](https://docs.google.com/forms/d/e/1FAIpQLSf-9pXjm_bGJNtGaXUnkh1MgLS6uNqQySA4nkk3LmOZY3tjxA/viewform).

### With Azure OpenAI

- Create a `.env` file with the content of [app/.env.azure.template](app/.env.azure.template)
- Change the `AZURE_OPENAI_API_KEY` in that file to the API Key - (Thoughtworkers can ask the Haiven team for access to the "trial" Azure OpenAI API Key).

```
mkdir haiven
cd haiven
# Put the .env file into this new folder

# Make sure you have git-lfs installed when cloning knowledge packs, otherwise git might only partially clone
git clone git@github.com:tw-haiven/haiven-tw-demo-knowledge-pack.git
# The TW knowledge pack is private, you can use our sample pack if you don't have access
# git clone git@github.com:tw-haiven/haiven-sample-knowledge-pack.git

docker run \
        -v ./haiven-tw-demo-knowledge-pack:/knowledge-pack \
        --env-file .env \
        -e AUTH_SWITCHED_OFF=true \
        -e KNOWLEDGE_PACK_PATH=/knowledge-pack \
        -p 8080:8080 \
        ghcr.io/tw-haiven/haiven:main
```

### With Ollama, locally

Prerequisites:
- Install [Ollama](https://ollama.com/).

```
ollama pull llama2
ollama pull llava:7b
mkdir haiven
cd haiven

# Make sure you have git-lfs installed when cloning knowledge packs, otherwise git might only partially clone
git clone git@github.com:tw-haiven/haiven-tw-demo-knowledge-pack.git
# The TW knowledge pack is private, you can use our sample pack if you don't have access
# git clone git@github.com:tw-haiven/haiven-sample-knowledge-pack.git

docker run \
        -v ./haiven-tw-demo-knowledge-pack:/knowledge-pack \
        -e KNOWLEDGE_PACK_PATH=/knowledge-pack \
        -e AUTH_SWITCHED_OFF=true \
        -e ENABLED_PROVIDERS=ollama \
        -e ENABLED_EMBEDDINGS_MODEL=ollama-mxbai-embed-large \
        -e ENABLED_VISION_MODEL=ollama-local-llava \
        -e OLLAMA_HOST=http://host.docker.internal:11434 \
        -p 8080:8080 \
        ghcr.io/tw-haiven/haiven:main
```

#### Ollama restrictions
Please note that while this local mode is great for getting a taste of the application, the prompts in our knowledge pack are currently only tested with the AWS, Azure and Google models listed [here](https://github.com/tw-haiven/haiven/blob/main/app/config.yaml), and might not work as well with the open models loaded with Ollama. Any of the RAG capabilities are also not working well in this mode, which is why our sample knowledge pack does not even contain any Ollama-compatible embeddings. It is possible, but we have not seen reasonable results with that yet.

## Limited-by-design

For now, this is a one-container web application. Everything is baked into the container image you build, and everything happens in memory. The only persistence are the logs written by the application. This is by design, to keep the infrastructure setup and data persistence setup as simple as possible, because we are prioritising a low barrier to experimentation.

![](docs/images/one_container_tradeoffs.png)

## How to run and deploy

### 1. Prepare access to Large Language Models

There are 4 options:
- Azure AI Studio
- AWS Bedrock
- Google AI Studio
- Ollama (locally)

#### Option 1: Use Ollama locally on your machine

- Install [Ollama](https://ollama.com/) on your machine, as described by their website
- Pull one of the models defined in the [config.yaml](app/config.yaml) file, e.g. `ollama pull llama2`
- Create an `.env` file: `cp app/.env.ollama.template app/.env`

#### Option 2: Setup credentials for Azure, GCP or AWS

- Prepare the model setup and credentials in your respective Cloud environment. Check `[app/config.yaml](app/config.yaml)` for the models that we currently have configured.
- Consider setting quota and billing alerts to avoid unexpected costs and detect unexpected usage.
- Create `.env` file from the respective template: Pick the template file that represents the provider you want to use, e.g. `cp ./app/.env.azure.template ./app/.env`.
- Look at the defined environment variables in your new `.env` file and fill in the credentials (API keys).

### 2. Get (and adapt) a "knowledge pack"

You can clone the [Sample Knowledge Pack](https://github.com/tw-haiven/haiven-sample-knowledge-pack) or, for Thoughtworkers, the [Thoughtworks Knowledge Pack](https://github.com/tw-haiven/haiven-tw-demo-knowledge-pack) to get started. <br/>
Note: Make sure you have *git-lfs* installed before cloning knowledge packs, otherwise git might only partially clone.


Find more documentation about knowledge packs and how to adapt them [here](docs/knowledge_packs.md).


### 3. Run locally
#### Option 1: Run the base image locally

See "quickest way to try it out" above, which describes how to run the base Docker image with Ollama as the model provider.

If you want to use Azure, GCP or AWS, you need to set the corresponding environment variables as documented in the `.env.***.template` files, and feed those to the container.

#### Option 2: Run the code locally

Prerequisites:
- Python (3.11)
- [Poetry](https://python-poetry.org/)
- Node and yarn - check `package.json` for current specific node version needed, we're often fighting with incompatibilities between next.js upgrades and node versions
- If you don't have OAuth integration and credentials set up yet, you can set `AUTH_SWITCHED_OFF=true` in the `.env` file.

Set up all other dependencies with this script (MacOS only):
```
./install_dev_dependencies.sh
```

Package the UI code (React):
```
cd ui
yarn install
yarn copy
```

Run Python backend:

```
poetry run init
poetry run app
```

Run UI code in hot reload mode:
```
cd ui
yarn dev
# "hot reload" ui will run on localhost:3000, but connect to localhost:8080 backend
```

Test:
```
poetry run pytest -m 'not integration' tests/
```

### 4. Deploy your own instance

#### Set up OAuth integration

If you want to integrate your own OAuth provider, check out the OAuth-related environment variables as described in the `.env.***.template` files.

#### Build an image with your knowledge pack

Look at the [Sample Knowledge Pack repository](https://github.com/tw-haiven/haiven-sample-knowledge-pack) for an example of a `Dockerfile` that helps you bake your own knowledge pack into a Haiven image that you can then deploy to your own environment. When you do the deployment, remember to set the environment variables and secrets described in the `.env` template files in that runtime.

### Configure more models

#### Setup models

[`app/config.yaml`](app/config.yaml) is where the configuration for the models and embeddings is set. You can add or remove models from the configuration file. It is pre-populated with some working examples. Note that if you want to add a new type of embeddings, the code would also have to change to support that.

Secrets should not be added to `app/config.yaml`. For that matter in `app/config.yaml`, if one of the values is considered a secret, you must use a placeholder for an environment variable using the following format: `${ENV_VAR_NAME}`, where `ENV_VAR_NAME` is the name of the environment variable. This value will be replaced on runtime with the value of the environment variable, which can be securely set at deployment time.

The base container image includes the default `app/config.yaml` file. You can override this by providing a different `config.yaml` when building an image for your knowledge pack. The `Dockerfile` in the [Sample Knowledge Pack repository](https://github.com/tw-haiven/haiven-sample-knowledge-pack) includes instructions to replace the default `config.yaml` with the one from the `config_override` folder. If no file is found in `config_override`, the default configuration is used.


##### Setup default models

You can fix the models to be used by different use cases by setting the `chat`, `vision` and `embeddings` properties to a valid model `id` value, in the `default_models` section of the `app/config.yaml` file.

Example:

```yaml
default_models:
  chat: azure-gpt4
  vision: azure-gpt4-with-vision
  embeddings: text-embedding-ada-002
```

#### You want to deploy?

How you deploy the container image is all up to your environment - you could use Google Cloud Run, or an existing Kubernetes cluster on AWS, or an equivalent service on Azure, or your own data center container infrastructure.

This of course makes you responsible for the usual application security practices like secrets management, TLS, security monitoring and alerting, etc.

For Thoughtworkers: Our demo deployment is an example for deploying Haiven to Google Cloud, ask the Haiven team about access to that code.
