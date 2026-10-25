> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/command.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/command.html)
> Retrieved 2026-10-25T09:12Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 7c1fb4e946f3a74c6f20e44a3f548b28622f9889786b6bf03739810b22a108fd.

# Command

A `Command` describes a type of method through a name and an ordered parameter signature. It does not perform any work itself: a [Computation](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/remote_processor.html#computation) associates it with an experiment, and a [Computer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#computer) implements the command.

The signature is a list of `(name,`` ``expected_type,`` ``mandatory)` tuples. For example, a command requiring an integer `count` and accepting an optional string `label` can be defined as follows:

``` default
>>> import perceval as pcvl
>>>
>>> command = pcvl.Command(
...     "custom_command",
...     [("count", int, True), ("label", str, False)],
... )
```

Set the expected type to `None` to accept a value of any type. The order of the signature determines how positional arguments are assigned.

## Filling and checking parameters

The `fill()` method maps positional and keyword arguments to the signature and checks argument names and types:

``` default
>>> command.fill(10, label="example")
{'count': 10, 'label': 'example'}
```

It raises `TypeError` for too many positional arguments, unknown or duplicate names, and values of the wrong type. Any parameter may be omitted. `check()` performs the separate final check that all mandatory parameters are present:

``` default
>>> parameters = command.fill(count=10)
>>> command.check(parameters)
```

## Error mitigation

The `apply_emt` attribute indicates whether error-mitigation techniques may expand and post-process a computation using this command. It defaults to `True`; custom commands whose results are not compatible with error mitigation should set it to `False`:

``` default
>>> command = pcvl.Command("custom_command", [], apply_emt=False)
```

## Class reference

*class* perceval.runtime.command.Command(*name*, *signature*, *apply_emt=True*)  
Describes a command through a name and a signature

The signature is exposed with a list of (name, expected type, is_mandatory)

check(*parameters*)  
Checks if the parameters are valid

Parameters:  
**parameters** (`dict`\[`str`, `Any`\]) – The final parameters that will be given as `**kwargs` in the command

fill(*\*args*, *\*\*kwargs*)  
Parameters:  
- **args** – The user given positional arguments

- **kwargs** – The user given keyword arguments

Raises:  
**TypeError** – If arguments do not match signature

Return type:  
`dict`\[`str`, `Any`\]

Returns:  
A dictionary to use as `**kwargs` in the final command, compatible with the signature
