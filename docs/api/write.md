# Write Functions

Each of these functions takes a {class}`~cdl_convert.correction.ColorCorrection` as an arg, then places as many attributes of the {class}`~cdl_convert.correction.ColorCorrection` that the format supports into a properly formatted string or XML Tree, then writes that file.

## write_cc

Write XML Color Correction (cc) files.

```{eval-rst}
.. autofunction:: cdl_convert.write.write_cc
```

## write_ccc

Write XML Color Correction Collection (ccc) files.

```{eval-rst}
.. autofunction:: cdl_convert.write.write_ccc
```

## write_cdl

Write XML Color Decision List (cdl) files.

```{eval-rst}
.. autofunction:: cdl_convert.write.write_cdl
```

## write_nk

Write Foundry Nuke OCIOCDLTransform node files.

This writes a Nuke script file containing an OCIOCDLTransform node with the CDL color correction values. The generated file can be directly loaded into Nuke and will apply the specified color correction.

```{eval-rst}
.. autofunction:: cdl_convert.write.write_nk
```

## write_rnh_cdl

Write Rhythm & Hues CDL format.

This writes a very sparse cdl format that is based on a very early spec of the cdl implementation. It lacks all metadata. Unless you work at Rhythm & Hues, a 
VFX company which hasn't existed for years now, you probably don't want to write a cdl that uses this format.

```{eval-rst}
.. autofunction:: cdl_convert.write.write_rnh_cdl
```
