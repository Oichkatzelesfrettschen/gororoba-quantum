> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9440b6891221c0a10ff73f9b57c7fe401c4c4d6224188b9cf94296d1c67947c1.

# setting_node

Full path: exa.common.data.setting_node

A tree-structured container for [`Settings`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Setting.html#exa.common.data.parameter.Setting "exa.common.data.parameter.Setting").

The [`SettingNode`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode") class combines a bunch of Settings together. It may also contain other SettingNodes. Together, the contents form a tree structure that provides a useful way of grouping Settings.

As an example, we manually construct a tree of SettingNodes with some dummy Settings, but it is usually not necessary. The root node in the following examples is called `'node'`.

## What’s inside?

The easiest way to see the content of the node is the [`SettingNode.print_tree()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode.print_tree "exa.common.data.setting_node.SettingNode.print_tree") method:

```
 >>> node.print_tree(levels=1)
  "root"
  ║
  ╚═ flux: "root.flux"
  ╚═ pulse: "root.pulse"
```

We see that the `'root'` node has two children, named `'root.flux'` and `'root.pulse'`, which themselves are also SettingNodes. This follows the typical naming convention in EXA: Subnodes include the names of their parents, separated by a dot.

In a Jupyter notebook, evaluating a node in a cell renders it as an interactive, collapsible tree where each subtree is loaded only when expanded (handy for large systems). This requires `ipywidgets`, installed via the `iqm-exa-common[notebook]` extra; without it the node falls back to a static summary.

```
 >>> node.print_tree()
  "root"
  ║
  ╠═ flux: "root.flux"
  ║   ╠─ voltage: Voltage = 1.5 V
  ║   ╚─ resistance: Resistance = None (automatic/unspecified)
  ╚═ pulse: "root.pulse"
      ╠─ amplitude: Amplitude = 1.0
      ╚─ duration: Duration = 1e-07 s
```

The children contain some dummy Settings, showing the keys, labels and current values.

For other ways to access the content of the node, see also [`SettingNode.children`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode.children "exa.common.data.setting_node.SettingNode.children"), [`SettingNode.all_settings`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode.all_settings "exa.common.data.setting_node.SettingNode.all_settings"), and [`SettingNode.nodes_by_type()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode.nodes_by_type "exa.common.data.setting_node.SettingNode.nodes_by_type").

## Get and set values

The values within the nodes can be accessed using the attribute or dictionary syntax:

```
>>> node.pulse.amplitude.value
1.0
>>> node['flux']['voltage'].value
1.5
```

The values can be changed with a simple `=` syntax:

```
>>> node.pulse.amplitude = 1.4
>>> node.pulse.amplitude.value
1.4
```

Note

`node.setting` refers to the Setting object. `node.setting.value` syntax refers to the data stored inside.

`SettingNode` also supports “the path notation” by default (but not if `align_name` is set to `False`, since it cannot be made to work consistently if nodes are allowed to be named differently from their paths):

```
>>> node['flux.voltage']
```

is the same as `node['flux']['voltage']`.

## Basic manipulation

Adding and deleting new Settings and nodes is simple:

```
>>> modified = node.copy()
>>> del modified.flux # removes the node
>>> del modified.pulse.amplitude # removes the Setting
>>> modified.pulse.my_new_setting = Setting(Parameter('my name'), 33)
```

It is usually a good idea to make a copy of the original node, so that it won’t be modified accidentally.

The path notation of `SettingNode` also works when inserting:

```
>>> node['flux.my.new.path.foo'] = Setting(Parameter('foo'), 1.0)
```

Any nodes that did not already exist under `node` will be inserted (in this case `flux` already existed, but the rest not, so under `flux` the nodes `my`, `new`, and `path` would be added), and then finally the value is added as child to the final node. Note: `SettingNode` always aligns the path and name of any nodes under it, so this would result in the new setting being renamed as “flux.my.new.path.foo”:

```
>>> node['flux.my.new.path.foo'] = Setting(Parameter('bar'), 1.0)
```

If `align_name` is set to ``` False", the name and path of nodes are not automatically aligned, but otherwise the above path notation will still work. The added nodes will be named by just their path fragments ("my", "new", "path", and so on), and the Setting will be added under the key "foo", but it will still retain its name "bar". Note: the root node name will always be excluded from the paths (and names when they are aligned with the path), so that the path of ``root.foo.bar ``` is `"foo.bar"`.

To merge values of two SettingNodes, there are helpers [`SettingNode.merge()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode.merge "exa.common.data.setting_node.SettingNode.merge") and [`SettingNode.merge_values()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode.merge_values "exa.common.data.setting_node.SettingNode.merge_values").

The first one merges the tree structure and values of two nodes and outputs a third one as a result. `None` values are always replaced by a proper value if such exists. In case of conflicting nodes or values, the content of the first argument takes priority.

```
>>> result = SettingNode.merge(node.flux, node.pulse)
>>> result.print_tree()
 "root.flux"
 ╠─ amplitude: Amplitude = 1.4
 ╠─ duration: Duration = 1e-07 s
 ╚─ voltage: Voltage = 1.5 V
```

Note how the result has values from `node.flux`, but also settings `node.pulse` that do not exist in `node.flux`.

The [`SettingNode.merge_values()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode.merge_values "exa.common.data.setting_node.SettingNode.merge_values") method is an in-place operation that only changes the values of Settings that already exist in the node, if possible:

```
>>> modified = node.copy()
>>> modified.flux.voltage = 222
>>> modified.flux.resistance = 333
>>> node.merge_values(modified, prioritize_other=True)
>>> node.print_tree()
 "root"
 ║
 ╠═ flux: "root.flux"
 ║   ╠─ voltage: Voltage = 222 V
 ║   ╚─ resistance: Resistance = 333 Ohm
 ╚═ pulse: "root.pulse"
     ╠─ amplitude: Amplitude = 1.4
     ╚─ duration: Duration = 1e-07 s
```

Sometimes, it is easier to collect values in a dictionary and set them all at once by using [`SettingNode.set_from_dict()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode.set_from_dict "exa.common.data.setting_node.SettingNode.set_from_dict"). The nested structure of the dictionary should match the structure of the SettingNode. Keys that are not found in the tree are silently ignored, unless the `strict` flag is used.

```
>>> values_to_set = {'flux': {'resistance': 0.001}, 'ignored_entry': 234}
>>> node.set_from_dict(values_to_set)
>>> node.flux.print_tree()
 "root.flux"
 ╠─ voltage: Voltage = 222 V
 ╚─ resistance: Resistance = 0.001 Ohm
```

Classes

|  |  |
|----|----|
| [`SettingNode`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode") | A tree-structured [`Setting`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Setting.html#exa.common.data.parameter.Setting "exa.common.data.parameter.Setting") container. |

Inheritance

![Inheritance diagram of exa.common.data.setting_node](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-83ffaa06fbe5e44d279c0fc78175b2cf58113c7d.png)
