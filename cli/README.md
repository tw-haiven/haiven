t statu# `teamai-cli`

**Usage**:

```console
$ teamai-cli [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `index-all-files`: Index all pdf or text files in a directory...
* `index-file`: Index single pdf or text file to a given...
* `init`: Initialize the config file with the given...
* `pickle-web-page`: Index a web page to a given destination path.
* `set-config-path`: Set the config path in the config file.
* `set-env-path`: Set the env path in the config file.

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
* `--config-path TEXT`: [default: config.yaml]
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
* `--config-path TEXT`: [default: config.yaml]
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

* `--config-path TEXT`: [default: config.yaml]
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
