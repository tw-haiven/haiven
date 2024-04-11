# `teamai-cli`

**Installation**:
```console
$ just cli-install
```

**Usage**:

```console
$ teamai-cli [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `index-all-files`
* `index-file`

## `teamai-cli index-all-files`

**Usage**:

```console
$ teamai-cli index-all-files [OPTIONS] SOURCE_DIR
```

**Arguments**:

* `SOURCE_DIR`: [required]

**Options**:

* `--destination-dir TEXT`: [default: new_knowledge_base.kb]
* `--embedding-model TEXT`: [default: openai]
* `--config-path TEXT`: [default: ../app/config.yaml]
* `--help`: Show this message and exit.

## `teamai-cli index-file`

**Usage**:

```console
$ teamai-cli index-file [OPTIONS] SOURCE_PATH
```

**Arguments**:

* `SOURCE_PATH`: [required]

**Options**:

* `--destination-dir TEXT`: [default: new_knowledge_base.kb]
* `--embedding-model TEXT`: [default: openai]
* `--config-path TEXT`: [default: ../app/config.yaml]
* `--help`: Show this message and exit.
