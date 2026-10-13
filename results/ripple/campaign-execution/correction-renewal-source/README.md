# Correction renewal source artifacts

These files are the script, log, and exit marker that
`../current-correction-renewal-rejection.json` names in `source_identity`.
Each copy replaces the operator's home directory prefix with the literal
token `@HOME@` and changes nothing else. Replacing `@HOME@` with the original
prefix reproduces the bytes whose sha256 the receipt records:

```sh
sed 's#@HOME@#/home/OPERATOR#g' current-campaign-correction-renewal.sh | sha256sum
```

with `OPERATOR` set to the recording account. The script carries no
`--submit` argument.
