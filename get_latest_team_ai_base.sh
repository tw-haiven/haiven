
# Preparing new repo structure while active development is going on in the other repo
# This script helps pull the necessary parts of the other repo when it's time to publish

! rm -rf tmp
! mkdir tmp
git clone git@github.com:twlabs/Team-AI-on-Google.git tmp/Team-AI-on-Google/
cp -r tmp/Team-AI-on-Google/app .
cp -r tmp/Team-AI-on-Google/docs .
cp -r tmp/Team-AI-on-Google/cli .
cp -r tmp/Team-AI-on-Google/.vscode .
# NOT cp tmp/Team-AI-on-Google/README.md . # preparing new README in this repo, don't override with old one
# NOT cp tmp/Team-AI-on-Google/.gitattributes . # LFS not necessary in this repo
cp tmp/Team-AI-on-Google/.gitignore .
cp tmp/Team-AI-on-Google/.pre-commit-config.yaml .
