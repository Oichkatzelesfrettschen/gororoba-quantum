"""Record the repository paths a gate process reads, through sys.addaudithook.

ci/run_gates.py prepends this directory to PYTHONPATH and sets
GOROROBA_READ_TRACE=<dir> when it keeps a gate ledger; site imports this
module at startup, so every Python process of the gate, spawn-pool children
included, appends tab-separated records to <dir>/<pid>.tsv through one
O_APPEND descriptor, one os.write per record. A pool worker ended by SIGTERM
never runs atexit, and each record is on disk when its write returns.

Records name paths relative to GOROROBA_READ_TRACE_ROOT:

- ``f PATH``: a file opened for reading (a ``.pyc`` maps to its source
  through importlib.util.source_from_cache; an open that fails still names
  the path, so a file created later changes the gate key);
- ``d PATH``: a directory listed through os.listdir or os.scandir;
- ``g RECURSIVE PATTERN``: a glob.glob pattern;
- ``s PATH`` and ``l PATH``: a path os.stat or os.lstat probed (os.path.exists,
  isfile, isdir, Path.exists and Path.stat resolve through them), keyed by
  existence and file type, so a file that appears later changes the key;
- ``k PATH``: a symbolic link a recorded path crosses, keyed by its link text,
  recorded even when the link points outside the root;
- ``U REASON``: the process did something the read set cannot capture: it
  opened a repository file for writing, or started a program that is not a
  traced interpreter of GOROROBA_READ_TRACE_PYTHONS (any non-Python program,
  a Python child under -I, -E or -S, or an environment that drops the trace
  variables).

Writes under a ``__pycache__`` directory are bytecode caches and record
nothing. Paths outside the root (the standard library, site-packages) belong
to the interpreter identity in the ledger key. The clock, stat calls through a
dir_fd or a direct posix binding (importlib's) and C-extension file access
leave no record; the nightly ledger audit reruns every gate against them.
"""

from __future__ import annotations

import os
import sys

# typing stays unimported at run time: this module loads in every gate process.
TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any

_TRACE = os.environ.get("GOROROBA_READ_TRACE")


def _chain() -> None:
    """Load the sitecustomize this module shadows, when one exists further along sys.path."""
    import importlib.machinery
    import importlib.util

    here = os.path.dirname(os.path.abspath(__file__))
    rest = [entry for entry in sys.path if os.path.abspath(entry or os.curdir) != here]
    spec = importlib.machinery.PathFinder.find_spec("sitecustomize", rest)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def _install(trace: str) -> None:
    import importlib.util

    root = os.path.realpath(os.environ.get("GOROROBA_READ_TRACE_ROOT") or os.getcwd())
    prefix = root + os.sep
    here = os.path.dirname(os.path.abspath(__file__))
    pythons = frozenset(
        os.path.realpath(path) for path in os.environ.get("GOROROBA_READ_TRACE_PYTHONS", "").split(os.pathsep) if path
    ) | {os.path.realpath(sys.executable)}
    write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
    descriptor = os.open(os.path.join(trace, f"{os.getpid()}.tsv"), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    import _thread

    seen: set[object] = set()
    # Threads that are inside the handler; an event a handler raises on its own
    # thread returns at once, while every other thread's events still record.
    active: set[int] = set()
    lock = _thread.allocate_lock()
    get_ident = _thread.get_ident
    events = frozenset(
        (
            "open",
            "os.listdir",
            "os.scandir",
            "glob.glob",
            "glob.glob/2",
            "subprocess.Popen",
            "os.posix_spawn",
            "os.exec",
            "os.spawn",
            "os.system",
            "pty.spawn",
        )
    )
    deduplicated = frozenset(("open", "os.listdir", "os.scandir"))
    realpath = os.path.realpath
    join = os.path.join
    getcwd = os.getcwd
    fspath = os.fsdecode
    source_from_cache = importlib.util.source_from_cache

    def emit(record: str) -> None:
        # One write per record on an O_APPEND descriptor, under the lock so
        # records from concurrent threads never interleave.
        with lock:
            os.write(descriptor, (record + "\n").encode("utf-8", "surrogateescape"))

    def links(absolute: str) -> None:
        """Record every symbolic link on a lexical repository path with its link text."""
        current = root
        for part in absolute[len(prefix) :].split(os.sep):
            current = join(current, part)
            if os.path.islink(current):
                name = current[len(prefix) :]
                key = ("k", name)
                with lock:
                    fresh = key not in seen
                    seen.add(key)
                if fresh:
                    emit(f"k\t{name}")
                current = realpath(current)
                if not current.startswith(prefix):
                    return

    def relative(path: Any, base: Any = None, follow: bool = True) -> str | None:
        """The root-relative resolved path, after recording each link the lexical path crosses."""
        if isinstance(path, int):
            return None
        text = fspath(path)
        if base is not None and not os.path.isabs(text):
            text = join(fspath(base), text)
        lexical = os.path.normpath(join(getcwd(), text))
        if lexical.startswith(prefix):
            links(lexical)
        if follow:
            absolute = realpath(lexical)
        else:
            absolute = join(realpath(os.path.dirname(lexical)), os.path.basename(lexical))
        if absolute == root:
            return "."
        if absolute.startswith(prefix):
            return absolute[len(prefix) :]
        return None

    def probe(original: Any, follow: bool) -> Any:
        """os.stat or os.lstat that records a repository path's existence and file type as a read."""
        tag = "s" if follow else "l"

        def wrapped(path: Any, *args: Any, **kwargs: Any) -> Any:
            result = original(path, *args, **kwargs)
            ident = get_ident()
            if ident in active or isinstance(path, int) or kwargs.get("dir_fd") is not None:
                return result
            record(path, ident, kwargs.get("follow_symlinks", True) and follow)
            return result

        def record(path: Any, ident: int, followed: bool) -> None:
            key = (tag, path if isinstance(path, (str, bytes)) else repr(path), followed, getcwd())
            with lock:
                if key in seen:
                    return
                seen.add(key)
            active.add(ident)
            try:
                name = relative(path, follow=followed)
                if name is not None:
                    emit(f"{'s' if followed else 'l'}\t{name}")
            except Exception as error:  # noqa: BLE001 -- a tracer fault marks the run, never the gate
                emit(f"U\ttracer {type(error).__name__} on stat")
            finally:
                active.discard(ident)

        def failing(path: Any, *args: Any, **kwargs: Any) -> Any:
            try:
                return wrapped(path, *args, **kwargs)
            except OSError:
                ident = get_ident()
                if ident not in active and not isinstance(path, int) and kwargs.get("dir_fd") is None:
                    record(path, ident, kwargs.get("follow_symlinks", True) and follow)
                raise

        failing.__name__ = original.__name__
        failing.__doc__ = original.__doc__
        return failing

    os.stat = probe(os.stat, True)
    os.lstat = probe(os.lstat, False)

    def python_child(argv: list[str], environment: Any) -> str | None:
        """The reason a child escapes the trace, or None for a traced Python child."""
        if not argv:
            return "empty argv"
        if realpath(argv[0]) not in pythons and realpath(_which(argv[0]) or argv[0]) not in pythons:
            return f"program {os.path.basename(argv[0])}"
        if environment is not None:
            mapping = dict(environment)
            decoded = {fspath(key): fspath(value) for key, value in mapping.items()}
            if decoded.get("GOROROBA_READ_TRACE") != trace or here not in decoded.get("PYTHONPATH", "").split(
                os.pathsep
            ):
                return "child environment drops the trace"
        tokens = iter(argv[1:])
        for token in tokens:
            if not token.startswith("-") or token == "-" or token.startswith("--"):
                break
            for index, letter in enumerate(token[1:]):
                if letter in "IES":
                    return f"python -{letter} child"
                if letter in "cm":
                    return None
                if letter in "WX":
                    if index == len(token) - 2:
                        next(tokens, None)
                    break
        return None

    def handle(event: str, args: tuple[Any, ...]) -> None:
        if event == "open":
            path, mode, flags = args
            writes = (mode is not None and any(letter in str(mode) for letter in "wax+")) or (
                mode is None and isinstance(flags, int) and flags & write_flags
            )
            name = relative(path)
            if name is None:
                return
            if writes:
                if "__pycache__" not in name.split(os.sep):
                    emit(f"U\twrites {name}")
                return
            if name.endswith(".pyc"):
                try:
                    source = source_from_cache(join(root, name))
                except (ValueError, NotImplementedError):
                    source = None
                if source is not None and os.path.exists(source):
                    name = relative(source) or name
            emit(f"f\t{name}")
        elif event in ("os.listdir", "os.scandir"):
            name = relative(args[0] if args and args[0] is not None else ".")
            if name is not None:
                emit(f"d\t{name}")
        elif event in ("glob.glob", "glob.glob/2"):
            pattern, recursive = args[0], args[1]
            base = args[2] if event == "glob.glob/2" and args[2] is not None else None
            if isinstance(pattern, bytes):
                pattern = fspath(pattern)
            text = str(pattern)
            if base is not None and not os.path.isabs(text):
                text = join(fspath(base), text)
            absolute = os.path.normpath(join(getcwd(), text))
            if not absolute.startswith(prefix):
                magic = min((absolute.find(c) for c in "*?[" if c in absolute), default=len(absolute))
                fixed = os.path.dirname(absolute[:magic]) if magic < len(absolute) else absolute
                absolute = realpath(fixed) + absolute[len(fixed) :]
            if absolute.startswith(prefix):
                emit(f"g\t{int(bool(recursive))}\t{absolute[len(prefix) :]}")
        elif event == "subprocess.Popen":
            executable, argv, _cwd, environment = args
            words = [fspath(word) for word in argv] if isinstance(argv, (list, tuple)) else [fspath(argv)]
            if executable is not None:
                words = [fspath(executable), *words[1:]]
            reason = python_child(words, environment)
            if reason is not None:
                emit(f"U\t{reason}")
        elif event in ("os.posix_spawn", "os.exec"):
            path, argv, environment = args[0], args[1], args[2]
            words = [fspath(word) for word in argv]
            reason = python_child([fspath(path), *words[1:]], environment)
            if reason is not None:
                emit(f"U\t{reason}")
        elif event in ("os.spawn", "os.system", "pty.spawn"):
            emit(f"U\t{event}")

    def hook(event: str, args: tuple[Any, ...]) -> None:
        if event not in events:
            return
        ident = get_ident()
        if ident in active:
            return
        if event in deduplicated:
            first = args[0]
            if first is not None and not isinstance(first, (str, bytes, int)):
                try:
                    first = os.fspath(first)
                except TypeError:
                    first = repr(first)
            writes = event == "open" and (
                (args[1] is None and isinstance(args[2], int) and args[2] & write_flags)
                or (args[1] is not None and any(letter in str(args[1]) for letter in "wax+"))
            )
            relative_path = first is None or (isinstance(first, (str, bytes)) and not os.path.isabs(first))
            key = (event, first, bool(writes), getcwd() if relative_path else None)
            with lock:
                if key in seen:
                    return
                seen.add(key)
        active.add(ident)
        try:
            handle(event, args)
        except Exception as error:  # noqa: BLE001 -- a tracer fault marks the run, never the gate
            emit(f"U\ttracer {type(error).__name__} on {event}")
        finally:
            active.discard(ident)

    sys.addaudithook(hook)


def _which(name: str) -> str | None:
    if os.sep in name:
        return None
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(directory, name)
        if os.access(candidate, os.X_OK):
            return candidate
    return None


if _TRACE:
    _install(_TRACE)
_chain()
