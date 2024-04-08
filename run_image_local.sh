
# Prerequisites
### Access to the knowledge pack git repo
### Access to the Docker registry
### Knowledge of the OAuth secrets (until we offer option without login)

# Provide path to the .env file as first argument
pathToEnvFileWithOauthValues=$1

! rm -rf tmp
! mkdir tmp
git clone git@github.com:birgitta410/team-ai-community-knowledge-pack.git tmp/team-ai-community-knowledge-pack/

# docker login ghcr.io -u <USERNAME> -p <personal access token with read:packages permission>
docker pull ghcr.io/birgitta410/team-ai:main
docker run \
        -v ./tmp/team-ai-community-knowledge-pack:/app/teams \
        --env-file $pathToEnvFileWithOauthValues \
        -e TEAM_CONTENT_PATH=/app/teams \
        -e DOMAIN_NAME=team_demo \
        -e ENABLED_PROVIDERS=ollama \
        -e ENABLED_EMBEDDINGS_MODEL=ollama \
        -e ENABLED_VISION_MODEL=google-gemini \
        -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
        -p 8080:8080 \
        ghcr.io/birgitta410/team-ai:main