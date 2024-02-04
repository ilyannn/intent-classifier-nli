#!/usr/bin/env just
# See https://github.com/casey/just for the just command and format explanation

_default:
    @just --list --unsorted --justfile {{justfile()}} --list-prefix '····'


# Update this list as necessary
docker_files := "*/Dockerfile*"
markdown_files := "*.md"
python_files := "**/*.py"
yaml_files := ".github/*/*.yml"


# Server instance URL for benchmarking
server_instance := "https://intents.cluster.megaver.se"

# Do you prefer Docker or Podman?
container_tool := "podman"


# format Markdown, YAML and Python files
fmt:
    prettier --write -- {{markdown_files}} {{yaml_files}}
    isort --settings-path .github/linters/.isort.cfg -- {{python_files}}
    black -- {{python_files}}


# lint Markdown, YAML, Dockerfiles and Python files
lint:
    hadolint --config .github/linters/.hadolint.yaml  -- {{docker_files}}
    yamllint --config-file .github/linters/.yaml-lint.yml -- {{yaml_files}}
    markdownlint --config .github/linters/.markdown-lint.yml -- {{markdown_files}}
    prettier --check -- {{markdown_files}} {{yaml_files}}
    flake8 --config .github/linters/.flake8 -- {{python_files}}
    mypy --config-file .github/linters/.mypy.ini -- {{python_files}}
    isort --settings-path .github/linters/.isort.cfg --check --diff -- {{python_files}}
    black --check --fast --diff --color -- {{python_files}}
    pylint --rcfile .github/linters/.python-lint -- {{python_files}} 


# test Python files
test:
    cd server && python -m unittest tests/*.py


# run the server application in Docker
serve port:
    {{container_tool}} run -it -p {{port}}:5501 `{{container_tool}} build -q server` 


# run benchmarks against the cloud instance
benchmark:
    client/benchmark.py --url {{server_instance}} -j 64 -o benchmark.errors.tsv -- data/atis/test.tsv
