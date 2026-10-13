"""Emit a deterministic direct-call map for the repository's Python modules.

The parser enforces the Python source version declared by ``pyproject.toml``.
Compiler symbol tables and explicit comprehension scopes resolve stable calls
from top-level function bodies, comprehension and generator expressions, and
evaluated nested-definition headers. Postponed annotations and function-local
variable annotations contribute no call edges. A stable bare decorator is an
implicit call, and a direct write through an imported repository-module alias
invalidates the written export throughout the map.

The bounded model covers flat modules and absolute repository imports. The
model excludes module-initializer calls; nested function, lambda, and class bodies;
class-method and dynamic dispatch; relative and star imports; function-local
import flow; decorated exports; values returned by decorator factories; calls
through values; and reflective mutation through ``setattr``, ``globals``,
``exec``, import hooks, or ``__code__`` replacement. Excluded targets require
data-flow or runtime evidence.
"""

from __future__ import annotations

import ast
import re
import symtable
import tomllib
from collections import defaultdict, deque
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "gororoba_quantum"
ROOT_FUNCTIONS = (
    "claim_boundaries.main",
    "sedenion_bundle.main",
    "annihilator_strata.main",
    "rank_polynomials.main",
    "rank_charts.main",
    "rank_attachments.main",
    "integral_homology.main",
    "rank_path_topology.main",
    "ripple_dynamics.main",
    "compile_evidence.main",
    "designs._verify",
    "modular_arithmetic._verify",
    "verify.main",
    "order_finding.order_finding_plan",
    "hybrid_shor.main",
)

Binding = tuple[str, str | None]


def _configured_source_version() -> tuple[int, int]:
    """Return the matching Ruff and mypy Python source version."""
    with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as configuration_file:
        configuration = tomllib.load(configuration_file)
    ruff_target = str(configuration["tool"]["ruff"]["target-version"])
    ruff_match = re.fullmatch(r"py(\d)(\d+)", ruff_target)
    if ruff_match is None:
        raise RuntimeError(f"unsupported Ruff target-version {ruff_target!r}")
    ruff_version = (int(ruff_match.group(1)), int(ruff_match.group(2)))
    mypy_target = str(configuration["tool"]["mypy"]["python_version"])
    try:
        mypy_version = tuple(int(component) for component in mypy_target.split("."))
    except ValueError as error:
        raise RuntimeError(f"unsupported mypy python_version {mypy_target!r}") from error
    if len(mypy_version) != 2 or mypy_version != ruff_version:
        raise RuntimeError(f"Ruff target-version {ruff_target!r} and mypy python_version {mypy_target!r} disagree")
    return ruff_version


SOURCE_FEATURE_VERSION = _configured_source_version()


def _assignment_names(target: ast.expr) -> frozenset[str]:
    """Return names bound by one assignment or comprehension target."""
    if isinstance(target, ast.Name):
        return frozenset({target.id})
    if isinstance(target, (ast.List, ast.Tuple)):
        return frozenset(name for element in target.elts for name in _assignment_names(element))
    if isinstance(target, ast.Starred):
        return _assignment_names(target.value)
    return frozenset()


def _visit_argument_expressions(
    visitor: ast.NodeVisitor,
    arguments: ast.arguments,
    *,
    annotations_are_evaluated: bool,
) -> None:
    """Visit defaults and any annotations evaluated outside a nested body."""
    if annotations_are_evaluated:
        for argument in (*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs):
            if argument.annotation is not None:
                visitor.visit(argument.annotation)
        if arguments.vararg is not None and arguments.vararg.annotation is not None:
            visitor.visit(arguments.vararg.annotation)
        if arguments.kwarg is not None and arguments.kwarg.annotation is not None:
            visitor.visit(arguments.kwarg.annotation)
    for default in (*arguments.defaults, *(default for default in arguments.kw_defaults if default is not None)):
        visitor.visit(default)


def _uses_postponed_annotations(syntax_tree: ast.Module) -> bool:
    """Return whether the module activates ``__future__.annotations``."""
    return any(
        isinstance(statement, ast.ImportFrom)
        and statement.module == "__future__"
        and any(imported_name.name == "annotations" for imported_name in statement.names)
        for statement in syntax_tree.body
    )


class ModuleBindingCollector(ast.NodeVisitor):
    """Collect module names that have one statically stable repository origin."""

    def __init__(self, module_name: str, *, annotations_are_evaluated: bool) -> None:
        self.module_name = module_name
        self.annotations_are_evaluated = annotations_are_evaluated
        self.bindings: defaultdict[str, list[Binding]] = defaultdict(list)
        self.control_depth = 0
        self.has_star_import = False

    def _record(self, name: str, binding_kind: str, target: str | None) -> None:
        if self.control_depth:
            self.bindings[name].append(("unknown", None))
        else:
            self.bindings[name].append((binding_kind, target))

    def _visit_function_header(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        _visit_argument_expressions(
            self,
            node.args,
            annotations_are_evaluated=self.annotations_are_evaluated,
        )
        if self.annotations_are_evaluated and node.returns is not None:
            self.visit(node.returns)
        for type_parameter in getattr(node, "type_params", ()):
            self.visit(type_parameter)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        binding_kind = "unknown" if node.decorator_list else "local_function"
        self._record(node.name, binding_kind, f"{self.module_name}.{node.name}")
        self._visit_function_header(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        binding_kind = "unknown" if node.decorator_list else "local_function"
        self._record(node.name, binding_kind, f"{self.module_name}.{node.name}")
        self._visit_function_header(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._record(node.name, "unknown", None)
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)
        for type_parameter in getattr(node, "type_params", ()):
            self.visit(type_parameter)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        _visit_argument_expressions(
            self,
            node.args,
            annotations_are_evaluated=self.annotations_are_evaluated,
        )

    def visit_Import(self, node: ast.Import) -> None:
        for imported_name in node.names:
            local_name = imported_name.asname or imported_name.name.split(".")[0]
            imported_module = imported_name.name if imported_name.asname else imported_name.name.split(".")[0]
            self._record(local_name, "module", imported_module)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for imported_name in node.names:
            if imported_name.name == "*":
                self.has_star_import = True
                continue
            local_name = imported_name.asname or imported_name.name
            target = None if node.level or node.module is None else f"{node.module}.{imported_name.name}"
            self._record(local_name, "imported_function", target)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self._record(node.id, "unknown", None)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name is not None:
            self._record(node.name, "unknown", None)
        self.generic_visit(node)

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name is not None:
            self._record(node.name, "unknown", None)
        if node.pattern is not None:
            self.visit(node.pattern)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        if node.name is not None:
            self._record(node.name, "unknown", None)

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        if node.rest is not None:
            self._record(node.rest, "unknown", None)
        self.generic_visit(node)

    def _visit_control_flow(self, node: ast.AST) -> None:
        self.control_depth += 1
        try:
            self.generic_visit(node)
        finally:
            self.control_depth -= 1

    def visit_If(self, node: ast.If) -> None:
        self._visit_control_flow(node)

    def visit_For(self, node: ast.For) -> None:
        self._visit_control_flow(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._visit_control_flow(node)

    def visit_While(self, node: ast.While) -> None:
        self._visit_control_flow(node)

    def visit_With(self, node: ast.With) -> None:
        self._visit_control_flow(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self._visit_control_flow(node)

    def visit_Try(self, node: ast.Try) -> None:
        self._visit_control_flow(node)

    def visit_TryStar(self, node: ast.TryStar) -> None:
        self._visit_control_flow(node)

    def visit_Match(self, node: ast.Match) -> None:
        self._visit_control_flow(node)

    def _visit_comprehension(self, generators: list[ast.comprehension], result_nodes: tuple[ast.expr, ...]) -> None:
        for generator in generators:
            self.visit(generator.iter)
            for condition in generator.ifs:
                self.visit(condition)
        for result_node in result_nodes:
            self.visit(result_node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self._visit_comprehension(node.generators, (node.key, node.value))


class FunctionBindingCollector(ast.NodeVisitor):
    """Collect bindings in one function while preserving nested-scope boundaries."""

    def __init__(self, arguments: ast.arguments, *, annotations_are_evaluated: bool) -> None:
        self.annotations_are_evaluated = annotations_are_evaluated
        self.bound_names = {
            argument.arg for argument in (*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs)
        }
        if arguments.vararg is not None:
            self.bound_names.add(arguments.vararg.arg)
        if arguments.kwarg is not None:
            self.bound_names.add(arguments.kwarg.arg)
        self.declared_globals: set[str] = set()

    @property
    def local_names(self) -> frozenset[str]:
        return frozenset(self.bound_names - self.declared_globals)

    def _visit_nested_function_header(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self.bound_names.add(node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        _visit_argument_expressions(
            self,
            node.args,
            annotations_are_evaluated=self.annotations_are_evaluated,
        )
        if self.annotations_are_evaluated and node.returns is not None:
            self.visit(node.returns)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_nested_function_header(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_nested_function_header(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.bound_names.add(node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        _visit_argument_expressions(
            self,
            node.args,
            annotations_are_evaluated=self.annotations_are_evaluated,
        )

    def visit_Import(self, node: ast.Import) -> None:
        for imported_name in node.names:
            self.bound_names.add(imported_name.asname or imported_name.name.split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for imported_name in node.names:
            if imported_name.name != "*":
                self.bound_names.add(imported_name.asname or imported_name.name)

    def visit_Global(self, node: ast.Global) -> None:
        self.declared_globals.update(node.names)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.bound_names.add(node.id)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name is not None:
            self.bound_names.add(node.name)
        self.generic_visit(node)

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name is not None:
            self.bound_names.add(node.name)
        if node.pattern is not None:
            self.visit(node.pattern)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        if node.name is not None:
            self.bound_names.add(node.name)

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        if node.rest is not None:
            self.bound_names.add(node.rest)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.visit(node.target)
        if node.value is not None:
            self.visit(node.value)

    def _visit_comprehension(self, generators: list[ast.comprehension], result_nodes: tuple[ast.expr, ...]) -> None:
        for generator in generators:
            self.visit(generator.iter)
            for condition in generator.ifs:
                self.visit(condition)
        for result_node in result_nodes:
            self.visit(result_node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self._visit_comprehension(node.generators, (node.key, node.value))


class DirectCallCollector(ast.NodeVisitor):
    """Collect conservative calls without assigning nested bodies to a parent."""

    def __init__(
        self,
        global_functions: dict[str, str],
        global_modules: dict[str, str],
        exported_functions: dict[str, dict[str, str]],
        function_symbol_table: symtable.SymbolTable,
        function_local_names: frozenset[str],
        *,
        annotations_are_evaluated: bool,
    ) -> None:
        self.global_functions = global_functions
        self.global_modules = global_modules
        self.exported_functions = exported_functions
        self.function_symbol_table = function_symbol_table
        self.function_local_names = function_local_names
        self.annotations_are_evaluated = annotations_are_evaluated
        self.comprehension_bindings: set[str] = set()
        self.calls: set[str] = set()

    def _resolves_global(self, name: str) -> bool:
        if name in self.comprehension_bindings:
            return False
        if name in self.function_local_names:
            return False
        try:
            symbol = self.function_symbol_table.lookup(name)
        except KeyError:
            # Python 3.11 keeps names used only in comprehensions in their
            # compiler-created child table. The function-local binding
            # inventory proves the repository name is global in the caller.
            return True
        if symbol.is_global():
            return not symbol.is_assigned() and not symbol.is_imported()
        # Python 3.12 and later inline list, set, and dict comprehensions. A
        # target then appears assigned in the function table even though its
        # binding remains isolated. Active comprehension bindings reject uses
        # inside the comprehension; the repository name remains global outside.
        return symbol.is_local() and symbol.is_assigned()

    def _resolve_static_callable(self, expression: ast.expr) -> str | None:
        if isinstance(expression, ast.Name) and self._resolves_global(expression.id):
            return self.global_functions.get(expression.id)
        if (
            isinstance(expression, ast.Attribute)
            and isinstance(expression.value, ast.Name)
            and self._resolves_global(expression.value.id)
        ):
            imported_module = self.global_modules.get(expression.value.id)
            if imported_module is not None:
                return self.exported_functions[imported_module].get(expression.attr)
        return None

    def _visit_decorator(self, decorator: ast.expr) -> None:
        self.visit(decorator)
        if isinstance(decorator, (ast.Name, ast.Attribute)):
            candidate = self._resolve_static_callable(decorator)
            if candidate is not None:
                self.calls.add(candidate)

    def visit_Call(self, node: ast.Call) -> None:
        candidate = self._resolve_static_callable(node.func)
        if candidate is not None:
            self.calls.add(candidate)
        self.generic_visit(node)

    def _visit_function_header(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for decorator in node.decorator_list:
            self._visit_decorator(decorator)
        _visit_argument_expressions(
            self,
            node.args,
            annotations_are_evaluated=self.annotations_are_evaluated,
        )
        if self.annotations_are_evaluated and node.returns is not None:
            self.visit(node.returns)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function_header(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function_header(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for decorator in node.decorator_list:
            self._visit_decorator(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        _visit_argument_expressions(
            self,
            node.args,
            annotations_are_evaluated=self.annotations_are_evaluated,
        )

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit executable target and value expressions, never a local annotation."""
        self.visit(node.target)
        if node.value is not None:
            self.visit(node.value)

    def _visit_comprehension(self, generators: list[ast.comprehension], result_nodes: tuple[ast.expr, ...]) -> None:
        first_generator, *remaining_generators = generators
        self.visit(first_generator.iter)
        original_bindings = set(self.comprehension_bindings)
        try:
            for generator in generators:
                self.comprehension_bindings.update(_assignment_names(generator.target))
            self.visit(first_generator.target)
            for condition in first_generator.ifs:
                self.visit(condition)
            for generator in remaining_generators:
                self.visit(generator.iter)
                self.visit(generator.target)
                for condition in generator.ifs:
                    self.visit(condition)
            for result_node in result_nodes:
                self.visit(result_node)
        finally:
            self.comprehension_bindings = original_bindings

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self._visit_comprehension(node.generators, (node.key, node.value))


def _module_inventory() -> tuple[dict[str, str], dict[str, Path]]:
    module_sources: dict[str, str] = {}
    source_paths: dict[str, Path] = {}
    for source_path in sorted(SOURCE_ROOT.glob("*.py")):
        module_name = source_path.stem
        module_sources[module_name] = source_path.read_text(encoding="utf-8")
        source_paths[module_name] = source_path
    return module_sources, source_paths


def _top_level_functions(syntax_tree: ast.Module) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {node.name: node for node in syntax_tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _symbol_table_kind(symbol_table: symtable.SymbolTable) -> str:
    table_kind = symbol_table.get_type()
    return str(getattr(table_kind, "value", table_kind))


def _globally_rebound_names(source: str, filename: str) -> frozenset[str]:
    """Return module names that any nested scope can explicitly rebind."""
    module_symbol_table = symtable.symtable(source, filename, "exec")
    rebound_names: set[str] = set()
    pending = list(module_symbol_table.get_children())
    while pending:
        symbol_table = pending.pop()
        for name in symbol_table.get_identifiers():
            symbol = symbol_table.lookup(name)
            if symbol.is_global() and (symbol.is_assigned() or symbol.is_imported()):
                rebound_names.add(name)
        pending.extend(symbol_table.get_children())
    return frozenset(rebound_names)


def _top_level_function_symbol_tables(
    source: str,
    filename: str,
    functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef],
) -> dict[str, symtable.SymbolTable]:
    module_symbol_table = symtable.symtable(source, filename, "exec")
    children_by_location: defaultdict[tuple[str, int], list[symtable.SymbolTable]] = defaultdict(list)
    for child in module_symbol_table.get_children():
        if _symbol_table_kind(child) == "function":
            children_by_location[(child.get_name(), child.get_lineno())].append(child)

    function_symbol_tables: dict[str, symtable.SymbolTable] = {}
    for function_name, function_node in functions.items():
        candidates = children_by_location[(function_name, function_node.lineno)]
        if len(candidates) != 1:
            raise RuntimeError(
                f"expected one symbol table for {function_name} at {filename}:{function_node.lineno}, "
                f"found {len(candidates)}"
            )
        function_symbol_tables[function_name] = candidates[0]
    return function_symbol_tables


def _stable_module_bindings(
    syntax_tree: ast.Module,
    module_name: str,
    repository_functions: frozenset[str],
    repository_modules: frozenset[str],
    globally_rebound_names: frozenset[str],
    *,
    annotations_are_evaluated: bool,
) -> dict[str, Binding]:
    collector = ModuleBindingCollector(
        module_name,
        annotations_are_evaluated=annotations_are_evaluated,
    )
    collector.visit(syntax_tree)
    if collector.has_star_import:
        return {}

    stable_bindings: dict[str, Binding] = {}
    for local_name, bindings in collector.bindings.items():
        if len(bindings) != 1 or local_name in globally_rebound_names:
            continue
        binding_kind, target = bindings[0]
        if binding_kind == "local_function" and target in repository_functions:
            stable_bindings[local_name] = (binding_kind, target)
        elif binding_kind == "imported_function" and target is not None:
            provider_module, separator, _ = target.rpartition(".")
            if separator and provider_module in repository_modules:
                stable_bindings[local_name] = (binding_kind, target)
        elif binding_kind == "module" and target in repository_modules:
            stable_bindings[local_name] = (binding_kind, target)
    return stable_bindings


def _repository_module_attribute_writes(
    syntax_tree: ast.Module,
    repository_modules: frozenset[str],
) -> dict[str, frozenset[str]]:
    """Return direct attributes written through imported repository aliases.

    Every syntactic import alias is a mutation candidate, even when later
    rebound. The conservative invalidation rule can omit a stable edge when a
    local value shadows the alias, but the rule cannot retain an edge whose
    visible repository export is directly assigned or deleted.
    """
    alias_targets: defaultdict[str, set[str]] = defaultdict(set)
    for node in ast.walk(syntax_tree):
        if not isinstance(node, ast.Import):
            continue
        for imported_name in node.names:
            imported_module = imported_name.name
            if imported_module not in repository_modules:
                continue
            local_name = imported_name.asname or imported_module.split(".")[0]
            alias_targets[local_name].add(imported_module)

    mutable_attributes: defaultdict[str, set[str]] = defaultdict(set)
    for node in ast.walk(syntax_tree):
        if not (
            isinstance(node, ast.Attribute)
            and isinstance(node.ctx, (ast.Store, ast.Del))
            and isinstance(node.value, ast.Name)
        ):
            continue
        for imported_module in alias_targets[node.value.id]:
            mutable_attributes[imported_module].add(node.attr)
    return {module_name: frozenset(attribute_names) for module_name, attribute_names in mutable_attributes.items()}


def _direct_call_graph(
    module_sources: dict[str, str], filenames: dict[str, str] | None = None
) -> dict[str, frozenset[str]]:
    filenames = filenames or {module_name: f"<{module_name}>" for module_name in module_sources}
    syntax_trees = {
        module_name: ast.parse(
            source,
            filename=filenames[module_name],
            feature_version=SOURCE_FEATURE_VERSION,
        )
        for module_name, source in module_sources.items()
    }
    annotations_are_evaluated = {
        module_name: not _uses_postponed_annotations(syntax_tree) for module_name, syntax_tree in syntax_trees.items()
    }
    functions_by_module = {
        module_name: _top_level_functions(syntax_tree) for module_name, syntax_tree in syntax_trees.items()
    }
    repository_functions = frozenset(
        f"{module_name}.{function_name}"
        for module_name, functions in functions_by_module.items()
        for function_name in functions
    )
    repository_modules = frozenset(module_sources)
    stable_bindings_by_module: dict[str, dict[str, Binding]] = {}
    for module_name in module_sources:
        globally_rebound_names = _globally_rebound_names(module_sources[module_name], filenames[module_name])
        stable_bindings_by_module[module_name] = _stable_module_bindings(
            syntax_trees[module_name],
            module_name,
            repository_functions,
            repository_modules,
            globally_rebound_names,
            annotations_are_evaluated=annotations_are_evaluated[module_name],
        )

    mutable_exports: defaultdict[str, set[str]] = defaultdict(set)
    for syntax_tree in syntax_trees.values():
        for provider_module, attribute_names in _repository_module_attribute_writes(
            syntax_tree,
            repository_modules,
        ).items():
            mutable_exports[provider_module].update(attribute_names)

    exported_functions: dict[str, dict[str, str]] = {module_name: {} for module_name in module_sources}
    for module_name, stable_bindings in stable_bindings_by_module.items():
        for local_name, (binding_kind, target) in stable_bindings.items():
            if (
                binding_kind == "local_function"
                and target is not None
                and local_name not in mutable_exports[module_name]
            ):
                exported_functions[module_name][local_name] = target

    unresolved_import_count = sum(
        binding_kind == "imported_function"
        for stable_bindings in stable_bindings_by_module.values()
        for binding_kind, _ in stable_bindings.values()
    )
    for _ in range(unresolved_import_count):
        resolution_changed = False
        for module_name, stable_bindings in stable_bindings_by_module.items():
            for local_name, (binding_kind, target) in stable_bindings.items():
                if binding_kind != "imported_function" or target is None:
                    continue
                if local_name in mutable_exports[module_name]:
                    continue
                provider_module, _, provider_name = target.rpartition(".")
                resolved_target = exported_functions[provider_module].get(provider_name)
                if resolved_target is not None and exported_functions[module_name].get(local_name) != resolved_target:
                    exported_functions[module_name][local_name] = resolved_target
                    resolution_changed = True
        if not resolution_changed:
            break

    graph: dict[str, frozenset[str]] = {}
    for module_name, functions in functions_by_module.items():
        global_functions = exported_functions[module_name]
        global_modules = {
            local_name: target
            for local_name, (binding_kind, target) in stable_bindings_by_module[module_name].items()
            if binding_kind == "module" and target is not None
        }
        function_symbol_tables = _top_level_function_symbol_tables(
            module_sources[module_name], filenames[module_name], functions
        )
        for function_name, function_node in functions.items():
            binding_collector = FunctionBindingCollector(
                function_node.args,
                annotations_are_evaluated=annotations_are_evaluated[module_name],
            )
            for statement in function_node.body:
                binding_collector.visit(statement)
            collector = DirectCallCollector(
                global_functions,
                global_modules,
                exported_functions,
                function_symbol_tables[function_name],
                binding_collector.local_names,
                annotations_are_evaluated=annotations_are_evaluated[module_name],
            )
            for statement in function_node.body:
                collector.visit(statement)
            graph[f"{module_name}.{function_name}"] = frozenset(collector.calls)
    return graph


def _reachable_subgraph(
    graph: dict[str, frozenset[str]], root_function: str
) -> tuple[frozenset[str], frozenset[tuple[str, str]]]:
    if root_function not in graph:
        raise ValueError(f"unknown root function {root_function}")
    reachable_functions: set[str] = set()
    reachable_edges: set[tuple[str, str]] = set()
    pending = deque([root_function])
    while pending:
        caller = pending.popleft()
        if caller in reachable_functions:
            continue
        reachable_functions.add(caller)
        for callee in graph[caller]:
            reachable_edges.add((caller, callee))
            if callee not in reachable_functions:
                pending.append(callee)
    return frozenset(reachable_functions), frozenset(reachable_edges)


def _verify_call_resolution() -> None:
    fixture_sources = {
        "other": "def target():\n    return None\n",
        "rebound_provider": """
def replacement():
    return None

def target():
    return None

target = replacement
""",
        "deleted_provider": """
def target():
    return None

del target
""",
        "provider_importer": """
from rebound_provider import target as rebound_from
from deleted_provider import target as deleted_from
import rebound_provider as rebound_module
import deleted_provider as deleted_module

def rebound_from_shadow():
    rebound_from()

def deleted_from_shadow():
    deleted_from()

def rebound_module_shadow():
    rebound_module.target()

def deleted_module_shadow():
    deleted_module.target()
""",
        "mutated_provider": """
def replacement():
    return None

def target():
    return None
""",
        "provider_mutator": """
import mutated_provider

def mutate_export():
    mutated_provider.target = mutated_provider.replacement
""",
        "provider_user": """
from mutated_provider import target as imported_target
import mutated_provider

def imported_mutation_shadow():
    imported_target()

def module_mutation_shadow():
    mutated_provider.target()
""",
        "future_fixture": """
from __future__ import annotations

from other import target

def postponed_header_shadow():
    observed = target
    def inner(value: target()) -> target():
        return value
    return observed, inner
""",
        "eager_fixture": """
from other import target

def eager_header_positive():
    observed = target
    def inner(value: target()) -> target():
        return value
    return observed, inner
""",
        "fixture": """
from other import target as imported_target
from other import target as mutable_target
from other import target as class_mutable_target
import other as other_module

def target():
    return None

def direct_positive():
    target()

def imported_positive():
    imported_target()

def module_positive():
    other_module.target()

def parameter_shadow(target):
    target()

def assignment_shadow():
    target()
    target = replacement

def annotated_assignment_shadow():
    target: object
    target()

def local_annotation_shadow():
    observed = target
    local_value: target()
    return observed

def named_expression_shadow(value):
    target()
    (target := value)

def destructuring_shadow(values):
    first, target = values
    target()

def loop_shadow(values):
    for target in values:
        target()

def with_shadow(manager):
    with manager as target:
        target()

def exception_shadow():
    try:
        raise RuntimeError
    except RuntimeError as target:
        target()

def nested_definition_shadow():
    def target():
        return None
    target()

def local_import_shadow():
    from other import target
    target()

def global_positive():
    global target
    target()

def global_rebind_shadow():
    global mutable_target
    mutable_target = replacement
    mutable_target()

def cross_function_global_rebind_shadow():
    mutable_target()

class GlobalMutator:
    global class_mutable_target
    class_mutable_target = replacement

def class_global_rebind_shadow():
    class_mutable_target()

def comprehension_shadow(values):
    return [target() for target in values]

def list_comprehension_positive(values):
    return [target() for value in values]

def set_comprehension_positive(values):
    return {target() for value in values}

def dict_comprehension_positive(values):
    return {value: target() for value in values}

def generator_expression_positive(values):
    return (target() for value in values)

def comprehension_outer_iter_positive():
    return [value for target in target()]

def comprehension_later_iter_shadow(values):
    return [value for value in values for target in target()]

def comprehension_outer_positive(values):
    [value for value in values]
    target()

def comprehension_walrus_shadow(values):
    [(target := value) for value in values]
    target()

def decorator_positive():
    @target
    def inner():
        return None
    return inner

def module_decorator_positive():
    @other_module.target
    def inner():
        return None
    return inner

def decorator_factory_positive():
    @target()
    def inner():
        return None
    return inner

def module_parameter_shadow(other_module):
    other_module.target()

rebound_target = imported_target

def assigned_alias_shadow():
    rebound_target()
""",
    }
    graph = _direct_call_graph(fixture_sources)
    expected_edges = {
        "fixture.direct_positive": {"fixture.target"},
        "fixture.imported_positive": {"other.target"},
        "fixture.module_positive": {"other.target"},
        "fixture.parameter_shadow": set(),
        "fixture.assignment_shadow": set(),
        "fixture.annotated_assignment_shadow": set(),
        "fixture.local_annotation_shadow": set(),
        "fixture.named_expression_shadow": set(),
        "fixture.destructuring_shadow": set(),
        "fixture.loop_shadow": set(),
        "fixture.with_shadow": set(),
        "fixture.exception_shadow": set(),
        "fixture.nested_definition_shadow": set(),
        "fixture.local_import_shadow": set(),
        "fixture.global_positive": {"fixture.target"},
        "fixture.global_rebind_shadow": set(),
        "fixture.cross_function_global_rebind_shadow": set(),
        "fixture.class_global_rebind_shadow": set(),
        "fixture.comprehension_shadow": set(),
        "fixture.list_comprehension_positive": {"fixture.target"},
        "fixture.set_comprehension_positive": {"fixture.target"},
        "fixture.dict_comprehension_positive": {"fixture.target"},
        "fixture.generator_expression_positive": {"fixture.target"},
        "fixture.comprehension_outer_iter_positive": {"fixture.target"},
        "fixture.comprehension_later_iter_shadow": set(),
        "fixture.comprehension_outer_positive": {"fixture.target"},
        "fixture.comprehension_walrus_shadow": set(),
        "fixture.decorator_positive": {"fixture.target"},
        "fixture.module_decorator_positive": {"other.target"},
        "fixture.decorator_factory_positive": {"fixture.target"},
        "fixture.module_parameter_shadow": set(),
        "fixture.assigned_alias_shadow": set(),
        "provider_importer.rebound_from_shadow": set(),
        "provider_importer.deleted_from_shadow": set(),
        "provider_importer.rebound_module_shadow": set(),
        "provider_importer.deleted_module_shadow": set(),
        "provider_user.imported_mutation_shadow": set(),
        "provider_user.module_mutation_shadow": set(),
        "future_fixture.postponed_header_shadow": set(),
        "eager_fixture.eager_header_positive": {"other.target"},
    }
    for caller, expected_callees in expected_edges.items():
        observed_callees = graph[caller]
        if observed_callees != frozenset(expected_callees):
            raise RuntimeError(
                f"call-resolution fixture {caller} produced {sorted(observed_callees)}, "
                f"expected {sorted(expected_callees)}"
            )

    # PEP 695 type parameters arrived in Python 3.12; below that target the
    # mapper rejects them as newer syntax.
    if SOURCE_FEATURE_VERSION < (3, 12):
        try:
            _direct_call_graph({"newer_syntax": "def identity[Value](value: Value) -> Value:\n    return value\n"})
        except SyntaxError:
            pass
        else:
            raise RuntimeError(f"call mapper accepted syntax newer than configured Python {SOURCE_FEATURE_VERSION}")


def main() -> int:
    _verify_call_resolution()
    module_sources, source_paths = _module_inventory()
    graph = _direct_call_graph(
        module_sources, {module_name: str(source_path) for module_name, source_path in source_paths.items()}
    )
    all_edges = frozenset((caller, callee) for caller, callees in graph.items() for callee in callees)
    print(f"modules\t{len(source_paths)}")
    print(f"functions\t{len(graph)}")
    print(f"direct_edges\t{len(all_edges)}")
    for caller, callee in sorted(all_edges):
        print(f"edge\t{caller}\t{callee}")

    union_functions: set[str] = set()
    union_edges: set[tuple[str, str]] = set()
    for root_function in ROOT_FUNCTIONS:
        reachable_functions, reachable_edges = _reachable_subgraph(graph, root_function)
        union_functions.update(reachable_functions)
        union_edges.update(reachable_edges)
        print(f"root\t{root_function}\tfunctions={len(reachable_functions)}\tedges={len(reachable_edges)}")
    print(f"root_union\tfunctions={len(union_functions)}\tedges={len(union_edges)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
