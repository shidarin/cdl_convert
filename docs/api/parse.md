# Parse Functions

These functions can either return a {class}`~cdl_convert.correction.ColorCorrection`, or a {class}`~cdl_convert.collection.ColorCollection`, depending on if they are from a container format.

:::{note}
Use the {func}`~cdl_convert.parse.parse_file` function to parse any input file correctly, without worrying about matching the file extension by hand.
:::

## parse_file

Passes on the file to the correct parser based on auto-detection.

```{eval-rst}
.. autofunction:: cdl_convert.parse.parse_file
```

## parse_ale

Parse Avid Log Exchange (ALE) files.

```{eval-rst}
.. autofunction:: cdl_convert.parse.parse_ale
```

## parse_cc

Parse XML Color Correction (cc) files.

```{eval-rst}
.. autofunction:: cdl_convert.parse.parse_cc
```

## parse_ccc

Parse XML Color Correction Collection (ccc) files.

```{eval-rst}
.. autofunction:: cdl_convert.parse.parse_ccc
```

## parse_cdl

Parse XML Color Decision List (cdl) files.

```{eval-rst}
.. autofunction:: cdl_convert.parse.parse_cdl
```

## parse_cmx

Parse CMX EDL files using OpenTimelineIO.

```{eval-rst}
.. autofunction:: cdl_convert.parse.parse_cmx
```

## parse_flex

Parse Film Log EDL Exchange (FLEx) files.

```{eval-rst}
.. autofunction:: cdl_convert.parse.parse_flex
```

## parse_nk

Parse Foundry Nuke OCIOCDLTransform node files.

Nuke's OCIOCDLTransform node format is a simple text-based format used for exchanging CDL corrections in Nuke-based VFX and compositing workflows.

```{eval-rst}
.. autofunction:: cdl_convert.parse.parse_nk
```

## parse_otio

Parse OpenTimelineIO timeline files with embedded CDL metadata.

```{eval-rst}
.. autofunction:: cdl_convert.parse.parse_otio
```

## parse_rnh_cdl

Parse Rhythm & Hues CDL format.

Rhythm & Hues' implementation of the cdl format is based on a very early spec, and as such lacks all metadata. It's extremely unlikely that you'll run into this format in the wild.

But it's here, because I miss Rhythm greatly.

```{eval-rst}
.. autofunction:: cdl_convert.parse.parse_rnh_cdl
```
