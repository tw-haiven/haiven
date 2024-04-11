
# Preparing new repo structure while active development is going on in the other repo
# This script helps pull the necessary parts of the other repo when it's time to publish

! rm -rf tmp
! mkdir tmp
git clone git@github.com:twlabs/Team-AI-on-Google.git tmp/Team-AI-on-Google/

! rm -rf app
cp -r tmp/Team-AI-on-Google/app .

# NOT cp -r tmp/Team-AI-on-Google/docs . # Starting fresh set of docs here. Copy files from other repo over deliberately

! rm -rf cli
cp -r tmp/Team-AI-on-Google/cli .

! rm -rf .vscode
cp -r tmp/Team-AI-on-Google/.vscode .

# NOT cp tmp/Team-AI-on-Google/README.md . # preparing new README in this repo, don't override with old one
# NOT cp tmp/Team-AI-on-Google/.gitattributes . # LFS not necessary in this repo
cp tmp/Team-AI-on-Google/.gitignore .
cp tmp/Team-AI-on-Google/.pre-commit-config.yaml .
cp tmp/Team-AI-on-Google/justfile .
cp tmp/Team-AI-on-Google/LICENSE.md .

cp ../../Team-AI-on-Google/app/.env ./app/
echo "Change TEAM_CONTENT_PATH=../../team-ai-tw-knowledge-pack"
