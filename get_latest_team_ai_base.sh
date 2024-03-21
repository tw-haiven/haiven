
mkdir tmp
git clone git@github.com:twlabs/Team-AI-on-Google.git tmp/Team-AI-on-Google/
cp -r tmp/Team-AI-on-Google/app .
cp -r tmp/Team-AI-on-Google/docs .
cp -r tmp/Team-AI-on-Google/cli .
cp -r tmp/Team-AI-on-Google/.vscode .
cp tmp/Team-AI-on-Google/README.md .
cp tmp/Team-AI-on-Google/.gitattributes .
cp tmp/Team-AI-on-Google/.gitignore .
cp tmp/Team-AI-on-Google/.pre-commit-config.yaml .

# rm -rf tmp