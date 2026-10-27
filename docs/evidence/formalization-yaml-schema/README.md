# formalization.yaml schema, retained bytes

`v0.4.schema.json` is the mathlib-initiative schema that the root
[formalization.yaml](../../../formalization.yaml) declares, retained so a
reviewer without network access validates the file against the same bytes.

- Source: https://raw.githubusercontent.com/mathlib-initiative/formalization.yaml/main/schema/v0.4.schema.json,
  fetched 2026-10-27 from the `main` branch of
  https://github.com/mathlib-initiative/formalization.yaml.
- SHA-256 of the retained file: see `SHA256SUMS`; `sha256sum -c SHA256SUMS`
  from this directory checks it.

## Validation

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -I -c '
import json, sys, yaml, jsonschema
schema = json.load(open("docs/evidence/formalization-yaml-schema/v0.4.schema.json"))
doc = yaml.safe_load(open("formalization.yaml"))
errors = list(jsonschema.Draft7Validator(schema).iter_errors(doc))
for e in errors: print(list(e.path), e.message)
sys.exit(1 if errors else 0)'
```

The command needs PyYAML and jsonschema, which the pinned test environment
does not install, so the validation is a documented replay rather than a
gate. Recorded run: jsonschema 4.26.0 with PyYAML 6.0.3 on 2026-10-27
reports no error on the formalization.yaml of pull request 581.
