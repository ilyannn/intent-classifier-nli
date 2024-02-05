# Contributing

The code should be tested,
linted and formatted correctly to pass server-side checks
(**[this repo's GitHub Actions](https://github.com/ilyannn/intent-classifier/actions)**).

## Testing

The local testing invocation is

```shell
# provided that you have an appropriate Python environment
just test
```

which currently runs some tests in the `server` folder,
including testing
that all models in `server/models` folder can be loaded
and perform inference on a simple example.

The code is expected to work for Python 3.11 and later versions
(they should be added to the tests as necessary as well as reflected in [`pyproject.toml`](pyproject.toml)).

## Code Style

### Formatting

The local formatting invocation is

```shell
# provided that you have formatters installed
just fmt
```

For Python files, this uses **isort** + **black** for formatting.

### Local Linting

The local linting invocation is

```shell
# provided that you have linters installed
just lint
```

The linting checks are as follows:

- **isort** + **black**, as well as **prettier** report no diffs
- **flake8** is happy for Python files
- **markdownlint**, **yamllint** and **hadolint** are happy for Markdown/YAML/Dockerfiles

The **pylint** command provides some statistics and refactoring suggestions, but is not used to fail the buid.

### Remote Linting

On a push,
the GitHub action **[super-linter](https://github.com/super-linter/super-linter)** is automatically triggered.
It runs a bunch of linters for many different languages.

If the local linting succeeds
while the remote linting fails,
it may be necessary to add new linters to
`just lint` or make sure all relevant files are covered by it.

### Configuration

Most of the tools can be configured with files in [`.github/linters`](.github/linters) folder.

The maximal line length in Python files is 88.

## Release Process

When the **[release tag](https://github.com/ilyannn/intent-classifier/releases)** is created,
the server-side **[CI workflow](https://github.com/ilyannn/intent-classifier/actions/workflows/docker-image.yml)** should automatically build and push the image to the cloud registry.

The image is deployed to **[intents.cluster.megaver.se](https://intents.cluster.megaver.se/info)**
by updating the corresponding **[Kustomization](https://docs.cluster.megaver.se/cluster/automatic/apps/kustomization.yaml)**
which is then picked up by the **[Argo CD](https://argocd.cluster.megaver.se)**.
