# `TEAMAI-CLI Quickstart Guide`
The `teamai-cli` is a command line interface that provides a set of commands for indexing files, and creating knowledge packages.

### TEAMAI-CLI Installation
Using [poetry](https://python-poetry.org/) run

```console
$ poetry run cli-init
$ poetry run cli-install
```

### Setup the CLI configuration
This will allow the cli to use the api keys and embedding models you have defined in the app configuration file.
```console
$ teamai-cli init --config-path <CONFIG_PATH> --env-path <ENV_PATH>
```
- CONFIG_PATH being the app config yaml definition

    By default you can use the one located at the following path `$(pwd)/app/config.yaml`

- ENV_PATH being the path to the app environment variable file definition

    By default you can use the one located at the following path `$(pwd)/app/.env`


### Create knowledge package structure
This will create a knowledge package structure for a given domain name which will allow you to tailor the applicatioin to your specific needs.

```console
$ teamai-cli create-domain-package domain_name <DOMAIN_NAME> parent_dir<PATH_TO_PARENT_DIR>
```
- DOMAIN_NAME being the name of the domain you want to create a knowledge package for.
- PATH_TO_PARENT_DIR being the path to the knowledge pack root directory.

### Index all files in the source directory
This will convert the files you want to rely on into embeddings and store them in the knowledge package directory.
```console
$ teamai-cli index-all-files <SOURCE_DIR>  --description <DESCRIPTION> --embedding-model <EMBEDDING_MODEL> --output-dir <PATH_TO_PARENT_DIR>/<DOMAIN_NAME>/embeddings
```
- SOURCE_DIR being the path to the source directory containing the files you want to index.
- DESCRIPTION being a description of the ensemble files you want to index.
- EMBEDDING_MODEL being the embedding model you want to use for indexing.
- PATH_TO_PARENT_DIR being the path to the knowledge pack root directory where the domain package is located.


___
# `teamai-cli`

**Usage**:

```console
$ teamai-cli [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `create-domain-package`: Create a domain package base structure.
* `index-all-files`: Index all pdf or text files in a directory...
* `index-file`: Index single pdf or text file to a given...
* `init`: Initialize the config file with the given...
* `pickle-web-page`: Index a web page to a given destination path.
* `set-config-path`: Set the config path in the config file.
* `set-env-path`: Set the env path in the config file.

## `teamai-cli create-domain-package`

Create a domain package base structure.

**Usage**:

```console
$ teamai-cli create-domain-package [OPTIONS] DOMAIN_NAME KNOWLEDGE_ROOT_DIR
```

**Arguments**:

* `DOMAIN_NAME`: [required]
* `KNOWLEDGE_ROOT_DIR`: [required]

**Options**:

* `--help`: Show this message and exit.

## `teamai-cli index-all-files`

Index all pdf or text files in a directory to a given destination directory.

**Usage**:

```console
$ teamai-cli index-all-files [OPTIONS] SOURCE_DIR
```

**Arguments**:

* `SOURCE_DIR`: [required]

**Options**:

* `--output-dir TEXT`: [default: new_knowledge_base]
* `--embedding-model TEXT`: [default: openai]
* `--description TEXT`
* `--config-path TEXT`
* `--help`: Show this message and exit.

## `teamai-cli index-file`

Index single pdf or text file to a given destination directory.

**Usage**:

```console
$ teamai-cli index-file [OPTIONS] SOURCE_PATH
```

**Arguments**:

* `SOURCE_PATH`: [required]

**Options**:

* `--embedding-model TEXT`: [default: openai]
* `--config-path TEXT`
* `--description TEXT`
* `--output-dir TEXT`: [default: new_knowledge_base]
* `--help`: Show this message and exit.

## `teamai-cli init`

Initialize the config file with the given config and env paths.

**Usage**:

```console
$ teamai-cli init [OPTIONS]
```

**Options**:

* `--config-path TEXT`
* `--env-path TEXT`
* `--help`: Show this message and exit.

## `teamai-cli pickle-web-page`

Index a web page to a given destination path.

**Usage**:

```console
$ teamai-cli pickle-web-page [OPTIONS] URL
```

**Arguments**:

* `URL`: [required]

**Options**:

* `--destination-path TEXT`: [default: web_page.pickle]
* `--html-filter TEXT`: [default: p]
* `--help`: Show this message and exit.

## `teamai-cli set-config-path`

Set the config path in the config file.

**Usage**:

```console
$ teamai-cli set-config-path [OPTIONS] CONFIG_PATH
```

**Arguments**:

* `CONFIG_PATH`: [required]

**Options**:

* `--help`: Show this message and exit.

## `teamai-cli set-env-path`

Set the env path in the config file.

**Usage**:

```console
$ teamai-cli set-env-path [OPTIONS] ENV_PATH
```

**Arguments**:

* `ENV_PATH`: [required]

**Options**:

* `--help`: Show this message and exit.
