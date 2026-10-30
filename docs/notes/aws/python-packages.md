# Host Python packages for AWS

This note records the Python packages installed on the build host for the
project in [the AWS account note](README.md). Credits, always-free bands, and
the five activity rewards stay in [free-plan-usage.md](free-plan-usage.md).
The recipes themselves live outside this repository, in
`~/Github/PKGBUILDs`, with the build plan in
`~/Github/PKGBUILDs/aws-python-plan.md`.

The measurements below are from 2026-10-29 on CPython 3.14. System
site-packages is `/usr/lib/python3.14/site-packages`. `sys.path` places
`~/.local/lib/python3.14/site-packages` ahead of that directory, which
changes one import, recorded under [dateparser](#dateparser). A name in a
signature is a name `inspect.signature` returned that day. A package whose
`__init__` re-exports the standard library is called out, and those
re-exports are left out of its API. No call in this note contacted AWS,
started Docker, or started LocalStack.

Pacman package versions and Python distribution versions differ for
protobuf: `python-protobuf` is `36.1-1.1` and
`importlib.metadata.version("protobuf")` is `7.36.1`. The tables use the
Python distribution version unless they name the pacman package.

Which archive was installed, and which archives were available and left
unused, is in
[Mirrors and the other install paths](#mirrors-and-the-other-install-paths).
Usage taken from each program's `--help` is in [Command help](#command-help).

## Mirrors and the other install paths

Three places can supply one of these packages: the pacman mirrors behind
`paru` and `pacman -S`, the AUR, and a recipe under `~/Github/PKGBUILDs`.
The path that was used is the one named in each package's section. The
others below were checked and left unused.

### OpenTelemetry pkgrel 4 and pkgrel 5

`/etc/pacman.d/mirrorlist` tries, in order,
`https://archlinux.cachyos.org/repo/$repo/os/$arch`,
`https://geo.mirror.pkgbuild.com/$repo/os/$arch`,
`https://mirror.osbeck.com/archlinux/$repo/os/$arch`, then
`mirror.sahil.world`, `fastly.mirror.pkgbuild.com`, and further Arch
mirrors. The local sync database still names both OpenTelemetry packages
`0.66b1-4`. A `paru -S --needed` run selected those pkgrel 4 files. The
download then failed: the mirrors it asked returned 404, and pacman stopped
with `no packages were upgraded`. Nothing from that transaction was
installed.

A later HEAD of
`python-opentelemetry-instrumentation-aws-lambda-0.66b1-<pkgrel>-any.pkg.tar.zst`,
and the same check for the X-Ray propagator on `geo.mirror.pkgbuild.com`:

| Mirror | pkgrel 4 | pkgrel 5 |
|---|---|---|
| `archlinux.cachyos.org/repo/extra/os/x86_64` | 404 | 200 |
| `geo.mirror.pkgbuild.com/extra/os/x86_64` | 404 | 200 |
| `fastly.mirror.pkgbuild.com/extra/os/x86_64` | 404 | 200 |
| `mirror.osbeck.com/archlinux/extra/os/x86_64` | 200 | 200 |

The first mirrors have replaced pkgrel 4 with pkgrel 5. osbeck still had
both files. The local database had not been refreshed, so it kept
advertising the file the first mirrors no longer store.

The install that landed is `pacman -U` of the pkgrel 4 archives already in
`/var/cache/pacman/pkg/`. That command does not refresh the database and
does not move the rest of `extra`. Both installed packages are `0.66b1-4`.

The unused alternatives:

- Refresh the sync database and install the two packages. They then resolve
  to `0.66b1-5` on a mirror that has that file. A database refresh changes
  what a later install sees, so it was left unrun.
- Install pkgrel 4 from osbeck while that mirror still has the file. The
  next time osbeck drops pkgrel 4, that URL 404s as well.
- A full system upgrade. That moves these two packages and every other
  outdated package. It was not run.
- A PKGBUILD pinned to either pkgrel. Both releases are the Arch `extra`
  package, and pkgrel 4 is already installed from the cache.

### paru selects BlackArch for boltons

`paru -Sp python-boltons` prints
`https://mirrors.dotsrc.org/blackarch/blackarch/os/x86_64/python-boltons-25.0.0-2-any.pkg.tar.zst`.
`paru --aur -Sp python-boltons` prints that same BlackArch archive. The AUR
package is 26.2.0-1, which is the release the Braket SDK depends on. The
path that was used is the wheel recipe
`~/Github/PKGBUILDs/python-boltons`, installed as `python-boltons` 26.2.0-1.
`paru -S python-boltons` stays unused.

### A newer release than paru's package

When `extra` or the AUR is behind the release this stack needs, the recipe
in `~/Github/PKGBUILDs` is the install. That is how scramp 1.4.9, pyathena
4.2.1, redshift-connector 2.2.0, and the other local recipes landed. The
AUR and PyPI versions that were left uninstalled are in
[Left uninstalled](#left-uninstalled). Replacing `python-boto3` 1.43.108-1
or installing `extra/aws-cli` 1.x is not one of those paths.

### moto's server extra

`/usr/bin/moto_server` imports `flask_cors` and raises
`ModuleNotFoundError: No module named 'flask_cors'`. The `moto[server]`
extra is not installed. `moto.mock_aws` is the in-process interface and
does not import that module. Installing `python-flask-cors` would be what
makes `moto_server` start. It was not installed. `moto_proxy --help` does
run. Its options are `-H/--host`, `-p/--port`, and `-v/--verbose`. The
proxy was not started.

## Core SDK, left at the installed release

These were already installed. The PKGBUILD set does not replace them, and
it does not install `extra/aws-cli` 1.x over `aws-cli-v2`.

| Pacman package | Distribution | Import | Role |
|---|---|---|---|
| `aws-cli-v2` 2.37.9-1 | the `aws` binary | none | owns `/usr/bin/aws` |
| `python-boto3` 1.43.108-1 | `boto3` 1.43.108 | `boto3` | service clients and resources |
| `python-botocore` 1.43.108-1 | `botocore` 1.43.108 | `botocore` | session, endpoints, retries, waiters |
| `python-s3transfer` 0.19.2-1 | `s3transfer` 0.19.2 | `s3transfer` | multipart S3 transfer |
| `python-awscrt` 0.37.0-1.1 | `awscrt` 0.37.0 | `awscrt` | CRT bindings boto3 can use |
| `python-moto` 5.2.3-1 | `moto` 5.2.3 | `moto` | in-process AWS mock |

`/usr/bin/aws` was still owned by `aws-cli-v2` 2.37.9-1 after the CDK asset
packages were installed. The running client reported
`aws-cli/2.37.9 Python/3.14.8`.

### boto3

`boto3` is the SDK entry. Constructing a client uses the ambient credentials
and is a service call, so this note imported the module and stopped there.
On this project the profile is `gororoba` and the selected Region is
`us-east-2`.

```text
boto3.client(*args, **kwargs)
boto3.resource(*args, **kwargs)
boto3.setup_default_session(**kwargs)
boto3.set_stream_logger(name="boto3", level=10, format_string=None)
boto3.Session(aws_access_key_id=None, aws_secret_access_key=None,
              aws_session_token=None, region_name=None,
              botocore_session=None, profile_name=None,
              aws_account_id=None)
```

`DEFAULT_SESSION` is `None` until `setup_default_session` or a first
`client()` call. Submodules on the package: `compat`, `docs`, `exceptions`,
`logging`, `resources`, `session`, `utils`.

### botocore

The session object is `botocore.session.Session`. The package top also
exposes initializer hooks and the operation-name translator. `xform_name`
carries a large memo as its default argument; the callable form is
`xform_name(name, sep="_")`.

```text
botocore.register_initializer(callback)
botocore.unregister_initializer(callback)
botocore.invoke_initializers(session)
botocore.xform_name(name, sep="_")
```

The package imports its endpoint, retry, signer, paginator, waiter, and
credential modules. Service operations live on the client a session creates,
one method per API operation, generated from the service model.

### s3transfer

Docstring: abstractions over S3 upload and download. The object a caller
builds is `S3Transfer`. `TransferConfig` sets the multipart threshold.

```text
s3transfer.S3Transfer(client, config=None, osutil=None)
s3transfer.TransferConfig(multipart_threshold=8388608, max_concurrency=10,
                          multipart_chunksize=8388608,
                          num_download_attempts=5, max_io_queue=100)
s3transfer.MultipartUploader(client, config, osutil, executor_cls=ThreadPoolExecutor)
s3transfer.MultipartDownloader(client, config, osutil, executor_cls=ThreadPoolExecutor)
```

Upload and download failures surface as `S3UploadFailedError`,
`RetriesExceededError`, `IncompleteReadError`, `ReadTimeoutError`, and
`ResponseStreamingError`.

### awscrt

`__all__` names `auth`, `crypto`, `http`, and `io`, and those four imported.
The same list also names `aio`, `aws_iot_metrics`, `logging`, `mqtt`,
`mqtt5`, `mqtt_request_response`, `s3`, and `websocket`. Those eight are
absent as attributes of this install.

### moto

`moto.mock_aws(func=None, config=None)` returns a `MockAWS` context or a
decorator. Console scripts, both unused here: `moto_proxy=moto.proxy:main`
and `moto_server=moto.server:main`. Submodules: `backend_index`, `backends`,
`core`, `settings`, `utilities`.

## Command-line programs

| Binary | Owner | Entry |
|---|---|---|
| `/usr/bin/aws` | `aws-cli-v2` 2.37.9-1 | the v2 CLI |
| `/usr/bin/awslocal` | `python-awscli-local` 0.22.0-1 | script, no importable module |
| `/usr/bin/sam` | `aws-sam-cli` 1.138.0-1 | `samcli.cli.main:cli` |
| `/usr/bin/cfn-lint` | `python-cfn-lint` 1.57.1-1 | `cfnlint.runner:main` |
| `/usr/bin/cookiecutter` | `python-cookiecutter` 2.7.1-1 | `cookiecutter.__main__:main` |
| `/usr/bin/localstack` | `python-localstack` 2026.8.2-1 | `localstack_cli.cli.main:main` |
| `/usr/bin/chevron` | `python-chevron` 0.14.0-1 | `chevron:cli_main` |
| `/usr/bin/lambda-builders` | `python-aws-lambda-builders` 1.54.0-1 | `aws_lambda_builders.__main__:main` |
| `/usr/bin/fastavro` | `python-fastavro` 1.13.1-1 | `fastavro.__main__:main` |
| `/usr/bin/py-build-cmake` | `python-py-build-cmake` 0.5.1-1 | `py_build_cmake.cli:cli` |
| `/usr/bin/jsonpath_ng` | `python-jsonpath-ng` 1.8.0-1 | `jsonpath_ng.bin.jsonpath:entry_point` |
| `/usr/bin/uvicorn` | `uvicorn` 0.54.0-1 | ASGI server |
| `/usr/bin/dateparser-download` | see [dateparser](#dateparser) | two copies |

`/usr/bin/lstk` does not exist. `localstack --help` on this host prints that
the `localstack` CLI is deprecated in favor of `lstk`, then continues with
the legacy CLI. Its commands begin with `auth`. The process was not asked to
start a container.

`awslocal` has an empty `top_level.txt`. `import awscli_local` raises
`ModuleNotFoundError`. The script's summary is a thin wrapper that inserts
`--endpoint-url` so a LocalStack command can omit it. `main` tries
`import awscli.clidriver`. That import fails here because `extra/aws-cli`
1.x is absent, and `main` then replaces the process with the `aws` binary
(`run_as_separate_process`). Endpoints come from
`localstack_client.config.get_service_endpoints`. For CloudFormation
`package` and `deploy`, the script prints that those two v2 subcommands are
outside what `awslocal` supports and that they want AWS CLI v1. The `ver1`
extra of the distribution requires the `awscli` distribution, which is that
v1 package and stays uninstalled. `awslocal` was not executed.

## Command help

Each block is what the program printed for `--help` on 2026-10-29, or the
usage it printed when `--help` is not a flag it accepts. None of these
commands was used to call AWS, start Docker, or start a server.

### aws

`aws --help` exits 252 because a command is required. The usage it prints
is `aws [options] <command> <subcommand> [<subcommand> ...] [parameters]`,
with further text from `aws help`, `aws <command> help`, and
`aws <command> <subcommand> help`. The binary is AWS CLI v2. Service
commands are that CLI's command set. `aws help` is the manual.

### awslocal

`awslocal -h` prints the wrapper summary. Its example is
`awslocal kinesis list-streams` in place of
`aws --endpoint-url=https://localhost:4568 --no-verify-ssl kinesis list-streams`.
Subcommand help is `aws help`. The CloudFormation `package` and `deploy`
limit is in the section above.

### sam

`sam --help` is the AWS SAM CLI. Commands it lists:

| Group | Commands |
|---|---|
| Learn | `docs` |
| Create an App | `init` |
| Develop your App | `build`, `local`, `validate`, `sync`, `remote` |
| Deploy your App | `package`, `deploy` |
| Monitor your App | `logs`, `traces` |
| And More | `list`, `delete`, `pipeline`, `publish` |

Global options: `--beta-features` / `--no-beta-features`, `--debug`,
`--version`, `--info`. The example in the help is `sam init`.

`sam build --help` builds one optional `RESOURCE_LOGICAL_ID`. It names
`AWS::Serverless::Function`, `AWS::Lambda::Function`,
`AWS::Serverless::LayerVersion`, and `AWS::Lambda::LayerVersion`. The
Python runtimes it lists are 3.8, 3.9, 3.10, 3.11, 3.12, and 3.13. The same
help says SAM CLI collects telemetry unless `SAM_CLI_TELEMETRY=0`. `sam
build` was not run.

`sam validate --help` lints a template. The default file is
`template.yaml`. The help's example is `sam validate --lint`, and it says
the command may not require AWS credentials. It was not run.

`sam local --help` has `generate-event`, `invoke`, `start-api`, and
`start-lambda`. Those start a local runtime and were not run. `sync`,
`deploy`, `package`, `logs`, `traces`, `remote`, `delete`, `pipeline`, and
`publish` talk to AWS and were not run.

### cfn-lint

`cfn-lint --help` gives these forms:

```text
cfn-lint test.yaml
cfn-lint -i E3012 -- test.yaml
cfn-lint -x E3012:strict=true -t test.yaml
cfn-lint dir/**/*.yaml
```

The flags it prints: `-t/--template`, `-b/--ignore-bad-template`,
`--ignore-templates`, `--deployment-files`, `--parameters`,
`--parameter-files`, `-f/--format` (`quiet`, `parseable`, `json`, `junit`,
`pretty`, `sarif`), `-l/--list-rules`, `-r/--regions`,
`-i/--ignore-checks`, `-c/--include-checks`, `-m/--mandatory-checks`,
`-e/--include-experimental`, `-x/--configure-rule` as `RuleId:key=value`,
`--config-file`, `-z/--custom-rules`, `-v/--version`, `--output-file`,
`--merge-configs`, and `--non-zero-exit-code` (`informational`, `warning`,
`error`, `none`). Debugging flags: `-D/--debug`, `-I/--info`,
`-L/--list-templates`, `-a/--append-rules`, `-o/--override-spec`,
`-g/--build-graph`, `-s/--registry-schemas`, `-u/--update-specs`. `-u`
downloads CloudFormation specs and was not used. A local lint of a template
file does not call AWS.

### cookiecutter

`cookiecutter --help` usage is
`cookiecutter [OPTIONS] [TEMPLATE] [EXTRA_CONTEXT]...`. Flags: `-V/--version`,
`--no-input`, `-c/--checkout`, `--directory`, `-v/--verbose`, `--replay`,
`--replay-file`, `-f/--overwrite-if-exists`, `-s/--skip-if-file-exists`,
`-o/--output-dir`, `--config-file`, `--default-config`, `--debug-file`,
`--accept-hooks` (`yes`, `ask`, `no`), `-l/--list-installed`,
`--keep-project-on-failure`. The help says `--no-input` deletes cached
resources and redownloads them, and that it cannot be combined with
`--replay`. `cookiecutter` was not run.

### localstack

`localstack --help` prints that the `localstack` CLI is deprecated in favor
of `lstk`, then continues. Options: `-v/--version`, `-d/--debug`,
`-p/--profile`. Commands: `auth`, `completion`, `config`, `logs`,
`restart`, `ssh`, `start`, `status`, `stop`, `update`, `wait`. Advanced
commands: `aws`, `dns`, `ephemeral`, `extensions`, `license`, `pod`,
`replicator`, `state`. `/usr/bin/lstk` is not installed, so the recommended
replacement is absent.

`localstack start --help` defaults to `--docker`, which starts a container.
`--host` is marked deprecated. Other flags: `--no-banner`, `-d/--detached`,
`--network`, `-e/--env`, `-p/--publish`, `-v/--volume`, `--host-dns`,
`-s/--stack` (the help's example values are `localstack:4.5` and
`snowflake`). `start` was not run.

### chevron

`chevron --help` usage is
`chevron [-h] [-v] [-d DATA] [-p PARTIALS_PATH] [-e PARTIALS_EXT] [-l DEF_LDEL] [-r DEF_RDEL] [-w] template`.
`-d` is a JSON data file. `-p` is the partials directory. `-e` defaults to
`mustache`. `-l` and `-r` default to `{{` and `}}`. `-w` warns on each
undefined key.

### lambda-builders

`lambda-builders --help` exits 1 with `JSONDecodeError`. The program reads
one JSON object from its first argument, or from stdin when there is no
argument, and `json.loads` it. `--help` is not a flag. `main` accepts only
the method `LambdaBuilder.build`. Any other `method` is JSON-RPC error
`-32601`, "Method unavailable". The request's `params` carry
`__protocol_version`, `capability` (`language`, `dependency_manager`,
`application_framework`), and the build directories. SAM is the caller.
No build request was sent.

### fastavro

`fastavro --help` usage is
`fastavro [--schema] [--metadata] [--codecs] [--version] [-p] [file ...]`.
It iterates an Avro file and emits records as JSON. `--schema` dumps the
schema, `--metadata` dumps metadata, `--codecs` prints codecs, and
`-p/--pretty` pretty-prints. A file named `-` reads stdin.

### py-build-cmake

`py-build-cmake --help` usage is `py-build-cmake [OPTIONS] COMMAND`. Global
options: `-C/--directory`, `-B/--build-path`, `-V/--verbose`, `-n/--dry`,
`--local`, `--cross`, `-o/--override`, `-v/--version`. `-n` prints the
CMake command and does not run it. Commands:

```text
py-build-cmake configure [--preset PRESET] [--use-build-presets] [--index INDEX]
py-build-cmake build [--preset PRESET] [--config CONFIG] [--index INDEX]
py-build-cmake install [--config CONFIG] [--component COMP] [--index INDEX]
py-build-cmake config format
```

The Ion extension was built by the recipe's PEP 517 backend. This CLI was
not run by hand.

### jsonpath_ng

`jsonpath_ng --help` usage is `jsonpath_ng expression [file ...]`. With no
files it reads stdin. The help's JSONPath summary: `$` is the root,
`` `this` `` is the current object, `path1.path2` descends, `path1|path2`
is a union, `path1..path2` searches in between, a bare name is a field,
`*` is any field, `[*]` is any index, and `[_start_?:_end_?]` is a slice.

### uvicorn

`uvicorn --help` usage is `uvicorn [OPTIONS] APP`. Defaults it prints:
`--host 127.0.0.1`, `--port 8000`, `--reload-delay 0.25`, `--loop auto`,
`--http auto`, `--ws auto`, `--ws-max-size 16777216`, `--ws-max-queue 32`,
`--ws-ping-interval 20.0`, `--ws-ping-timeout 20.0`, per-message deflate
on, `--lifespan auto`, `--interface auto`, `--log-level info`, access log
on, `--timeout-keep-alive 5`, `--timeout-worker-healthcheck 5`.
`--factory` treats `APP` as a zero-argument callable. Further flags cover
reload globs, workers, SSL, proxy headers, and concurrency limits. The
server was not started.

### dateparser-download

`~/.local/bin/dateparser-download --help` and
`/usr/bin/dateparser-download --help` print the same usage:
`dateparser-download [--fasttext FASTTEXT] [--clear]`. `--fasttext` takes
`small` or `large` and downloads a language-detection model. `--clear`
clears cached models. The copy on `PATH` is the user-site script. Neither
flag was run.

### moto_proxy

`moto_proxy --help` usage is `moto_proxy [-H HOST] [-p PORT] [-v]`. The
help shows `HTTPS_PROXY=http://localhost:5005` and then an `aws` command
with `--no-verify-ssl`. That would send the AWS call to the proxy. The
proxy was not started. `moto_server --help` raises
`ModuleNotFoundError: No module named 'flask_cors'` before argument
parsing, as recorded under
[moto's server extra](#motos-server-extra).

## dateparser

`python-dateparser` 1.4.3-1 is installed and owns
`/usr/lib/python3.14/site-packages/dateparser` plus
`/usr/bin/dateparser-download`. `import dateparser` loads
`~/.local/lib/python3.14/site-packages/dateparser/__init__.py`, version
1.3.0, because the user site is earlier on `sys.path`. `command -v
dateparser-download` is `~/.local/bin/dateparser-download`, and that script
imports the user-site `dateparser_cli`. The user-site copy was left in
place. `importlib.metadata.version("dateparser")` therefore reports 1.3.0.
The system dist-info is `dateparser-1.4.3.dist-info`.

The console script on both copies is
`dateparser-download=dateparser_cli.cli:entrance`.

## Repository packages installed with paru

These came from `extra`. The two OpenTelemetry packages came from the local
pkgrel 4 cache, for the reason in
[OpenTelemetry pkgrel 4 and pkgrel 5](#opentelemetry-pkgrel-4-and-pkgrel-5).
Versions are the installed pacman release and the matching distribution
version.

### python-aioitertools 0.13.0-2

Import `aioitertools`. Docstring: itertools and builtins for asyncio and
mixed iterables. It is a dependency of the async AWS client. No console
script. The async functions, each returning an async iterator unless noted:

`accumulate`, `batched`, `combinations`, `combinations_with_replacement`,
`compress`, `count`, `cycle`, `dropwhile`, `enumerate`, `filterfalse`,
`groupby`, `islice`, `iter`, `map`, `permutations`, `product`, `repeat`,
`starmap`, `takewhile`, `tee`, `zip`, `zip_longest`.

Consumers that return a concrete value: `all`, `any`, `list`, `max`, `min`,
`next`, `set`, `sum`, `tuple`. `chain` is the class `Chain`. Submodules:
`asyncio`, `builtins`, `helpers`, `itertools`, `types`.

### python-aiobotocore 3.9.2-1

Import `aiobotocore`. Docstring: async client for AWS services, wrapping
botocore with aiohttp or httpx. The package `__init__` exports nothing.
The session factory is `aiobotocore.session.get_session(env_vars=None)`,
which returns `AioSession`.

```text
AioSession(session_vars=None, event_hooks=None,
           include_builtin_handlers=True, profile=None)
AioBaseClient(...)
AioClientCreator(...)
ClientCreatorContext(coro)
```

`get_session` was imported and not called. Calling it and then `create_client`
would use ambient credentials. Submodules include `session`, `client`,
`credentials`, `httpsession`, `httpxsession`, `paginate`, `retries`,
`signers`, `stub`, and `waiter`.

### python-aws-sam-translator 1.113.0-1

Import `samtranslator`. The package `__init__` exports nothing. The
translator class is `samtranslator.translator.translator.Translator`. Its
docstring says it translates SAM templates into CloudFormation templates.

```text
Translator(managed_policy_map, sam_parser, plugins=None,
           boto_session=None, metrics=None)
Translator.translate(sam_template, parameter_values,
                     feature_toggle=None, passthrough_metadata=False,
                     get_managed_policy_map=None) -> dict
```

`translate` returns a copy of the template with SAM resources replaced by
CloudFormation resources. Passing a `boto_session` makes the translator read
that session's region. This note did not construct one. Other submodules:
`parser`, `plugins`, `model`, `swagger`, `validator`, `region_configuration`,
`policy_template_processor`.

### python-aws-xray-sdk 2.15.0-4

Import `aws_xray_sdk`. The top of the package exposes `SDKConfig` and
`global_sdk_config`. The recorder API is `aws_xray_sdk.core`:

```text
patch(modules_to_patch, raise_errors=True, ignore_module_patterns=None)
patch_all(double_patch=False)
AWSXRayRecorder()
xray_recorder   # an AsyncAWSXRayRecorder instance created at import
```

`__all__` there is `patch`, `patch_all`, `xray_recorder`, `AWSXRayRecorder`.
`patch` and `patch_all` monkeypatch libraries in the current process. They
were not called. Subpackages: `core`, `ext`, `sdk_config`, `version`.

### python-requests-aws4auth 1.4.0-1

Import `requests_aws4auth`. Docstring: AWS signature version 4
authentication for Requests. No console script.

```text
AWS4Auth(*args, **kwargs)
StrictAWS4Auth(*args, **kwargs)
PassiveAWS4Auth(*args, **kwargs)
AWS4SigningKey(secret_key, region, service, date=None, store_secret_key=True)
```

Errors: `RequestsAws4AuthException`, `DateMismatchError`, `NoSecretKeyError`.
An `AWS4Auth` instance is a Requests auth handler. Building one needs a
signing key, so this note stopped at the import.

### python-s3fs 2026.9.0-1

Import `s3fs`. fsspec filesystem over S3. No console script.
`python-fsspec` 2026.9.0-1 is the matching fsspec.

```text
S3FileSystem(anon=False, endpoint_url=None, key=None, secret=None, token=None,
             use_ssl=True, client_kwargs=None, requester_pays=False,
             default_block_size=None, default_fill_cache=True,
             default_cache_type="readahead", version_aware=False,
             config_kwargs=None, s3_additional_kwargs=None, session=None,
             username=None, password=None, cache_regions=False,
             asynchronous=False, loop=None, max_concurrency=10,
             fixed_upload_size=False, local_expiry_check=False, **kwargs)
S3File(s3, path, mode="rb", block_size=52428800, acl=False, version_id=None,
       fill_cache=True, s3_additional_kwargs=None, autocommit=True,
       cache_type="readahead", requester_pays=False, cache_options=None,
       size=None)
S3Map(root, s3, check=False, create=False)
```

`S3FileSystem()` with the defaults reads ambient credentials and was not
constructed. `add_retryable_error(exc)` and `set_custom_error_handler(func)`
adjust the filesystem's error policy. Submodules: `core`, `errors`,
`mapping`, `utils`.

### python-cfn-lint 1.57.1-1

Import `cfnlint`. The CLI is `cfn-lint` via `cfnlint.runner:main`. The
library functions take a template string or a path and return a list of
`Match` objects. They do not call AWS.

```text
cfnlint.lint(s, rules=None, regions=None, config=None) -> list[Match]
cfnlint.lint_all(s) -> list[Match]
cfnlint.lint_file(template: Path, config=None) -> list[Match]
cfnlint.lint_by_config(config) -> list[Match]
cfnlint.Template(filename, template, regions=None, parameter_sets=None)
cfnlint.ConfigMixIn(cli_args=None, **kwargs)
cfnlint.Rules(rules=None, **kwargs)
```

Submodules include `rules`, `schema`, `template`, `runner`, `formatters`,
`decode`, and `graph`.

### python-cookiecutter 2.7.1-1

Import `cookiecutter`. The package top exports `version(distribution_name)`.
Project generation is `cookiecutter.main.cookiecutter`. The CLI is
`cookiecutter`.

```text
cookiecutter(template, checkout=None, no_input=False, extra_context=None,
             replay=None, overwrite_if_exists=False, output_dir=".", ...)
generate_context(context_file="cookiecutter.json", default_context=None,
                 extra_context=None) -> dict
generate_files(repo_dir, context=None, output_dir=".",
               overwrite_if_exists=False, skip_if_file_exists=False,
               accept_hooks=True, ...)
get_user_config(config_file=None, default_config=False) -> dict
```

`cookiecutter()` can clone a remote template. It was not called.

### python-docker 7.1.0-4

Import `docker`. No console script. This is the Docker SDK, used by
LocalStack and by SAM's container builds. Nothing here constructed a client
or talked to a daemon.

```text
docker.from_env(**kwargs)
DockerClient(*args, **kwargs)
APIClient(base_url=None, version=None, timeout=60, tls=False,
          user_agent="docker-sdk-python/7.1.0", num_pools=None,
          credstore_env=None, use_ssh_client=False, max_pool_size=10)
TLSConfig(client_cert=None, ca_cert=None, verify=None)
Context(name, orchestrator=None, host=None, endpoints=None, tls=False)
ContextAPI()
```

### OpenTelemetry AWS packages

Both are pacman `0.66b1-4`, installed from `/var/cache/pacman/pkg/`. The
mirror split and the unused pkgrel 5 install are in
[OpenTelemetry pkgrel 4 and pkgrel 5](#opentelemetry-pkgrel-4-and-pkgrel-5).

`python-opentelemetry-instrumentation-aws-lambda` has distribution version
`0.66b1`. Import
`opentelemetry.instrumentation.aws_lambda.AwsLambdaInstrumentor`.
`_instrument` returns immediately unless `AWS_LAMBDA_FUNCTION_NAME` is set,
so importing it on this host does not patch a handler. The constructor
accepts `tracer_provider`, `meter_provider`, and `event_context_extractor`.
Files: `__init__.py`, `_sqs.py`, `package.py`, `version.py`.

`python-opentelemetry-propagator-aws-xray` has distribution version
`1.1.0.dev` (dist-info `opentelemetry_propagator_aws_xray-1.1.0.dev0`).
Import `opentelemetry.propagators.aws`.

```text
AwsXRayPropagator()
AwsXRayLambdaPropagator()
```

Both are OpenTelemetry propagators for the X-Ray trace header.

### python-jsonpath-ng 1.8.0-1

Import `jsonpath_ng`. CLI `jsonpath_ng`. The parser is `parse(string)`.
Path nodes: `JSONPath`, `Child`, `Fields`, `Index`, `Slice`, `Where`,
`WhereNot`, `Descendants`, `Union`, `Intersect`, `Parent`, `Root`, `This`,
`DatumInContext`, `AutoIdForDatum`. The module also binds itertools names
(`tee`, `chain`, `islice`, and the rest). Those are the standard-library
functions, not a JSONPath API. awswrangler lists this package as the
JSONPath provider for its optional path helpers.

### python-tenacity 9.2.1-1

Import `tenacity`. Retry helper pulled in by the recipes. `__all__` has 55
names. The decorator and the two runners:

```text
retry(*dargs, **dkw)
Retrying(sleep=sleep, stop=..., wait=..., retry=..., before=..., after=...,
         before_sleep=None, reraise=False, retry_error_cls=RetryError,
         retry_error_callback=None, name=None, enabled=True)
AsyncRetrying(...)   # same shape, async callbacks
```

Stop, wait, and retry predicates are further classes on the same module
(`retry_if_exception`, `retry_all`, `retry_any`, and the `stop_*` / `wait_*`
classes, 42 classes in total). Log hooks: `before_log`, `after_log`,
`before_sleep_log`, and the `*_nothing` no-ops.

### python-schema 0.7.8-2

Import `schema`. Docstring: a library for validating Python data structures.

```text
Schema(schema, error=None, ignore_extra_keys=False, name=None,
       description=None, as_reference=False)
And(*args, error=None, ignore_extra_keys=False, schema=None)
Or(*args, only_one=False, **kwargs)
Regex(pattern_str, flags=0, error=None)
Optional(*args, **kwargs)
Use(callable_, error=None)
Forbidden(*args, **kwargs)
Const(schema, error=None, ignore_extra_keys=False, name=None,
      description=None, as_reference=False)
Literal(value, description=None, title=None)
```

Failures are `SchemaError` and the subclasses `SchemaWrongKeyError`,
`SchemaMissingKeyError`, `SchemaForbiddenKeyError`,
`SchemaUnexpectedTypeError`, `SchemaOnlyOneAllowedError`.

### python-dnslib 0.9.26-3

Import `dnslib`. DNS codec used by LocalStack's DNS stub. The records a
caller builds:

```text
DNSRecord(header=None, questions=None, rr=None, q=None, a=None, auth=None, ar=None)
DNSHeader(id=None, bitmap=None, q=0, a=0, auth=0, ar=0, **args)
DNSQuestion(qname=None, qtype=1, qclass=1)
RR(rname=None, rtype=1, rclass=1, ttl=0, rdata=None)
ZoneParser(zone, origin="", ttl=0)
```

Rdata classes include `A`, `AAAA`, `CNAME`, `MX`, `NS`, `PTR`, `SOA`, `SRV`,
`TXT`, `CAA`, `DS`, `DNSKEY`, `NSEC`, `RRSIG`, `TLSA`, `SSHFP`, `LOC`,
`NAPTR`, `HTTPS`, and `EDNS0`. `DNSRecord` is the parse and pack object.
`chain` and `zip_longest` on this module are itertools re-exports.

### python-pyotp 2.10.0-1

Import `pyotp`. One-time passwords. The library classes are `OTP`, `HOTP`,
and `TOTP`. `parse_qsl`, `urlparse`, `unquote`, and `split` on the package
top are standard-library re-exports.

```text
OTP(s, digits=6, digest=hashlib.sha1, name=None, issuer=None)
HOTP(s, digits=6, digest=None, name=None, issuer=None, initial_count=0)
TOTP(s, digits=6, digest=None, name=None, issuer=None, interval=30)
parse_uri(uri) -> OTP
random_base32(length=32, chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") -> str
random_hex(length=40, chars="ABCDEF0123456789") -> str
```

Submodules: `otp`, `hotp`, `totp`, `utils`, `compat`, `contrib`.

### python-typeguard 4.6.0-1

Import `typeguard`. Distribution version 4.6.0. `typeguard.__version__`
raises `AttributeError` because the attribute is lazy; the version comes
from `importlib.metadata.version("typeguard")`. jsii declares
`typeguard==2.13.3`. This install keeps 4.6.0. See [the pin tests](#pins-that-stay-unmet).

### python-fastavro 1.13.1-1

Import `fastavro`. CLI `fastavro`. Avro reader and writer used by the Glue
schema registry. `__all__` has 24 names. The Python-visible callables:

```text
reader(fo, reader_schema=None, return_record_name=False,
       return_record_name_override=False, handle_unicode_errors="strict",
       return_named_type=False, return_named_type_override=False)
block_reader(fo, reader_schema=None, ...)
json_reader(fo, schema, reader_schema=None, *, decoder=AvroJSONDecoder)
json_writer(fo, schema, records, *, write_union_type=True, validator=False,
            encoder=AvroJSONEncoder, strict=False,
            strict_allow_default=False, disable_tuple_notation=False)
```

`writer`, `schemaless_reader`, `schemaless_writer`, `is_avro`, and `validate`
are Cython functions on the same module. Submodules include `schema`, `read`,
`write`, `json_read`, `json_write`, `validation`, `logical_readers`, and
`logical_writers`.

### python-py-build-cmake 0.5.1-1

Import `py_build_cmake`. The package `__init__` exports nothing. The CLI is
`py-build-cmake` at `py_build_cmake.cli:cli`. Click commands in that module:
`configure`, `build`, `install`, `config`, `format`, plus
`cmake_command(directory, build_path, verbose, dry, cross, local, override)`.
amazon-ion's build backend is `py_build_cmake.build`, and the recipe bounds
this package to `>=0.5.0` and `<0.6.0`. The installed 0.5.1 satisfies that.
The Ion extension built with it on this host.

### uvicorn 0.54.0-1 and python-opt_einsum 3.4.0-2

Both were already installed from `extra`. A second recipe for each was
deleted because the names collide: `uvicorn` owns `/usr/bin/uvicorn` and
provides no `python-uvicorn` package; `python-opt_einsum` owns `opt_einsum`
and provides no hyphenated package.

`uvicorn` 0.54.0 satisfies bedrock-agentcore's `uvicorn>=0.34.2`. The public
entry is `uvicorn.run(app, *, host="127.0.0.1", port=8000, ...)`, with
`Config` and `Server` beside it. The live signature carries the full server
option set (HTTP, websockets, SSL, reload, workers, timeouts). `run` was not
called.

`opt_einsum` 3.4.0 is the contraction library the Braket simulator imports.

```text
contract(subscripts, *operands, out=None, use_blas=True, optimize=True,
         memory_limit=None, backend="auto", **kwargs)
contract_expression(subscripts, *shapes, constants=None, use_blas=True,
                    optimize=True, memory_limit=None, **kwargs)
contract_path(subscripts, *operands, use_blas=True, optimize=True,
              memory_limit=None, shapes=False, **kwargs)
get_symbol(i) -> str
shared_intermediates(cache=None)
```

Optimizers on the module: `DynamicProgramming`, `BranchBound`, `RandomGreedy`.

## AUR packages

`paru` installed these. Two of them are behind current PyPI and stay there:
a newer stub package would conflict with `python-boto3-stubs`, and the
request was to install what paru ships.

| Pacman package | Distribution | Import |
|---|---|---|
| `python-aws-lambda-powertools` 3.38.0-1 | `aws-lambda-powertools` 3.38.0 | `aws_lambda_powertools` |
| `python-opensearch` 3.2.0-2 | `opensearch-py` 3.2.0 | `opensearchpy` |
| `python-boto3-stubs` 1.35.36-3 | `boto3-stubs` 1.35.36 | none |
| `python-botocore-stubs` 1.31.64-2 | none | none |
| `python-localstack-client` 2.12-1 | `localstack-client` 2.12 | `localstack_client` |
| `python-awscli-local` 0.22.0-1 | `awscli-local` 0.22.0 | none; binary `awslocal` |
| `aws-sam-cli` 1.138.0-1 | `aws-sam-cli` 1.138.0 | `samcli` |
| `python-events` 0.5-1 | `Events` 0.5 | `events` |
| `python-chevron` 0.14.0-1 | `chevron` 0.14.0 | `chevron` |
| `python-aws-lambda-builders` 1.54.0-1 | `aws_lambda_builders` 1.54.0 | `aws_lambda_builders` |

PyPI at the time of the plan had `boto3-stubs` 1.43.121 and `aws-sam-cli`
1.170.0. The installed AUR versions are the ones in the table.

### aws_lambda_powertools

Docstring: top-level package for Lambda Python Powertools. `__all__` is four
names. No console script.

```text
Logger(service=None, level=None, child=False, sampling_rate=None, stream=None,
       logger_formatter=None, logger_handler=None,
       log_uncaught_exceptions=False, json_serializer=None,
       json_deserializer=None, json_default=None, datefmt=None,
       use_datetime_directive=False, log_record_order=None, utc=False,
       use_rfc3339=False, serialize_stacktrace=True, buffer_config=None, **kwargs)
Metrics(service=None, namespace=None, provider=None, function_name=None)
Tracer(service=None, disabled=None, auto_patch=None, patch_modules=None,
       provider=None)
single_metric(name, unit, value, resolution=60, namespace=None,
              default_dimensions=None)
```

`single_metric` is a generator context that yields a `SingleMetric`.
`Tracer` can patch modules when constructed; it was not constructed.
Subpackages: `event_handler`, `exceptions`, `logging`, `metrics`,
`middleware_factory`, `shared`, `tracing`, `utilities`, `warnings`.

### opensearchpy

Import `opensearchpy`, distribution `opensearch-py` 3.2.0. `__all__` has 108
names: 9 functions and 97 classes, plus the `connections` submodule. The
query constructors at the top are `Q(name_or_query="match_all", **params)`,
`A(name_or_agg, filter=None, **params)`, and `SF(name_or_sf, **params)`.
`analyzer(name_or_instance, type=None, **kwargs)` builds an analyzer.
The client class lives in that 97-name set. This note imported the package
and did not open a connection. awswrangler's `opensearch` submodule is a
separate pandas-shaped wrapper over a client.

### boto3-stubs and botocore-stubs

`import boto3_stubs` raises `ModuleNotFoundError`. The files are type stubs.
`python-boto3-stubs` installs `boto3-stubs/**/*.pyi`, `boto3-stubs/py.typed`,
and two dist-info directories: `boto3_stubs-1.35.36.dist-info` (top-level
name `boto3-stubs`) and `mypy_boto3-1.35.36.dist-info` (top-level name
`mypy_boto3`). A type checker reads those `.pyi` files. They describe boto3
1.35.36, while the installed boto3 is 1.43.108, so the stubs are older than
the runtime they annotate.

`python-botocore-stubs` 1.31.64-2 owns only
`/usr/share/licenses/python-botocore-stubs/LICENSE`. It ships no module, no
`.pyi`, and no dist-info. `importlib.metadata.distribution("botocore-stubs")`
raises `PackageNotFoundError`. There is nothing to import.

### localstack-client

`import localstack_client` succeeds and the package `__init__` is empty.
The API is the three submodules.

`localstack_client.session`:

```text
Session(...)
client(*args, **kwargs)
resource(*args, **kwargs)
```

`client` and `resource` build a boto3-shaped client aimed at LocalStack.
They were not called.

`localstack_client.config`:

```text
parse_localstack_host(given) -> tuple[str, int]
get_service_endpoints(localstack_host=None) -> dict[str, str]
get_service_endpoint(...)
get_service_port(service) -> int | None
get_service_ports() -> dict[str, int]
```

`localstack_client.patch`:

```text
enable_local_endpoints()
disable_local_endpoints()
patch_expand_host_prefix()
```

`enable_local_endpoints` patches boto3 in-process. It was not called.

### events, chevron, and lambda builders

`events` 0.5 exports two names:

```text
Events(events=None, event_slot_cls=events.events._EventSlot)
EventsException(*args, **kwargs)
```

`chevron` 0.14.0 is a Mustache renderer. CLI `chevron` calls `cli_main()`.

```text
render(template="", data={}, partials_path=".", partials_ext="mustache",
       partials_dict={}, padding="", def_ldel="{{", def_rdel="}}",
       scopes=None, warn=False)
main(template, data=None, **kwargs)
cli_main()
ChevronError(*args, **kwargs)
```

`aws_lambda_builders` documents itself as the AWS Lambda Builder Library.
The package top exports `RPC_PROTOCOL_VERSION` only. The builder class is
`aws_lambda_builders.builder.LambdaBuilder`. The CLI `lambda-builders` is
`aws_lambda_builders.__main__:main`, which speaks the RPC protocol SAM uses
to request a build.

```text
LambdaBuilder(language, dependency_manager, application_framework,
              supported_workflows=None)
LambdaBuilder.build(source_dir, artifacts_dir, scratch_dir, manifest_path,
                    runtime=None, unpatched_runtime=None, optimizations=None,
                    options=None, executable_search_paths=None, mode=None,
                    download_dependencies=True, dependencies_dir=None,
                    combine_dependencies=True, architecture="x86_64",
                    is_building_layer=False, experimental_flags=None,
                    build_in_source=None)
```

`build` downloads dependencies when asked and was not called.

### aws-sam-cli

Distribution `aws-sam-cli` 1.138.0, script `sam=samcli.cli.main:cli`. `sam`
is the CLI for building, packaging, and invoking Lambda applications. The
installed release is the AUR 1.138.0 package. PyPI's 1.170.0 was left
uninstalled. `sam` was not invoked.

## Local recipes

Twenty-eight recipes in `~/Github/PKGBUILDs` were built and installed on
2026-10-29. `python-smdebug-rulesconfig` is pkgrel 3.
`python-aws-cdk-cloud-assembly-schema` is pkgrel 2. The others are pkgrel 1.
`python-boltons` is the local wheel recipe 26.2.0-1. `paru -Sp
python-boltons`, including `paru --aur -Sp`, still resolves to the BlackArch
25.0.0-2 archive, so boltons is not installed through paru.

### python-boltons 26.2.0-1

Import `boltons`. The package `__init__` exports nothing. Each tool is a
submodule, imported as `boltons.<name>`. Public classes and functions
measured on each submodule:

| Submodule | Public names |
|---|---|
| `cacheutils` | `CachedFunction`, `CachedMethod`, `LRI`, `LRU`, `MinIDMap`, `ThresholdCounter`, `cached`, `cachedmethod`, `cachedproperty`, `make_cache_key`, `make_sentinel` |
| `debugutils` | `pdb_on_signal`, `pdb_on_exception`, `wrap_trace` |
| `deprutils` | `DeprecatableModule`, `deprecate_module_member` |
| `dictutils` | `MultiDict`, `OMD`, `OrderedMultiDict`, `OneToOne`, `ManyToMany`, `subdict`, `FrozenDict` |
| `easterutils` | `gobs_program` |
| `ecoutils` | `dumps`, `get_profile`, `get_profile_json`, `get_python_info`, `main` |
| `excutils` | `ExceptionCauseMixin` |
| `fileutils` | `mkdir_p`, `atomic_save`, `AtomicSaver`, `FilePerms`, `iter_find_files`, `copytree` |
| `formatutils` | `DeferredValue`, `get_format_args`, `tokenize_format_str`, `construct_format_field_str`, `infer_positional_format_args`, `BaseFormatField` |
| `funcutils` | `CachedInstancePartial`, `FunctionBuilder`, `InstancePartial`, `copy_function`, `dir_dict`, `format_invocation`, `format_exp_repr`, `format_nonexp_repr`, `get_module_callables`, `inspect_formatargspec`, `mro_items`, `noop`, and further helpers (24 callables) |
| `gcutils` | `get_all`, `GCToggler` |
| `ioutils` | `MultiFileReader`, `SpooledBytesIO`, `SpooledStringIO`, `EncodedFile`, `is_text_fileobj` |
| `iterutils` | `bucketize`, `chunked`, `chunked_iter`, `chunk_ranges`, `first`, `backoff`, `backoff_iter`, `GUIDerator`, `SequentialGUIDerator`, `PathAccessError` (50 callables) |
| `jsonutils` | `JSONLIterator`, `reverse_iter_lines` |
| `listutils` | `BList`, `BarrelList` |
| `mathutils` | `Bits`, `ceil`, `clamp`, `floor` |
| `mboxutils` | `mbox_readonlydir` |
| `namedutils` | `namedlist`, `namedtuple` |
| `pathutils` | `augpath`, `shrinkuser`, `expandpath` |
| `queueutils` | `PriorityQueue`, `BasePriorityQueue`, `HeapPriorityQueue`, `SortedPriorityQueue` |
| `setutils` | `IndexedSet`, `complement` |
| `socketutils` | `BufferedSocket`, `NetstringSocket`, `Timeout`, `ConnectionClosed`, `MessageTooLong` |
| `statsutils` | `Stats`, `mean`, `median`, `variance`, `std_dev`, `skewness`, `kurtosis`, `iqr`, `trimean`, `describe`, `format_histogram_counts` |
| `strutils` | `camel2under`, `under2camel`, `slugify`, `ordinalize`, `cardinalize`, `pluralize`, `singularize`, `asciify`, `is_ascii`, `is_uuid`, `html2text`, `strip_ansi`, `bytes2human`, `find_hashtags`, `a10n`, `gzip_bytes` (34 callables) |
| `tableutils` | `Table` |
| `tbutils` | `ExceptionInfo`, `TracebackInfo`, `Callpoint`, `ParsedException`, `print_exception`, and the `Contextual*` variants |
| `timeutils` | `daterange`, `isoparse`, `parse_timedelta`, `relative_time`, `dt_to_timestamp`, `ConstantTZInfo`, `LocalTZInfo`, `USTimeZone` |
| `typeutils` | `classproperty`, `get_all_subclasses`, `issubclass` |
| `urlutils` | `URL`, `parse_url`, `find_all_links`, `QueryParamDict`, `URLParseError` |

`iterutils` has 50 public callables and `funcutils` 24. The table names the
ones a caller reaches first; the rest are on the submodule. `easterutils`
exports `gobs_program` only. The Braket SDK depends on this boltons, which
is why the BlackArch 25.0.0 package was not used.

### python-scramp 1.4.9-1

Import `scramp`. SCRAM authentication for the Redshift driver. The AUR
package is 1.5.0, and redshift-connector 2.2.0 requires `scramp<1.5`, so the
recipe holds 1.4.9. License MIT-0.

```text
ScramClient(mechanisms, username, password, channel_binding=None, c_nonce=None)
ScramMechanism(mechanism="SCRAM-SHA-256")
ScramException(message, server_error=None)
make_channel_binding(name, ssl_socket)
```

### python-plux 1.16.0-1

Import `plux`. Plugin loader used by LocalStack. No runtime requirements.

```text
plugin(namespace, name=None, should_load=None, load=None)
PluginManager(namespace, load_args=None, load_kwargs=None, listener=None,
              finder=None, filters=None)
Plugin(self, *args, **kwargs)
FunctionPlugin(fn, should_load=None, load=None)
PluginSpec(namespace, name, factory)
PluginContainer()
PluginFinder()
PluginSpecResolver()
PluginLifecycleListener()
CompositePluginLifecycleListener(initial=None)
PluginDisabled(namespace, name, reason=None)
PluginException(message, namespace=None, name=None)
```

`plugin` is the decorator that registers a callable in a namespace.
`PluginManager` loads that namespace.

### python-jsonconversion 2.0.0-1

Import `jsonconversion`. Dependency of amazon-ion. The three functions that
belong to it:

```text
get_all_args(func)
getfullargspec(func)
version(distribution_name) -> str
```

`ClassType`, `basestring`, and `PackageNotFoundError` on the module are
compatibility re-exports, as are the `builtins` and `sys` module objects.
License is the 2-clause BSD text shipped in the recipe.

### python-publication 0.0.3-1

Import `publication` (a module, `publication.py`). Docstring: it keeps a
public API from leaking private names through introspection.

```text
publish()
```

`__all__` is `publish` and `__version__`. Homepage is `glyph/publication`.
jsii and the CDK schema package depend on it.

### python-openpulse 1.0.1-1

Import `openpulse`. OpenPulse parser. `python-antlr4` 4.13.2-3 satisfies
both `>=4.7,<4.14` here and the simulator's tighter `>=4.13.2,<4.13.3`.
`python-openqasm3` 1.0.1-1 is installed.

```text
parse(input_: str, permissive: bool = False) -> openqasm3.ast.Program
```

Submodules: `ast`, `parser`, `spec`.

### python-awswrangler 3.18.0-1

Import `awswrangler`. Pandas-shaped helpers over boto3. The package top
exports enums and submodules, and no functions of its own. `EngineEnum` and
`MemoryFormatEnum` are the two classes. `config`, `engine`, and
`memory_format` are the process-wide settings objects. Service functions are
re-exported, so `inspect.isfunction` on the submodule returns nothing; the
names below are each submodule's `__all__`.

Every function that reads or writes a service uses ambient credentials.
None of them were called.

| Submodule | Count | Names |
|---|---|---|
| `s3` | 56 | `copy_objects`, `merge_datasets`, `delete_objects`, `describe_objects`, `get_bucket_region`, `size_objects`, `does_object_exist`, `list_buckets`, `list_directories`, `list_objects`, `read_deltalake`, `read_parquet`, `read_parquet_metadata`, `read_parquet_table`, `read_orc`, `read_orc_metadata`, `read_orc_table`, `read_csv`, and further readers and writers |
| `athena` | 26 | `read_sql_query`, `read_sql_table`, `create_athena_bucket`, `describe_table`, `get_query_columns_types`, `get_query_execution`, `get_query_executions`, `get_query_results`, `get_named_query_statement`, `get_work_group`, `generate_create_query`, `list_query_executions`, `repair_table`, `create_spark_session`, `run_spark_calculation`, `create_ctas_table`, `show_create_table`, `start_query_execution` |
| `catalog` | 46 | `add_column`, `add_csv_partitions`, `add_json_partitions`, `add_parquet_partitions`, `add_orc_partitions`, `does_table_exist`, `delete_column`, `drop_duplicated_columns`, `extract_athena_types`, `rename_duplicated_columns`, `sanitize_column_name`, `sanitize_dataframe_columns_names`, `sanitize_table_name`, `create_csv_table`, `create_database` |
| `quicksight` | 38 | `get_dashboard_id`, `get_dashboard_ids`, `get_data_source_arn`, `get_data_source_arns`, `get_data_source_id`, `get_data_source_ids`, `get_dataset_id`, `get_dataset_ids`, `get_template_id`, `get_template_ids`, `list_dashboards`, `list_data_sources` |
| `timestream` | 13 | `create_database`, `create_table`, `delete_database`, `delete_table`, `list_databases`, `list_tables`, `query`, `write`, `batch_load`, `batch_load_from_files`, `wait_batch_load_task`, `unload_to_files` |
| `neptune` | 11 | `connect`, `execute_gremlin`, `execute_opencypher`, `execute_sparql`, `to_property_graph`, `to_rdf_graph`, `bulk_load`, `bulk_load_from_files`, `GremlinParser`, `flatten_nested_df`, `BulkLoadParserConfiguration` |
| `opensearch` | 10 | `connect`, `create_collection`, `create_index`, `delete_index`, `index_csv`, `index_documents`, `index_df`, `index_json`, `search`, `search_by_sql` |
| `dynamodb` | 9 | `delete_items`, `execute_statement`, `get_table`, `put_csv`, `put_df`, `put_items`, `put_json`, `read_partiql_query`, `read_items` |
| `redshift` | 9 | `connect`, `connect_temp`, `copy`, `copy_from_files`, `read_sql_query`, `read_sql_table`, `to_sql`, `unload`, `unload_to_files` |
| `data_quality` | 5 | `create_recommendation_ruleset`, `create_ruleset`, `evaluate_ruleset`, `get_ruleset`, `update_ruleset` |
| `oracle` | 4 | `connect`, `read_sql_query`, `read_sql_table`, `to_sql` |
| `sqlserver` | 4 | `connect`, `read_sql_query`, `read_sql_table`, `to_sql` |
| `bedrock` | 3 | `describe_invoke_batch`, `invoke_batch`, `read_invoke_batch` |
| `cleanrooms` | 2 | `read_sql_query`, `wait_query` |
| `data_api` | 2 | `redshift`, `rds` |

`chime`, `cloudwatch`, `emr`, `emr_serverless`, `exceptions`, `mysql`,
`postgresql`, `secretsmanager`, `sts`, and `typing` import and have no
`__all__`. Their functions are attributes of those submodules. The Glue
catalog helpers and the S3 readers are the paths that match Athena and S3
work on this project. `awswrangler.redshift.connect` is optional at runtime
and needs the Redshift driver, which is installed separately below.

### python-aws-encryption-sdk 4.0.7-1

Import `aws_encryption_sdk`. Docstring: high-level AWS Encryption SDK client
functions. Encrypting needs a KMS key or a local master key and was not done.

```text
EncryptionSDKClient(*args, **kwargs)
EncryptionSDKClientConfig(commitment_policy=REQUIRE_ENCRYPT_REQUIRE_DECRYPT,
                          max_encrypted_data_keys=None)
EncryptorConfig(source, commitment_policy, signature_policy=ALLOW_ENCRYPT_ALLOW_DECRYPT,
                max_encrypted_data_keys=None, materials_manager=None,
                key_provider=None, source_length=None, line_length=131072,
                encryption_context=NOTHING, algorithm=None, frame_length=4096)
DecryptorConfig(source, commitment_policy, signature_policy=ALLOW_ENCRYPT_ALLOW_DECRYPT,
                max_encrypted_data_keys=None, materials_manager=None,
                key_provider=None, source_length=None, line_length=131072,
                max_body_length=None, encryption_context=None)
StreamEncryptor(**kwargs)
StreamDecryptor(**kwargs)
StrictAwsKmsMasterKeyProvider(**kwargs)
DiscoveryAwsKmsMasterKeyProvider(**kwargs)
DefaultCryptoMaterialsManager(master_key_provider)
CachingCryptoMaterialsManager(cache, max_age, max_messages_encrypted=4294967296,
                              max_bytes_encrypted=9223372036854775807,
                              partition_name=None, master_key_provider=None,
                              backing_materials_manager=None)
LocalCryptoMaterialsCache(capacity)
NullCryptoMaterialsCache()
Algorithm(algorithm_id, encryption, message_format_version, ...)
CommitmentPolicy()
SignaturePolicy()
KMSMasterKeyProviderConfig(botocore_session=NOTHING, key_ids=NOTHING,
                           region_names=NOTHING, grant_tokens=NOTHING,
                           discovery_filter=None, discovery_region=None)
```

`AWSEncryptionSDKClientError` is the client error. Submodules: `caches`,
`exceptions`, `identifiers`, `internal`, `key_providers`,
`materials_managers`, `streaming_client`, `structures`. The MPL extra is not
packaged. Installed `cryptography` 50.0.2 meets the SDK's cryptography floor.

### python-aws-secretsmanager-caching 1.2.0-1

Import `aws_secretsmanager_caching`. Docstring: high-level Secrets Manager
caching client. `SecretCache` takes a botocore or boto3 client. No client
was passed.

```text
SecretCache(config=SecretCacheConfig(), client=None)
SecretCacheConfig(**kwargs)
InjectSecretString(secret_id, cache)
InjectKeywordedSecretString(secret_id, cache, **kwargs)
```

`InjectSecretString` is a decorator that pulls a cached secret into a
function argument. It was not applied.

### python-aws-bedrock-token-generator 1.1.0-1

Import `aws_bedrock_token_generator`. Builds a bearer token for a Bedrock
call. `provide_token` reads credentials from the supplied provider or from
the ambient botocore chain and returns a string. It was not called. A token
minted here would be a credential, and this note does not record one.

```text
BedrockTokenGenerator()
provide_token(region=None, aws_credentials_provider=None,
              expiry=timedelta(seconds=43200)) -> str
```

The default lifetime is 12 hours.

### python-pyathena 4.2.1-1

Import `pyathena`. Docstring: DB API 2.0 interface to Amazon Athena,
`connect()`, `aio_connect()`, and type objects. The AUR package is 3.17.1
and was not used. boto3 1.43.108 satisfies `>=1.43.31`. fsspec 2026.9.0
satisfies `>=2026.9.0`. The pandas extra wants `pandas>=3`. Installed
`python-pandas` is 2.3.3-7.1, so that extra is not declared. SQLAlchemy
2.0.54 and pyarrow 25.0.1 are installed and were not wired in as an extra.

```text
connect(**kwargs) -> Connection
aio_connect(**kwargs) -> AioConnection
ExecuteOptions(work_group=None, s3_staging_dir=None, cache_size=0,
               cache_expiration_time=0, result_reuse_enable=None,
               result_reuse_minutes=None, paramstyle=None,
               on_start_query_execution=None, result_set_type_hints=None)
```

DB-API exceptions on the module: `Warning`, `Error`, `InterfaceError`,
`DatabaseError`, `DataError`, `OperationalError`, `IntegrityError`,
`InternalError`, `ProgrammingError`, `NotSupportedError`. Type objects:
`STRING`, `BINARY`, `NUMBER`, `DATETIME`, `DATE`, `TIME`, `BOOLEAN`, `JSON`,
plus constructors `Date`, `Time`, `Timestamp`, `Binary`. `apilevel`,
`threadsafety`, and `paramstyle` are the DB-API module constants.
`connect()` opens an Athena session and was not called.

Package files besides `__init__`: `aio`, `arrow`, `async_cursor`, `common`,
`connection`, `converter`, `cursor`, `error`, `filesystem`, `formatter`,
`glue`, `model`, `options`, `pandas`, `parser`, `polars`, `result_set`,
`s3fs`, `spark`, `sqlalchemy`, `util`.

### python-oqpy 0.3.11-1

Import `oqpy`. OpenQASM 3 builder used by the Braket SDK. The Braket pin
`oqpy>=0.3.7,<0.4.0` admits 0.3.11. `Program` is the object that collects
statements.

```text
Program(version="3.0", simplify_constants=True)
Qubit(name, size=None, needs_declaration=True, annotations=())
If(program, condition)
Else(program)
While(program, condition)
ForIn(program, iterator, identifier_name=None, identifier_type=IntVar)
Box(program, duration=None)
Cal(program)
gate(program, qubits, name, arguments=None, declare_here=False)
defcal(program, qubits, name, arguments=None, return_type=None)
subroutine(func, annotations=())
declare_extern(name, args, return_type=None, annotations=())
declare_waveform_generator(name, argtypes, annotations=())
make_duration(time)
convert_float_to_duration(time, require_nonnegative=False)
convert_range(program, item)
```

Classical constructors: `bit_`, `int_`, `uint_`, `float_`, `angle_`,
`complex_`, `arrayreference_`, and the variables `BitVar`, `IntVar`,
`UintVar`, `FloatVar`, `AngleVar`, `BoolVar`, `ComplexVar`, `DurationVar`,
`ArrayVar`, `PortVar`, `FrameVar`, `StretchVar`, `WaveformVar`. Constants
bound on the module include `pi`, `int64`, `float64`, `complex128`, `bit`,
`duration`, `frame`, `port`, `waveform`. Submodules: `base`,
`classical_types`, `control_flow`, `program`, `pulse`, `quantum_types`,
`subroutines`, `timing`.

### python-amazon-braket-schemas 1.32.1.post0-1

Import path is the shared `braket` package. This wheel contributes
`braket.schema_common`, device-schema modules, and the IR types the
simulator accepts. It depends on installed `python-pydantic` 2.14.1. The
SDK and the simulator wheels install further submodules into the same
`braket` namespace. See the SDK section for the combined import.

### python-amazon-braket-default-simulator 1.42.1-1

Import `braket.default_simulator`. Local state-vector and density-matrix
simulation. Depends on `python-opt_einsum` and on `python-antlr4>=4.13.2,<4.13.3`,
both satisfied.

```text
StateVectorSimulator()
StateVectorSimulation(qubit_count, shots, batch_size)
DensityMatrixSimulator()
DensityMatrixSimulation(qubit_count, shots)
GateOperation(targets, *params, ctrl_modifiers=(), power=1)
DefaultSimulator()
```

Submodules: `state_vector_simulator`, `density_matrix_simulator`,
`gate_operations`, `noise_operations`, `observables`, `openqasm`,
`result_types`, `simulation`, `simulation_strategies`, `linalg_utils`.

`StateVectorSimulator.run` is implemented on the simulator base and accepts
the circuit IR plus `shots`. The call that ran on this host is in
[the pin tests](#pins-that-stay-unmet). The Braket service API stays denied
for this project. The local simulator is the part that can run here.

### python-amazon-braket-sdk 1.127.7-1

Import `braket`. The SDK wheel, the schemas wheel, and the simulator wheel
share that package. Combined submodules measured from `braket` after all
three were installed include `circuits`, `devices`, `default_simulator`,
`ahs`, `annealing`, `aws`, `emulation`, `jobs`, `program_sets`, `pulse`,
`quantum_information`, `registers`, `tasks`, `timings`, and `tracking`.

Circuit construction:

```text
Circuit(addable=None, *args, **kwargs)
Instruction(operator, target=None, *, control=None, control_state=None, power=1)
Gate(qubit_count, ascii_symbols)
AngledGate(angle, qubit_count, ascii_symbols)
FreeParameter(name)
FreeParameterExpression(expression)
QubitSet(qubits=None)
Moments(instructions=None)
```

`Circuit` grows gates by methods (`h`, `cnot`, and the rest of the standard
set) that return the same circuit. The test below used `Circuit().h(0)`.

Devices:

```text
LocalSimulator(backend="default", noise_model=None)
Device(name, status)
```

`LocalSimulator` runs on this host. `braket.aws` is the service client and
was not used. The SDK pins `cloudpickle==2.2.1`. Installed
`python-cloudpickle` is 3.1.2-3 and stayed. It also depends on this tree's
`python-boltons` 26.2.0 and on `oqpy>=0.3.7,<0.4.0`.

### python-jsii 1.142.0-1

Import `jsii`. The Python kernel for jsii, which is how the CDK loads its
generated bindings. It declares `typeguard==2.13.3`. Installed typeguard is
4.6.0, and both `jsii` and `jsii._type_checking` import under that version.
That is an unsupported upstream configuration. A later call that exercises
the type-checking hooks can still disagree with typeguard 4.

Decorators and casts:

```text
enum(*, jsii_type)
data_type(*, jsii_type, jsii_struct_bases, name_mapping)
interface(*, jsii_type)
implements(*interfaces)
member(*, jsii_name)
proxy_for(abstract_class)
unsafe_cast(value, interface)
```

Kernel operations, used by generated bindings:

```text
load(name, version, tarball)
create(klass, obj, args=None)
delete(ref)
get(obj, property)
set(obj, property, value)
sget(klass, property)
sset(klass, property, value)
invoke(obj, method, args=None)
ainvoke(obj, method, args=None)
sinvoke(klass, method, args=None)
sainvoke(klass, method, args=None)
stats()
```

Classes: `JSIIAssembly(name, version, module, filename)`, `JSIIMeta`,
`JSIIAbstractClass`. Submodule: `python`.

### python-constructs 10.8.1-1

Import `constructs`. The construct tree CDK stacks are built from.

```text
Construct(scope, id)
RootConstruct(id=None)
Node(host, scope, id)
DependencyGroup(*deps)
Dependable()
MetadataEntry(*, data, type, trace=None)
MetadataOptions(*, stack_trace=None, stack_trace_override=None,
                trace_from_function=None)
ConstructOrder()
IConstruct()
IDependable()
IMixin()
IValidation()
```

`Construct` is the node a stack subclass inherits. `Node` holds the scope,
id, and dependency edges.

### CDK asset packages

`python-aws-cdk-asset-awscli-v1` 2.2.292-1 and
`python-aws-cdk-asset-node-proxy-agent-v6` 2.1.3-1 are jsii assemblies whose
payload is a Lambda layer zip, not a host install. The CLI asset is exactly
the version `aws-cdk-lib` 2.275.0 requires (`>=2.2.292,<2.2.293`). Its layer
contains AWS CLI v1 built for CPython 3.11. The node-proxy asset is the same
shape of zip. Neither wheel has an `aws` entry point. `/usr/bin/aws` stayed
with `aws-cli-v2`. Homepages are `cdklabs/awscdk-asset-awscli` and
`cdklabs/awscdk-asset-node-proxy-agent`.

### python-aws-cdk-cloud-assembly-schema 55.2.0-2

Distribution `aws-cdk.cloud-assembly-schema` 55.2.0. `aws-cdk-lib` wants
`>=55,<56`. The schema wheel and the library wheel both contain
`aws_cdk/cloud_assembly_schema/__init__.py`, and the two files differ. pip
installs the schema first and the library overwrites that one file. The
recipe drops that `__init__.py`, its `__pycache__`, and the matching RECORD
row, and it keeps `py.typed` and `_jsii/`. After install,
`aws_cdk/cloud_assembly_schema/__init__.py` is owned by
`python-aws-cdk-lib` 2.275.0-1. Depends: `python-jsii>=1.141,<2` and
`python-publication`.

### python-aws-cdk-lib 2.275.0-1

Import `aws_cdk`. Distribution `aws-cdk-lib` 2.275.0. Docstring: AWS Cloud
Development Kit library. `__all__` has 642 names. `inspect` classified 290
of them as classes and 352 as modules. `App` and `Stack` are both exported.
`Stack.__init__` is the jsii proxy signature `(*args, **kwargs)`. `App`'s
keyword arguments are `analytics_reporting`, `auto_synth`,
`builtin_cloud_formation_validation`,
`confirm_validation_plugins_do_not_mutate`, `context`,
`default_stack_synthesizer`, `outdir`, `performance_reporting`,
`policy_validation_beta1`, `post_cli_context`, `property_injectors`,
`stack_traces`, and `tree_metadata`.

Service constructs live in submodules named `aws_<service>` (`aws_s3`,
`aws_lambda`, `aws_ec2`, `aws_rds`, `aws_bedrock`, and the rest of that
list). A stack is a `Construct` subclass whose resources are attributes of
those submodules. `cdk synth` is a Node CLI and is not part of this wheel.
Importing `aws_cdk` loads the jsii kernel. It does not synthesize or deploy.
Homepage of the library and the schema is `aws/aws-cdk`.

### python-amazon-ion 0.15.0-1

Import `amazon.ion`. The package `__init__` lists its submodules in
`__all__` and does not import them. The simplejson-shaped API is
`amazon.ion.simpleion`. The extension was compiled on this host from the
sdist with `py-build-cmake` and cmake 4.4.4. No cp314 wheel is published.
`arch` is `x86_64`.

```text
dumps(obj, imports=None, binary=True, sequence_as_stream=False, indent=None,
      tuple_as_sexp=False, omit_version_marker=False, trailing_commas=False)
loads(ion_str, catalog=None, single_value=True, parse_eagerly=True,
      text_buffer_size_limit=None, value_model=IonPyValueModel.ION_PY)
dump(obj, fp, imports=None, binary=True, sequence_as_stream=False, indent=None,
     tuple_as_sexp=False, omit_version_marker=False, trailing_commas=False)
load(fp, catalog=None, single_value=True, parse_eagerly=True,
     text_buffer_size_limit=None, value_model=IonPyValueModel.ION_PY)
is_null(value)
```

`simple_types` holds `IonPyBool`, `IonPyBytes`, `IonPyDecimal`, `IonPyDict`,
`IonPyFloat`, `IonPyInt`, `IonPyList`, `IonPyNull`, `IonPySymbol`,
`IonPyText`, `IonPyTimestamp`, `IonType`, `Timestamp`, `TimestampPrecision`,
`SymbolToken`, and `is_null`. Lower-level readers and writers:
`reader`, `reader_binary`, `reader_text`, `reader_managed`, `writer`,
`writer_binary`, `writer_text`, `writer_buffer`. `c_ext` on `simpleion` is
true on this build, so `loads` and `dumps` go through the compiled ion-c
extension.

### python-localstack 2026.8.2-1

The wheel's console script is `localstack=localstack_cli.cli.main:main`,
which owns `/usr/bin/localstack`. `import localstack` raises
`ModuleNotFoundError`. `import localstack_cli` succeeds and the package
`__init__` exports nothing. The CLI implementation is
`localstack_cli.cli.main`. `windows-curses` is a Windows marker and is
absent from the recipe. Starting LocalStack needs Docker and was not done.
The deprecation warning is recorded under [command-line programs](#command-line-programs).

### python-redshift-connector 2.2.0-1

Import `redshift_connector`. DB-API driver. The AUR package is 2.1.8 and
was not used. The sdist is absent upstream, so the recipe installs the
wheel. It depends on `scramp` 1.4.9. boto3 1.43.108 satisfies `>=1.42.22`.

`connect(...)` returns `Connection`. The keyword set covers the direct
login (`user`, `database`, `password`, `host`, `port` defaulting toward
5439, `ssl`, `sslmode`), IAM (`iam`, `profile`, `region`,
`cluster_identifier`, `access_key_id`, `secret_access_key`, `session_token`,
`role_arn`), serverless (`is_serverless`, `serverless_acct_id`,
`serverless_work_group`), and the IdC, SAML, and browser-IdP fields
(`idp_host`, `client_id`, `client_secret`, `web_identity_token`,
`issuer_url`, `idc_region`, `group_federation`). The live signature lists
each of those as an optional keyword. `connect` was not called.

Also on the module: `Connection`, `Cursor`, `set_plugin_allowlist`, the
DB-API constructors `Binary`, `Date`, `Time`, `Timestamp`, `DateFromTicks`,
`TimeFromTicks`, `TimestampFromTicks`, the DB-API exceptions (`Warning`,
`Error`, `InterfaceError`, `DatabaseError`, `DataError`, `OperationalError`,
`IntegrityError`, `InternalError`, `ProgrammingError`, `NotSupportedError`),
the array exceptions, and the adapters `PGEnum`, `PGJson`, `PGJsonb`,
`PGText`, `PGVarchar`, `PGTsvector`. The remaining public names are Redshift
OID constants (`INTEGER`, `BIGINT`, `BOOLEAN`, `DATE`, `JSON`, `JSONB`,
`GEOMETRY`, and the rest).

### python-aws-glue-schema-registry 1.1.3-1

Import `aws_schema_registry`. Glue Schema Registry client and Kafka serde.
Homepage is `DisasterAWARE/aws-glue-schema-registry-python`.
`fastjsonschema` 2.21.2 satisfies `>=2.15,<3`. `orjson` 3.13.0 satisfies
`>=3.7.7`. `fastavro` is the Avro implementation above.

```text
SchemaRegistryClient(glue_client, registry_name="default-registry",
                     max_wait_attempts=10, wait_interval_seconds=3)
KafkaSerializer(client, is_key=False, compatibility_mode="BACKWARD",
                schema_naming_strategy=topic_name_strategy)
KafkaDeserializer(client, return_record_name=False, secondary_deserializer=None)
SchemaVersion(schema_name, version_id, definition, data_format, status,
              version_number=None)
DataAndSchema()
Schema()
SchemaRegistryException()
ValidationError()
```

`SchemaRegistryClient` needs a Glue client and was not constructed.
Submodules: `avro`, `client`, `codec`, `exception`, `jsonschema`, `naming`,
`schema`, `serde`. `CompatibilityMode` and `DataFormat` are literal types.

### python-bedrock-agentcore 1.25.1-1

Import `bedrock_agentcore`. Docstring: Bedrock AgentCore Runtime SDK, a
Python SDK for building and deploying AI agents. It declares
`boto3>=1.43.115` and `botocore>=1.43.115`. Installed boto3 and botocore are
1.43.108. The import does not raise. A later client constructor can still
reject that pair. pydantic 2.14.1 satisfies `<2.41.3`. uvicorn 0.54.0
satisfies `>=0.34.2`. No Bedrock call was made.

```text
BedrockAgentCoreApp(debug=False, lifespan=None, middleware=None)
RequestContext(**data)
BedrockAgentCoreContext(*args, **kwargs)
PingStatus(*args, **kwargs)
```

`BedrockAgentCoreApp` is a Starlette application a Lambda or a container
serves. Constructing it does not contact AWS. It was imported, and the class
was not instantiated, so the uvicorn server was not started.

### python-smdebug-rulesconfig 1.0.1-3

Import `smdebug_rulesconfig`. Debugger and profiler rule definitions that
`sagemaker-core` imports. The upstream wheel ships a top-level `tests`
package. `python-qiskit-serverless` owns
`/usr/lib/python3.14/site-packages/tests/__init__.py` (and `python-nassl`
owns files in that directory). The recipe deletes that tree, the RECORD
rows that begin with `tests/`, and the `tests` line of `top_level.txt`.
Installed `top_level.txt` is the single line `smdebug_rulesconfig`.
`import tests` is the qiskit-serverless package and is not part of this
distribution. Upstream `SyntaxWarning`s for `\-`, `\w`, and `\+` in
`smdebug_rulesconfig/actions/utils.py` remain.

Rule functions, each called with no arguments except where shown:

`all_zero`, `check_input_images`, `class_imbalance`, `confusion`,
`create_xgboost_report`, `dead_relu`, `exploding_tensor`,
`feature_importance_overweight`, `loss_not_decreasing`, `nlp_sequence_ratio`,
`overfit`, `overtraining`, `poor_weight_initialization`,
`saturated_activation`, `similar_across_runs`, `stalled_training_rule`,
`tensor_variance`, `tree_depth`, `unchanged_tensor`, `vanishing_gradient`,
`weight_update_ratio`, and `get_collection(collection_name)`.

```text
is_valid_action_object(actions: Action | ActionList)
ActionList(*actions)
StopTraining(training_job_prefix=None)
Email(email_address)
SMS(phone_number)
ProfilerReport(**rule_parameters)
BatchSize(cpu_threshold_p95=70, gpu_threshold_p95=70,
          gpu_memory_threshold_p95=70, patience=1000, window=500,
          scan_interval_us=60000000)
CPUBottleneck(threshold=50, gpu_threshold=10, cpu_threshold=90,
              patience=1000, scan_interval_us=60000000)
GPUMemoryIncrease(increase=5, patience=1000, window=10, scan_interval_us=60000000)
IOBottleneck(threshold=50, gpu_threshold=10, io_threshold=50,
             patience=1000, scan_interval_us=60000000)
LoadBalancing(threshold=0.5, patience=1000, scan_interval_us=60000000)
LowGPUUtilization(threshold_p95=70, threshold_p5=10, window=500,
                  patience=1000, scan_interval_us=60000000)
MaxInitializationTime(threshold=20, scan_interval_us=60000000)
OverallSystemUsage(scan_interval_us=60000000)
StepOutlier(stddev=3, mode=None, n_outliers=10, scan_interval_us=60000000)
```

Submodules: `actions`, `debugger_rules`, `profiler_rules`. These objects
describe rules. They do not start a training job.

### python-sagemaker-core 2.27.0-1

Import `sagemaker`, which is a namespace package whose docstring says
"Namespace package for SageMaker." The only submodule it exposes is `core`.
`sagemaker.core`'s docstring: SageMaker Core package for low-level resource
management and SDK foundations. File:
`/usr/lib/python3.14/site-packages/sagemaker/core/__init__.py`.

The distribution's upstream pins disagree with this host, and the import
still succeeds. See [the pin tests](#pins-that-stay-unmet). No session was
opened and no training or processing job was started.

```text
enable_textual_rich_console_and_traceback(force=False)
register_removed_module_finder()
set_attribution(attribution)
Processor(role=None, image_uri=None, instance_count=None, instance_type=None,
          entrypoint=None, volume_size_in_gb=30, ...)
ScriptProcessor(role=None, image_uri=None, command=None, instance_count=None,
                instance_type=None, volume_size_in_gb=30, ...)
FrameworkProcessor(image_uri, role=None, instance_count=None, instance_type=None,
                   command=None, volume_size_in_gb=30, ...)
Transformer(model_name, instance_count, instance_type, strategy=None, ...)
PartnerAppAuthProvider(credentials=None)
Attribution()
```

`Processor`, `ScriptProcessor`, and `FrameworkProcessor` describe a
processing job. `Transformer` describes a batch transform. Each takes a
`sagemaker_session` and would submit work once a method that creates a job
is called. Submodules: `apiutils`, `common_utils`, `config`, `constants`,
`deprecations`, `deserializers`, `enums`, `exceptions`, `helper`, `inputs`,
`job`, `local`, `logs`, `network`, `partner_app`, `processing`, `resources`,
`s3`, `serializers`, `session_settings`, `shapes`, `telemetry`,
`transformer`, `user_agent`, `utils`, `workflow`.

The meta-package `sagemaker` 3.27.0, and `sagemaker-train`,
`sagemaker-serve`, `sagemaker-mlops`, MLflow, and their closure, are not
installed. `sagemaker-core` is the library those distributions import.

## Pins that stay unmet

Four recipes declare versions this host will not install or downgrade to.
Pacman installed the wheels anyway. A successful import does not prove a
later call will accept the substitute.

| Package | Declared pin | Installed | What ran |
|---|---|---|---|
| jsii 1.142.0 | `typeguard==2.13.3` | typeguard 4.6.0 | `import jsii` and `import jsii._type_checking` both succeeded |
| amazon-braket-sdk 1.127.7 | `cloudpickle==2.2.1` | cloudpickle 3.1.2 | a one-qubit `Circuit().h(0)` round-tripped through `cloudpickle.dumps` / `loads` (1 qubit, 1 instruction) |
| bedrock-agentcore 1.25.1 | `boto3` and `botocore` `>=1.43.115` | 1.43.108 | `import bedrock_agentcore` succeeded and exposed the four public names |
| sagemaker-core 2.27.0 | `rich<15`, `protobuf<7`, `importlib-metadata<7`, `mock>4,<5` | rich 15.0.0, protobuf 7.36.1, importlib-metadata 9.0.1, mock 5.2.0 | `import sagemaker.core` succeeded |

sagemaker-core's `boto3>=1.43.90` and `cryptography>=46` are met by 1.43.108
and cryptography 50.0.2. pydantic 2.14.1 meets agentcore's `<2.41.3`.

The Braket simulator check, with no service call:

```python
from braket.circuits import Circuit
from braket.default_simulator.state_vector_simulator import StateVectorSimulator

circuit = Circuit().h(0)
simulator = StateVectorSimulator()
result = simulator.run(circuit.to_ir(), shots=1)
```

`result` is a `GateModelTaskResult` and `len(result.measurements)` is 1.
`simulator.run(circuit.to_ir(), shots=0)` raises `ValueError`: result types
must be specified in the IR when `shots=0`. `run(ir, qubit_count=1, shots=0)`
raises `TypeError` because `qubit_count` is not a parameter of `run`.

## Left uninstalled

| Item | Why it is absent |
|---|---|
| `extra/aws-cli` 1.x | `/usr/bin/aws` stays on `aws-cli-v2` 2.37.9-1 |
| AUR git snapshots of boto3, botocore, s3transfer, awscrt, moto | the installed extra releases stay |
| AUR `python-boltons` 25.0.0-2 (BlackArch) | `paru` selects it; the local recipe installed 26.2.0 |
| AUR `python-scramp` 1.5.0 | redshift-connector requires `scramp<1.5` |
| AUR `python-pyathena` 3.17.1 | the recipe installed 4.2.1 |
| AUR `python-redshift-connector` 2.1.8 | the recipe installed 2.2.0 |
| a current `boto3-stubs` PKGBUILD | it would conflict with the installed AUR stubs |
| `aws-sam-cli` 1.170.0 | the AUR package 1.138.0 stays |
| OpenTelemetry pkgrel 5 | pkgrel 4 is installed from the local cache; see [the mirror table](#opentelemetry-pkgrel-4-and-pkgrel-5) |
| `sagemaker` 3.27.0 and `sagemaker-train`, `sagemaker-serve`, `sagemaker-mlops` | train pulls MLflow; mlops pulls `pyiceberg` |
| `mlflow`, `mlflow-skinny`, `mlflow-tracing`, `huey`, `skops`, `pyiceberg`, `sagemaker-mlflow` | none of that closure is packaged here |
| `lstk` | the LocalStack package ships the legacy `localstack` script only |
| `windows-curses` | Windows marker on the LocalStack wheel |

`python-tenacity` 9.2.1-1, `python-schema` 0.7.8-2, `python-dnslib` 0.9.26-3,
`python-pyotp` 2.10.0-1, and `python-typeguard` 4.6.0-1 were pulled from
`extra` by `makepkg -s` and are installed.

## What this host can run locally

Imports, cfn-lint, cookiecutter generation, chevron rendering, Ion
`loads`/`dumps`, OpenQASM and OpenPulse parsing, a Braket
`StateVectorSimulator` shot, opt_einsum contraction, and jsii/CDK class
construction that does not synthesize against an account are local. `sam
build` without a container, and `lambda-builders` with
`download_dependencies=False`, can also stay local.

`boto3.client`, `aiobotocore` clients, `s3fs.S3FileSystem`, awswrangler
service functions, `pyathena.connect`, `redshift_connector.connect`,
`awslocal`, `SecretCache`, `provide_token`, `SchemaRegistryClient`,
`EncryptionSDKClient` with a KMS provider, `LocalSimulator` pointed at
`braket.aws`, `sagemaker.core` job methods, and `localstack` start are
service or daemon calls. On this project they follow the free-plan rules in
[free-plan-usage.md](free-plan-usage.md). Braket's service API, including
device search, is denied. The local simulator is the Braket path that ran.
