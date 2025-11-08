# Utility Functions

## reset_all

Resets all the class level lists and dictionaries of cdl_convert. Calling this is the same as calling each individual `reset_members` method.

```{eval-rst}
.. autofunction:: cdl_convert.reset_all
```

## sanity_check

Check {class}`~cdl_convert.correction.ColorCorrection` values for potentially invalid numbers.

```{eval-rst}
.. autofunction:: cdl_convert.utils.sanity_check
```

## to_decimal

This is the function we use to convert ints, floats and strings to Decimal objects. We do NOT attempt to use maximum accuracy on floats passed in, as that results in extremely long values more often than not. Better to just truncate the float with a string conversion, than attempt to perfectly represent with a Decimal.

```{eval-rst}
.. autofunction:: cdl_convert.utils.to_decimal
```
