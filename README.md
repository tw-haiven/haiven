# Team AI demo

**Team AI** is an accelerator to help software delivery teams build their own lightweight prompting application as an _assistant and knowledge amplifier for frequently done tasks_ across their software delivery process.

This demo shows some examples of the types of tasks that can be supported by GenAI, and the types of interaction patterns teams can leverage. But this is not meant to be a ready-made product, the idea is to copy the codebase and use it as an accelerator to build a team's own customized team assistant.

Find more [context about Team AI here](https://docs.google.com/presentation/d/11VGcwOP-HxCXqDhUAd-PE6LWBeiMNbIItrdtyBRtkMI/edit?usp=sharing)

## Benefits

- Amplifying and scaling good prompt engineering via reusable prompts
- Use GenAI optimized for a particular team's or organization's tasks, wherever existing products are too rigid
- Knowledge exchange via the prepared context parts of the prompts
- Helping people with tasks they have never done before (e.g. if team members have little experience with story-writing)
- The "Q&A" pattern in particular helps leverage LLMs for brainstorming and finding gaps earlier in the delivery process

### How does the "acceleration" work

When a team takes the codebase as a starting point to deploy their own Team AI, they can use existing demo components as a basis for their own task support. E.g., use the "Story writing" example as a basis if you want to support a task with a Question<>Answer interaction. It's not a lot of code, the "Story writing" example is just about 70 lines of Python code, plus the prompting template.

## Local development

### Folder structure

- `./app` contains the Python application
  - `./shared` contains code that can be reused by all use cases
  - `./tab_*` folders contains one of the "use cases", i.e. tabs in the UI
  - `./resources` contains resources like reusable prompt components, HTML templates, static files that will be served as part of the webserver
  - `./teams` contains prompts and team folders, where one folder per team contains a set of knowledge bases
- `./infra` contains the Terraform code that sets up the deployment infrastructure on Google Cloud Run

### Prerequisites

- Python3
- Knowledge Base Use Case: [Git Large File Storage](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage) is needed to store the larger knowledge bases. You might have to run `git lfs install` and `git lfs pull` to make sure the knowledge bases are properly cloned.
- For using vertexAI install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
- Credentials for the AI services. If you don't have your own, you can get the shared credentials by accessing the secrets manager in the corresponding google cloud project. Talk to the neo project owner.
- Just CLI for running helper scripts. [Install Just](https://just.systems/man/en/chapter_4.html) and use `just -l` to list available scripts.

#### Setup credentials

- Create .env file from template `cp .env.template .env`
- Filter the model providers you want to be available via the `ENABLED_PROVIDERS` variable in `.env`. This is expected to be a comma-separated list of providers, the values must match the "provider" properties in `app/config.yaml`. Example: `ENABLED_PROVIDERS=azure,gcp,aws`
- Set corresponding credentials in the `.env` file
- For vertextai ensure to be logged into `gcloud`
- For Google Gemini, you need a `GOOGLE_API_KEY`, can be generated in Google's AI Studio at makersuite.google.com (or get it from the secrets manager in the Team AI Google Cloud project)

#### Setup models

[`app/config.yaml`](app/config.yaml) is where the configuration for the models and embeddings is set. You can add or remove models from the configuration file. Currently only `embedding` is used to setup the application.

The configuration file is a YAML containing a list of LLM models and one embedding model, using the following structure:

```yaml
models:
  - id: model id
    name: Model name
    provider: provider name
    features: # a list of strings
      - text-generation
      - image-to-text
    config: # a dictionary of key value pairs
      config_key: config value
      secret_config: ${ENVIRONMENT_VARIABLE}

embedding:
  id: model id
  name: Model name
  provider: provider name
  config: # a dictionary of key value pairs
    config_key: config value
    secret_config: ${ENVIRONMENT_VARIABLE}
```

`app/config.yaml` is pre-populated with some working examples. To use your own embeddings model replace the values of the current one, adding the corresponding confoguration values. Note that only OpenAI or Azure embeddings models are supported at the moment. If you want to use a different provider, you need to implement the corresponding `generate_[your provider]_embeddings` method in [`app/shared/embeddings.py`](app/shared/embeddings.py).

Secrets should not be added to `app/config.yaml`. For that matter in `app/config.yaml`, if one of the values is considered a secret, you must use a placeholder for an environment variable using the following format: `${ENV_VAR_NAME}`, where `ENV_VAR_NAME` is the name of the environment variable. This value will be replaced on runtime with the value of the environment variable, which can be securely set at deployment time.

> Note: Embeddings model cannot be changed after app initialization. The same embeddings model is used independentely of the LLM model selected.
>
> Note 2: Currently, the embedding model configured in `app/config.yaml` is only used for the PDFs uploaded. The existing knwoledge bases are fixed to use OpenAI embeddings model.

##### Setup default models

You can fix the models to be used by different use cases by setting the `chat`, `vision` and `embeddings` properties to a valid model `id` value, in the `default_models` section of the `app/config.yaml` file.

Example:

```yaml
default_models:
  chat: azure-gpt4
  vision: google-gemini
  embeddings: text-embedding-ada-002
```

Only embeddings is mandatory. When chat or vision are not set, the app will show a dropdown allowing the user to select the model to use.

#### Setup LM Studio to use a local LLM

Team-AI supports using a local LLM model for some of the use cases (diagram interpretation use case not yet supported). We use [LM Studio](https://lmstudio.ai/) for this purpose, as it offers the possibility to host a downloaded LLM as an OpenAI compatible API.

After installing and configuring LM Studio with the model of your choice, go to the local server tab `<->` in LM Studio. You can choose which port the server will use, by default is `1234` as already configured in `.env.teplate` file. If you change the port, it needs to be reflected in the environment variable `LM_STUDIO_BASE_URL`.

In order for the option to use a local model to appear in the UI, you need to enable the usage of LM Studio, but setting `USE_LMSTUDIO` to `true` in the `.env` file. Once this is done, start the app with `just init` and `just run` and the option to use a local model should appear in models dropdown with the name _Local Model on LM Studio_, independently of the model you use.

> Tip: You can change models in LM Studio without restarting Team-AI.

### Run Manually

#### Start the app

Follow the steps below to run the app manually:

```bash
cd app
python3.10 -m venv venv # create a virtual environment, only required in the first run
source ./venv/bin/activate # activate the virtual environment
pip install -r requirements.txt # install dependencies, only required in the first run
python main.py # start the app
```

The app starts a local web server in port 8080, browse to <http://localhost:8080> to open the app.

Team AI app uses uvicorn as the web server. To run the app with uvicorn using hot reload, use the following command:

```bash
uvicorn "dev:app" --host "localhost" --port 8080 --reload
```

#### Using docker

To run the app using docker, use the following commands:

```bash
cd app
docker build -t team-ai-local .
docker run --env-file .env -p 8080:8080 team-ai-local
```

**Experimental: Running the image locally and mounting a folder with knowledge and prompts**

Copy the `demo-knowledge-pack` folder to somewhere on your machine, and use that location as the source for prompts and knowledge. This offers the potential to run this fully locally - however, note that the knowledge bases in the demo pack will not work with ollama locally, because they have all been built with another embeddings model. The model that creates the knowledge needs to match the embeddings model used at runtime to ask the question.

Also, we haven't looked into a local vision model yet.

```
docker pull us-central1-docker.pkg.dev/team-ai-7a96/team-ai/team-ai-base:main
docker run \
        -v ./path/to/your/local/pack:/app/teams \
        --env-file Team-AI-on-Google/app/.env \
        -e TEAM_CONTENT_PATH=/app/teams \
        -e DOMAIN_NAME=team_demo \
        -e ENABLED_PROVIDERS=ollama \
        -e ENABLED_EMBEDDINGS_MODEL=ollama \
        -e ENABLED_VISION_MODEL=google-gemini \
        -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
        -p 8080:8080 \
        us-central1-docker.pkg.dev/team-ai-7a96/team-ai/team-ai-base:main
```

```bash
docker run \
        -v ~/your/local/teams/folder/copy:/app/teams/team-ai-mount \
        --env-file .env \
        -e TEAM_CONTENT_PATH=/app/teams/team-ai-mount \
        -e TEAM_NAME=team_xxx \
        -e ENABLED_PROVIDERS=azure,gcp,aws \
        -e LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1 \
        -p 8080:8080 \
        team-ai-local
```

#### Tests

To execute the test, use the following commands:

```bash
cd app
source ./venv/bin/activate
pip install pytest
pytest
```

### Using Just

These are the scripts available using `just` CLI:

- `just init`: Initializes the environment. This only has to be done the first time, or each time a new dependency is added to the project.
- `just run`: Runs the app.
- `just test`: Runs the tests.
- `just build-docker-image`: Builds the Docker image.
- `just run-docker-image`: Starts the Docker image.
