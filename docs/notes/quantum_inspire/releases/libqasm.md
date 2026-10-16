> Full piece: [https://github.com/QuTech-Delft/libqasm/releases](https://github.com/QuTech-Delft/libqasm/releases)
> Retrieved 2026-10-16T22:00Z by scripts/capture_qi_docs.py --releases (urllib, REST API);
> 27 releases, newest first, bodies verbatim; data in [libqasm.json](libqasm.json).

# libqasm releases

## Release 1.6.0

Tag `1.6.0`, 2026-10-14T13:34:10Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/1.6.0>

### Added
- Support for Python 3.14.

## Release 1.5.0

Tag `1.5.0`, 2026-10-02T09:12:13Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/1.5.0>

### Added
- `CCX`, `CCNOT`, and `CSWAP` unitary instructions.

## Release 1.4.1

Tag `1.4.1`, 2026-06-15T11:19:21Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/1.4.1>

### Fixed
- Aliases `measureX`, `measureY`, and `measureZ`, for the `measure` instruction, recognized as tokens by the lexer.

## Release 1.4.0

Tag `1.4.0`, 2026-06-05T14:26:14Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/1.4.0>

### Added
- `CV`, `CY`, `DCNOT`, `ECR`, `ISWAP`, `InvSqrtSWAP`, `M`, `MS`, `SqrtISWAP`, and `SqrtSWAP` unitary instructions.
- Aliases `measureX`, `measureY`, and `measureZ`, for the `measure` instruction along the respective axes.

## Release 1.3.0

Tag `1.3.0`, 2026-04-14T13:28:29Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/1.3.0>

### Added
- `U`, `Z90`, and `mZ90` unitary instructions.
- The `measure` instruction also accepts (3 float) parameters to specify measurement axis.

## Release 1.2.1

Tag `1.2.1`, 2025-07-28T13:45:05Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/1.2.1>

### Added
- Support for Python 3.13.

### Fixed
- Semantic analyzer throws exception if the number of provided instruction parameters are incorrect.

## Release 1.2.0

Tag `1.2.0`, 2025-03-27T16:08:00Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/1.2.0>

### Added
- Semantic analyzer check for same number of indices in each qubit operand.

## Release 1.1.0

Tag `1.1.0`, 2025-03-13T16:58:19Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/1.1.0>

### Added
- Assembly declaration.
- `Rn` unitary instruction.
- Publish WASM binaries to npm.

### Changed
- Update to `mkdocs-material/9.6.5` and `mkdocstrings/0.28.2` versions in `requirements.txt`.
- Do not hardcode `CMAKE_CXX_STANDARD`.
- Rename `ast` to `syntactic`.

### Fixed
- Setting of `build_type` in Conan profiles.
- `cibw-wheels` GitHub Actions job was building wheels only for Linux/ARM64.

## Removed
- Upload WASM binaries as release assets.

## Release 1.0.0

Tag `1.0.0`, 2025-01-31T14:42:25Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/1.0.0>

### Added
- `.clang-tidy`.
- Python Linux/ARM64 GitHub Actions job.

### Changed
- Error when redeclaring a variable.
- Change Linux/ARM64 jobs to use GitHub-hosted runners.

### Fixed
- clang/Linux/x64 GitHub Actions jobs (which use Ubuntu 24.04.1 since 2025).

## Release 0.6.9

Tag `0.6.9`, 2024-11-14T14:13:55Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.6.9>

### Added
- `SWAP` unitary instruction.
- `init`, `barrier`, and `wait` non-unitary instructions.

### Changed

### Removed
- `reset` without qubit operands form.

## Release 0.6.8

Tag `0.6.8`, 2024-10-18T10:28:54Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.6.8>

### Added
- Gate modifiers: `inv`, `pow`, and `ctrl`.
- C++ linters GitHub Actions job (just running clang-format at the moment).

### Changed
- Fix bug: empty lists are written out to JSON as `"[]"` instead of `[]`.
- Fix bug: CRk and CZ parameter types were interchanged in the instruction set.
- More descriptive and consistent (snake case) file names. 
- Minor fixes and tweaks to documentation.

### Removed

## Release 0.6.7

Tag `0.6.7`, 2024-08-26T20:34:49Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.6.7>

### Added
- `pyproject.toml`.
- GitHub pages.

### Changed
- Fix building of tests in Conan profiles and `setup.py`.
- Fix Python MacOS/x64 (with Python > 3.11) packages.
- Fix deserialization of CBOR strings.

### Removed
- Python 3.8 packages generation.

## Release 0.6.6

Tag `0.6.6`, 2024-05-14T13:16:07Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.6.6>

### Added
- Allow multiple qubit/bit (register) definitions and mid-circuit measurements.
- Python MacOS/arm64 jobs.
- `python/test_libqasm.py` to test Python jobs.

### Changed
- Fix Python MacOS/arm64 packages.
- Fix `scripts/generate_antlr_parser.py`.
- MacOS/x64 jobs now run in macos-13, and MacOS/arm64 jobs in macos-14, both GitHub runners.
- Python module name from `libQasm` to `libqasm`.

### Removed
- `python/module/libQasm` folder.

## Release 0.6.5

Tag `0.6.5`, 2024-04-24T11:00:18Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.6.5>

### Added

### Changed

- Updated emscripten compilation flags.
- Changed GitHub Actions `js-emscripten-wasm` job to work with `deno` instead of `node`.

### Removed

## Release 0.6.4

Tag `0.6.4`, 2024-04-23T14:46:27Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.6.4>

### Added

### Changed

- Fixed CMake install.
- `generate_antlr_parser.py` writes output include files in a given `include` folder. 

### Removed

## Release 0.6.3

Tag `0.6.3`, 2024-04-15T20:31:30Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.6.3>

### Added

- `cpp-linux-x64-release-shared` test job.

### Changed

- Allow multiple `measure` instructions at the end of a program.

### Removed

## Release 0.6.2

Tag `0.6.2`, 2024-04-12T09:00:08Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.6.2>

### Added

- `.clang-format`.
- `emscripten-wasm` assets job.

### Changed

- Fix shared library build.

### Removed

- `TREEN_GEN_BUILD_TESTS` option.

## Release 0.6.1

Tag `0.6.1`, 2024-04-08T16:33:51Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.6.1>

### Added

### Changed

- Fix Python interface.
- Update GitHub Actions versions.

### Removed

- `m4` dependency.

## Release 0.6.0

Tag `0.6.0`, 2024-03-28T15:06:39Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.6.0>

### Added

- cQasm 3.0 parser. MVP (Minimum Viable Product) implemented.
- Conan as package manager.

### Changed

- Different upgrades: C++20, CMake 3.12, Python 3.8 to 3.12.

### Removed

- cQasm 1.x support.
- Git submodules.

## Release 0.4

Tag `0.4.0`, 2021-07-15T08:10:35Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.4.0>

- Add barrier instruction to default instruction set, all the way back to cQASM 1.0
 - Add `@@LINE` token to grammar to allow modification of line number information, similar to #line in the C preprocessor (this was needed for OpenQL)
 - Various bugfixes along the way

## Release 0.3

Tag `0.3.0`, 2021-06-16T10:48:05Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.3.0>

- Add cQASM 1.1 and 1.2 support.
 - Add new Python API that supports all 1.x versions (`import cqasm.v1`), while maintaining the legacy 1.0-only API (`import libQasm`).
 - Python 3.9 support.
 - Various bugfixes along the way.

## Release 0.2.0

Tag `0.2.0`, 2020-08-31T15:32:58Z: <https://github.com/QuTech-Delft/libqasm/releases/tag/0.2.0>

- New C++ API implemented that allows the instruction set to be modified, rather than it being hardcoded in the grammar.
 - Various improvements to the cQASM language:
    - expressions & API-configurable constant propagation;
    - additional semantic checks;
    - fewer keywords/reserved names;
    - no more restrictions on whitespace and existing comment style, addition of block comments;
    - new U matrix syntax;
    - annotation support.
 - Multiple cQASM syntax/semantic errors can be reported at once, and all error messages have line & column numbers attached.
 - Vast improvements to the CMake and Python build systems. The former allows libqasm to be used as a submodule in an external project with only two CMake directives (add_subdirectory and target_link_libraries).
 - Additional tests and continuous integration for all supported platforms to ensure that the releases actually work.
 - First release to PyPI and Anaconda cloud (though the Python API still follows the old one).

## Minor Fixes and Features

Tag `0.1.4`, 2019-07-23T10:28:40Z (pre-release): <https://github.com/QuTech-Delft/libqasm/releases/tag/0.1.4>

- licensed repo 
- new style jenkings
- changed python version
- fixed stateful behavior

## Bugfix release 0.1.3

Tag `0.1.3`, 2018-12-13T13:06:04Z (pre-release): <https://github.com/QuTech-Delft/libqasm/releases/tag/0.1.3>

Bugs fixed:

* Remove `-u 0` from Jenkinsfile again

## Bugfix release 0.1.2

Tag `0.1.2`, 2018-12-13T12:48:51Z (pre-release): <https://github.com/QuTech-Delft/libqasm/releases/tag/0.1.2>

Bugs fixed:
* Single qubit operations now accept integers as arguments. Previously it required floats similar to the previous problem solved in release 0.1.1.

## Bugfix release 0.1.1

Tag `0.1.1`, 2018-07-27T10:47:29Z (pre-release): <https://github.com/QuTech-Delft/libqasm/releases/tag/0.1.1>

Bugs fixed:

* Line with single space in between version and qubits is not parsed
* Float without part after the decimal seperator is not accepted (for eg. `1.`)

Improvements:

* Jenkinsfile for CI setup added
* Add line number and column number of syntax error to exception

## Initial release

Tag `0.1.0`, 2018-06-15T11:14:46Z (pre-release): <https://github.com/QuTech-Delft/libqasm/releases/tag/0.1.0>

Initial release.

Known issues:
* Grammar accepts invalid syntax
