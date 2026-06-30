# Cleanup Safety Reference

Loaded on demand when a cleanup operation touches risky territory: dynamic
dispatch, public API surface, or test strategy. This is the detail behind the
Contract in `SKILL.md`. When this reference and a tight deadline conflict, the
Contract wins.

The core risk of any cleanup is **deleting or moving code that is still
reached**, which changes behavior. A naive grep misses dynamic reach. This file
tells you where dynamic reach hides and how to prove a deletion is safe.

## Dynamic reference patterns by language

Before deleting or renaming a symbol, grep the whole repo for these patterns.
A hit means the symbol may be reached dynamically: keep it, or rename every
call site, never just delete.

### Python

- `getattr(obj, "name")` and `getattr(obj, "name", default)`.
- `importlib.import_module("name")`, `__import__("name")`.
- `setattr`, `delattr`, `hasattr` with string literals.
- `obj.__dict__["name"]`, `globals()["name"]`, `locals()["name"]`.
- `typing.get_type_hints`, plugin/registry decorators that register by string.
- `__all__` gates what `from module import *` exports. A name not in `__all__`
  may still be imported directly; do not assume `__all__` is the full surface.

### JavaScript and TypeScript

- Dynamic `import("name")`, `require(varName)` with a non-literal.
- `obj["name"]`, `window["name"]`, `globalThis["name"]`, bracket member access
  with a string variable.
- `eval`, `new Function(...)`.
- Framework registries: React component maps, Next.js dynamic routes, NestJS
  providers, Express route strings. These resolve handlers by string at runtime.
- `package.json` `exports`, `main`, `module`, `types` fields define the public
  surface. Anything under a published path is public even without a doc comment.

### Ruby

- `obj.send(:name)`, `public_send`, `__send__`.
- `Object.const_get("Name")`, `const_defined?`.
- `method(:name).call`, `define_method`, `method_missing`.
- Rails conventions: `User` from `"user".classify.constantize`. String table
  and class names resolve dynamically.

### PHP

- `$container->get("name")`, `$container->get(Class::class)`.
- `call_user_func`, `call_user_func_array`, `$obj->$method()`.
- Symfony and Laravel service containers, autowiring, event subscriber tags.
- Composer `autoload` PSR-4 roots define the public path surface.

### C# and Java

- Reflection: `GetMethod("Name")`, `GetMethod("name", BindingFlags)`,
  `Class.forName("name")`.
- DI containers resolve by interface or string id.
- Source generators and annotation processors inject code at build time; grep
  will not show those call sites.

### Go and Rust

- Go `reflect`, interface satisfaction by method set, `plugin` package.
- Rust macros and `inventory`/`linkme` registration generate call sites at
  compile time. Generated code is invisible to grep.

## Public API surface, how to identify it

A change is internal-only when it does not cross the public surface. Find the
surface first, then stay inside it.

- **Exports and package manifests.** Python `__all__` and top-level names;
  `package.json` `exports`/`main`/`module`/`types`; Rust `pub` items and
  `lib.rs`; Go capitalized identifiers; Java/Kotlin public classes; C#
  `public` members; Ruby `module_function` and constants in documented API.
- **Type signatures.** Public function and method signatures, including
  parameter and return types, are part of the surface. Splitting must preserve
  them.
- **Module paths.** Import paths that callers use are public. Preserve them
  with re-exports when you move a file: the old path re-exports from the new
  location so existing imports keep working.
- **Serialized forms.** Anything written to disk, sent over the wire, or stored
  in a config (JSON keys, DB columns, env var names, log field names) is a
  public contract. Do not rename these during cleanup.
- **Documented or tested names.** If a README, docstring, or test references a
  name, assume a caller does too.

When you cannot prove a name is internal, treat it as public. Keep it.

## Test strategy

Tests are the proof that behavior is unchanged. Adapt to what the repo has.

- **Detect the runner.** Look for `pytest`, `unittest`, `jest`/`vitest`,
  `rspec`, `phpunit`, `go test`, `cargo test`, `dotnet test`, `make test`, or a
  `package.json` `test` script. Run that exact command.
- **Baseline first.** Run the suite before any change. If it is already red,
  stop and tell the human; you cannot prove a later green if the start was red.
- **After every change.** Re-run after each logical edit. Green after a red
  baseline proves nothing; only green-after-green-from-green is evidence.
- **No suite present.** If there are no tests, say so and ask. Do not clean by
  faith. Offer to add a minimal characterization test around the area first.
- **Narrow then broad.** Run the targeted test for the file you touched, then
  the full suite before finishing. Both must pass.

## Rollback

Use git as the safety net so a failed step never lingers.

- Work in small commits, one logical change each.
- After a failing test you did not cause, revert immediately:
  `git restore <path>` or `git checkout -- <path>` for unstaged work,
  `git reset --hard` only if you are sure nothing else uncommitted matters.
- Never pile a second change on top of a red step. Revert first, re-baseline,
  then continue.

## When to stop and ask

- The codebase uses a framework registry or plugin system and you cannot tell
  whether a symbol is registered dynamically.
- A deletion would touch a serialized form or a documented name.
- There is no test suite and the change is not trivially safe.
- Tests are red at the start.

In all four cases, keep the code and surface the question. Keeping code that
might be used is always cheaper than silently changing behavior.
