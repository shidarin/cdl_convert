# Classes

## ColorCorrection

The {class}`~cdl_convert.correction.ColorCorrection` class is the backbone of cdl_convert, as it represents the basic level of the color decision list concept- the color decision list itself. All the parse functions exist to extract the CDL metadata and populate this class, and all the write functions exist to write files out from this class.

Parser → {class}`~cdl_convert.correction.ColorCorrection` → Writer

{class}`~cdl_convert.correction.ColorCorrection` can be instantiated and used without a parse function, see {doc}`../usage` for a walkthrough.

:::{warning}
When an instance of {class}`~cdl_convert.correction.ColorCorrection` is first created, the `id` provided is checked against a class level dictionary variable named `members` to ensure that no two {class}`~cdl_convert.correction.ColorCorrection` share the same `id`, as this is required by the specification.

If the `id` does match an already created `id` and `HALT_ON_ERROR` is not set, the `id` assignment will go forward, appending the duplicate number to the back of the `id`. So the 2nd instance of 'sh100cc' will become 'sh100cc001'.

Reset the members dictionary by either calling the `reset_members` method on {class}`~cdl_convert.correction.ColorCorrection` or by reseting all cdl_convert member lists and dictionaries with the {func}`~cdl_convert.reset_all` function.
:::

```{eval-rst}
.. autoclass:: cdl_convert.correction.ColorCorrection
   :members:
   :undoc-members:
   :show-inheritance:
```

## ColorCollection

This class functions as both a ColorDecisionList and a ColorCorrectionCollection. Its children can be either ColorDecisions, ColorCorrections, or a combination of the two. Despite being able to have either type of child, the {class}`~cdl_convert.collection.ColorCollection` still needs to know which type of collection you want it to represent.

Setting the `type` of the {class}`~cdl_convert.collection.ColorCollection` to either `ccc` or `cdl` causes children of the opposite type to be converted into the appropriate type when exporting the class.

```{eval-rst}
.. autoclass:: cdl_convert.collection.ColorCollection
   :members:
   :undoc-members:
   :show-inheritance:
```

## ColorDecision

ColorDecision's are normally found only within {class}`~cdl_convert.collection.ColorCollection` but this limitation of the ASC CDL schema is not enforced by cdl_convert.

```{eval-rst}
.. autoclass:: cdl_convert.decision.ColorDecision
   :members:
   :undoc-members:
   :show-inheritance:
```

## ColorCorrectionRef

```{eval-rst}
.. autoclass:: cdl_convert.decision.ColorCorrectionRef
   :members:
   :undoc-members:
   :show-inheritance:
```

## MediaRef

Media Ref's are normally found only inside of {class}`~cdl_convert.decision.ColorDecision`, which itself is found only inside of the ColorDecisionList collection. This isn't a restriction that `cdl_convert` explicitly enforces, but the parse and write functions will only be creating and writing found {class}`~cdl_convert.decision.MediaRef` objects following the rules.

Where possible when writing filetypes that don't support {class}`~cdl_convert.decision.MediaRef`, the information kept in {class}`~cdl_convert.decision.MediaRef` will be converted into description field metadata and preserved in that way.

{class}`~cdl_convert.decision.MediaRef` is meant to provide a convenient interface for managing and interpreting data stored in CDLs. You can change a broken absolute link directory to a relative link without touching the filename, or retrieve a full list of image sequences contained within a referenced directory.

```{eval-rst}
.. autoclass:: cdl_convert.decision.MediaRef
   :members:
   :undoc-members:
   :show-inheritance:
```

## SopNode

:::{note}
This class is meant only to be created by a {class}`~cdl_convert.correction.ColorCorrection`, and thus has the required arg of `parent` when instantiating it.
:::

:::{warning}
Setting any of the sop node values with a single value as in `offset = 5.4` will cause that value to be copied over all 3 colors, resulting in `[5.4, 5.4, 5.4]`.
:::

```{eval-rst}
.. autoclass:: cdl_convert.correction.SopNode
   :members:
   :undoc-members:
   :show-inheritance:
```

## SatNode

:::{note}
This class is meant only to be created by a {class}`~cdl_convert.correction.ColorCorrection`, and thus has the required arg of `parent` when instantiating it.
:::

```{eval-rst}
.. autoclass:: cdl_convert.correction.SatNode
   :members:
   :undoc-members:
   :show-inheritance:
```

## Base Classes

### AscColorSpaceBase

Classes that deal with input and viewer colorspace can subclass from this class to get the `input_desc` and `viewing_desc` attributes.

```{eval-rst}
.. autoclass:: cdl_convert.base.AscColorSpaceBase
   :members:
   :undoc-members:
   :show-inheritance:
```

### AscDescBase

Classes that are allowed to have a description field subclass from this class to get the `desc` attribute. The `desc` attribute can be set with a single string, which will append to the list of strings already present in `desc`. If set to a list or tuple, `desc` will become a list of those values. If set to `None`, `desc` will become an empty list.

```{eval-rst}
.. autoclass:: cdl_convert.base.AscDescBase
   :members:
   :undoc-members:
   :show-inheritance:
```

### AscXMLBase

```{eval-rst}
.. autoclass:: cdl_convert.base.AscXMLBase
   :members:
   :undoc-members:
   :show-inheritance:
```

### ColorNodeBase

This class only exists to be subclassed by {class}`~cdl_convert.correction.SatNode` and {class}`~cdl_convert.correction.SopNode` and should not be used directly.

```{eval-rst}
.. autoclass:: cdl_convert.base.ColorNodeBase
   :members:
   :undoc-members:
   :show-inheritance:
```
