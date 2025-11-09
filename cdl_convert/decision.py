#!/usr/bin/env python
"""CDL Convert Decision Module

This module contains classes for managing color decisions and media references
in ASC CDL workflows, providing type-safe containers for linking color
corrections with reference media.

Classes:
    ColorCorrectionRef: Reference to existing ColorCorrection instances.
        References are validated when accessed if strict mode is enabled.

    ColorDecision: Container linking ColorCorrections with MediaRefs.
        Supports both direct corrections and correction references.

    MediaRef: Media reference handler with pathlib integration for
        file operations, sequence detection, and path manipulation.

Example Usage:
    >>> from pathlib import Path
    >>> from cdl_convert import ColorCorrection, ColorDecision, MediaRef
    >>>
    >>> # Create correction and media reference
    >>> cc = ColorCorrection("shot_001")
    >>> media = MediaRef(Path("footage/shot_001.%04d.exr"))
    >>>
    >>> # Create decision linking correction to media
    >>> decision = ColorDecision(cc, media_ref=media)
    >>>
    >>> if media.exists():
    ...     print(f"Media found: {media.ref}")
    >>>
    >>> try:
    ...     decision.validate_references()
    ... except ValidationError as e:
    ...     print(f"Validation error: {e}")

## License

The MIT License (MIT)

cdl_convert
Copyright (c) 2015-2025 Sean Wallitsch
http://github.com/shidarin/cdl_convert/

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

# ==============================================================================
# IMPORTS
# ==============================================================================


# Standard Imports

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union
from xml.etree import ElementTree

# cdl_convert imports
from cdl_convert import config
from cdl_convert.base import AscColorSpaceBase, AscDescBase, AscXMLBase
from cdl_convert.correction import ColorCorrection
from cdl_convert.exceptions import ParseError, ValidationError

# ==============================================================================
# DATACLASSES
# ==============================================================================


@dataclass
class MediaRefInfo:
    """Container for parsed media reference URI components.

    Stores the individual components of a media reference URI after parsing,
    allowing separate access to protocol, directory, and filename parts.

    """

    protocol: str = ""
    """URI protocol (e.g., 'http', 'file') without the '://' suffix.
    Empty string if no protocol is present."""
    directory: str = ""
    """Directory path component of the URI. May be relative or
    absolute path."""
    filename: str = ""
    """Filename component of the URI. Empty string if URI points to a
    directory only."""
    original_uri: str = ""
    """Complete original URI as provided during initialization. Used to
    preserve exact path separator formatting across platforms."""

    def to_uri(self) -> str:
        """Reconstruct the full URI from individual components.

        Returns the original URI if available to preserve exact formatting,
        otherwise reconstructs from components using intelligent separator
        detection based on the directory's existing separator pattern.

        Returns:
            str: Complete URI string. Returns original_uri if available,
                otherwise reconstructed from components.

        """
        # Return original URI if available to preserve exact formatting
        if self.original_uri:
            return self.original_uri

        # Fallback to reconstruction for backward compatibility
        if self.protocol:
            prefix = f"{self.protocol}://"
        else:
            prefix = ""

        # Intelligent separator detection for reconstruction
        if self.filename:
            if self.directory:
                separator = self._detect_separator(self.directory)
                path = f"{self.directory}{separator}{self.filename}"
            else:
                path = self.filename
        else:
            path = self.directory if self.directory else "."

        return prefix + path

    def _detect_separator(self, directory: str) -> str:
        """Detect the appropriate path separator based on directory pattern.

        Analyzes the directory string to determine whether to use forward
        slashes, backslashes, or default to forward slash for mixed patterns.

        Args:
            directory (str): Directory path to analyze.

        Returns:
            str: '\\' for Windows-style paths, '/' for Unix-style or mixed paths.
        """
        if not directory:
            return "/"

        has_forward = "/" in directory
        has_backward = "\\" in directory

        if has_backward and not has_forward:
            # Pure Windows-style path
            return "\\"
        else:
            # Unix-style or mixed - default to forward slash
            return "/"


@dataclass
class SequenceInfo:
    """Container for image sequence detection results.

    Stores information about detected image sequences, including whether
    sequences were found and their patterns with frame padding notation.

    """

    is_sequence: bool = False
    """True if image sequences were detected in the media reference path."""
    sequences: list[str] | None = None
    """List of sequence patterns using # padding notation ('image.####.exr').
    None is converted to empty list during initialization."""

    def __post_init__(self) -> None:
        """Initialize sequences list after dataclass creation.

        Ensures sequences attribute is always a list, converting None
        to an empty list for consistent behavior.

        """
        if self.sequences is None:
            self.sequences = []


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "ColorCorrectionRef",
    "ColorDecision",
    "MediaRef",
    "MediaRefInfo",
    "SequenceInfo",
]

# ==============================================================================
# CLASSES
# ==============================================================================


class ColorCorrectionRef(AscXMLBase):
    """Reference to an existing ColorCorrection by ID.

    Contains a reference to a ColorCorrection instance by storing its ID.
    The reference can be resolved to retrieve the actual ColorCorrection
    object if it exists in the ColorCorrection.members dictionary.

    When writing to formats that support references (like CDL), the reference
    writes as a ColorCorrectionRef element. When writing to formats that don't
    support references (like CCC), behavior depends on halt_on_error setting.

    Example:
        >>> cc = ColorCorrection("shot_001")
        >>> ref = ColorCorrectionRef("shot_001")
        >>> print(ref.cc.id)  # "shot_001"
        >>> print(ref.id)  # "shot_001"

    """

    members: dict[str, list["ColorCorrectionRef"]] = {}
    """Dictionary mapping ColorCorrection IDs to lists of ColorCorrectionRef
    instances that reference them. Multiple references can point to the
    same ID."""

    def __init__(self, id: str) -> None:  # pylint: disable=W0622
        """Initialize ColorCorrectionRef with target ColorCorrection ID.

        Args:
            id (str): ID of the ColorCorrection this reference should point to.
                The ColorCorrection doesn't need to exist at creation time.
        """
        super().__init__()
        self._id: str | None = None
        # Bypass cc id existence checks on first set by calling private
        # method directly.
        self._set_id(id)

        # While all ColorCorrectionReferences should be under a
        # ColorDecision node, we won't strictly enforce that a
        # parent must exist.
        self.parent: ColorDecision | None = None

    # Properties ==============================================================

    @property
    def cc(self) -> ColorCorrection | None:  # pylint: disable=C0103
        """Return the referenced ColorCorrection instance if it exists.

        Returns:
            Optional[ColorCorrection]: The ColorCorrection instance with
                matching ID, or None if reference cannot be resolved.
        """
        return self.resolve_reference()

    @property
    def id(self) -> str | None:  # pylint: disable=C0103
        """Return the ID of the referenced ColorCorrection.

        Returns:
            Optional[str]: ColorCorrection ID this reference points to.
        """
        return self._id

    @id.setter
    def id(self, ref_id: str) -> None:  # pylint: disable=C0103
        """Set the ID of the ColorCorrection to reference.

        Args:
            ref_id (str): ID of the ColorCorrection to reference.

        Raises:
            ValidationError: If ref_id doesn't match existing ColorCorrection
                and halt_on_error is enabled.
        """
        if (
            ref_id not in ColorCorrection.members
            and config.config.halt_on_error
        ):
            raise ValidationError(
                f"Reference id '{ref_id}' does not match any existing "
                f"ColorCorrection id in ColorCorrection.members "
                f"dictionary."
            )

        self._set_id(ref_id)

    # Private Methods =========================================================

    def _set_id(self, new_ref: str) -> None:
        """Change reference ID and update class members dictionary.

        Args:
            new_ref (str): New ColorCorrection ID to reference.
        """
        # The only time it won't be in here is if this is the first time
        # we set it.
        if self.id in ColorCorrectionRef.members:
            ColorCorrectionRef.members[self.id].remove(self)
            # If the remaining list is empty, we'll pop it out
            if not ColorCorrectionRef.members[self.id]:
                ColorCorrectionRef.members.pop(self.id)

        # Check if this id is already registered
        if new_ref in ColorCorrectionRef.members:
            ColorCorrectionRef.members[new_ref].append(self)
        else:
            ColorCorrectionRef.members[new_ref] = [self]

        self._id = new_ref

    # Public Methods ==========================================================

    def build_element(self) -> ElementTree.Element:
        """Build XML ElementTree Element representing this reference.

        Creates a ColorCorrectionRef XML element with ref attribute containing
        the referenced ColorCorrection ID.

        Returns:
            ElementTree.Element: XML element representing this reference.

        """
        cc_ref_xml = ElementTree.Element("ColorCorrectionRef")
        if self.id is not None:
            cc_ref_xml.attrib = {"ref": self.id}

        return cc_ref_xml

    # =========================================================================

    @classmethod
    def reset_members(cls) -> None:
        """Clear the class-level members dictionary.

        Removes all ColorCorrectionRef instances from the members dictionary.
        Useful for testing or when starting with a clean state.

        """
        cls.members = {}

    # =========================================================================

    def resolve_reference(self) -> ColorCorrection | None:
        """Resolve reference to return the actual ColorCorrection instance.

        Attempts to find and return the ColorCorrection instance with matching
        ID from the ColorCorrection.members dictionary.

        Returns:
            Optional[ColorCorrection]: The referenced ColorCorrection if found,
                None if not found (when halt_on_error is False).

        Raises:
            ValidationError: If reference cannot be resolved and halt_on_error
                is enabled.

        """
        if self.id in ColorCorrection.members:
            return ColorCorrection.members[self.id]
        else:
            if config.config.halt_on_error:
                raise ValidationError(
                    f"Cannot resolve ColorCorrectionRef with reference "
                    f"id of '{self.id}' because no ColorCorrection with that id "
                    f"can be found."
                )
            else:
                return None


# ==============================================================================


class ColorDecision(AscDescBase, AscColorSpaceBase, AscXMLBase):  # pylint: disable=R0903
    """Container linking ColorCorrections with media references.

    Associates a ColorCorrection (or ColorCorrectionRef) with an optional
    MediaRef to link color corrections with reference media files. This is
    the primary mechanism for connecting color corrections to specific media
    in CDL workflows.

    The ColorCorrection component is required, while MediaRef is optional.
    ColorDecision can contain either a direct ColorCorrection or a
    ColorCorrectionRef that points to an existing ColorCorrection.

    ColorDecision is the only container that can hold ColorCorrectionRef
    objects, allowing the same ColorCorrection to be linked with multiple
    different media references across different ColorDecisions.

    An example containing a ColorCorrection node::

        <ColorDecision>
            <MediaRef ref="http://www.theasc.com/foasc-logo2.png"/>
            <ColorCorrection id="ascpromo">
                <SOPNode>
                    <Description>get me outta here</Description>
                    <Slope>0.9 1.1 1.0</Slope>
                    <Offset>0.1 -0.01 0.0</Offset>
                    <Power>1.0 0.99 1.0</Power>
                </SOPNode>
            </ColorCorrection>
        </ColorDecision>

    But it can also contain just a reference::

        <ColorDecision>
            <MediaRef ref="best/project/ever/jim.0100.dpx"/>
            <ColorCorrectionRef ref="xf45.x628"/>
        </ColorDecision>

    """

    members: dict[str, list["ColorDecision"]] = {}
    """Dictionary mapping ColorCorrection IDs to lists of ColorDecision
    instances that contain them. Multiple decisions can reference the same
    correction."""

    def __init__(
        self,
        color_correct: Union[ColorCorrection, "ColorCorrectionRef"]
        | None = None,
        media: Optional["MediaRef"] = None,
    ) -> None:
        """Initialize ColorDecision with ColorCorrection and optional MediaRef.

        Args:
            color_correct (Optional[Union[ColorCorrection, ColorCorrectionRef]]):
                ColorCorrection or ColorCorrectionRef to associate with media.
                Can be None initially and set later.
            media (Optional[MediaRef]): Optional media reference to associate
                with the color correction.

        """
        super().__init__()
        self.parent: Any | None = None
        self._cc: ColorCorrection | ColorCorrectionRef | None = None
        self._set_cc(color_correct)
        self._media_ref: MediaRef | None = media

        if self.cc:
            self.set_parentage()

    # Properties ==============================================================

    @property
    def cc(self) -> Union[ColorCorrection, "ColorCorrectionRef"] | None:  # pylint: disable=C0103
        """Return the contained ColorCorrection or ColorCorrectionRef.

        Returns:
            Optional[Union[ColorCorrection, ColorCorrectionRef]]: The color
                correction instance or reference, or None if not set.

        """
        return self._cc

    @cc.setter
    def cc(
        self, new_cc: Union[ColorCorrection, "ColorCorrectionRef"] | None
    ) -> None:  # pylint: disable=C0103
        """Set the ColorCorrection or ColorCorrectionRef and update links.

        Args:
            new_cc (Optional[Union[ColorCorrection, ColorCorrectionRef]]):
                New color correction to associate with this decision.

        """
        self._set_cc(new_cc)

    @property
    def is_ref(self) -> bool:
        """Return True if contains ColorCorrectionRef.

        Returns:
            bool: True if cc is a ColorCorrectionRef, False if ColorCorrection.
        """
        return type(self.cc) is ColorCorrectionRef

    @property
    def media_ref(self) -> Optional["MediaRef"]:
        """Return the associated MediaRef instance if present.

        Returns:
            Optional[MediaRef]: The media reference associated with this
                decision, or None if no media reference is set.

        """
        return self._media_ref

    @media_ref.setter
    def media_ref(self, new_media_ref: Optional["MediaRef"]) -> None:
        """Set the MediaRef and update parent relationship.

        Args:
            new_media_ref (Optional[MediaRef]): New media reference to
                associate with this decision.

        """
        self._media_ref = new_media_ref
        if new_media_ref:
            new_media_ref.parent = self

    # Private Methods =========================================================

    def _set_cc(
        self, new_cc: Union[ColorCorrection, "ColorCorrectionRef"] | None
    ) -> None:
        """Set ColorCorrection and update class members dictionary.

        Args:
            new_cc (Optional[Union[ColorCorrection, ColorCorrectionRef]]):
                New color correction to set and register in members dictionary.

        """
        if self.cc:
            # If we have a cc, we've already been added to the member's list,
            # and need to update membership.
            if self.cc.id is not None and self.cc.id in ColorDecision.members:
                ColorDecision.members[self.cc.id].remove(self)
                # If the remaining list is empty, we'll pop it out
                if not ColorDecision.members[self.cc.id]:
                    ColorDecision.members.pop(self.cc.id)
        if new_cc:
            # It's possible to have new_cc be None, in which case we won't
            # assign this ColorDecision to the member dictionary.
            #
            # Check if this id is already registered
            if new_cc.id is not None:
                if new_cc.id in ColorDecision.members:
                    ColorDecision.members[new_cc.id].append(self)
                else:
                    ColorDecision.members[new_cc.id] = [self]

            new_cc.parent = self

        self._cc = new_cc

    # Public Methods ==========================================================

    def build_element(self, resolve: bool = False) -> ElementTree.Element:  # pylint: disable=W0221
        """Build XML ElementTree Element representing this ColorDecision.

        Creates a ColorDecision XML element containing descriptions, MediaRef
        (if present), and ColorCorrection or ColorCorrectionRef.

        Args:
            resolve (bool): If True and this contains a ColorCorrectionRef,
                resolve the reference and include the actual ColorCorrection
                element instead of the reference element.

        Returns:
            ElementTree.Element: XML element representing this ColorDecision.

        """
        cd_xml = ElementTree.Element("ColorDecision")
        if self.input_desc:
            input_desc = ElementTree.SubElement(cd_xml, "InputDescription")
            input_desc.text = self.input_desc
        if self.viewing_desc:
            viewing_desc = ElementTree.SubElement(cd_xml, "ViewingDescription")
            viewing_desc.text = self.viewing_desc
        for description in self.desc:
            desc = ElementTree.SubElement(cd_xml, "Description")
            desc.text = description
        # Customary for the Media Ref element to go first (if there is one)
        if self.media_ref and self.media_ref.element is not None:
            cd_xml.append(self.media_ref.element)

        # The resolve arg should only be applied to reference color decisions.
        #
        # Our behavior for non-reference CDs is the same as our behavior
        # for non-resolving.
        if not resolve or not self.is_ref:
            if self.cc and self.cc.element is not None:
                cd_xml.append(self.cc.element)
        elif resolve:
            # We're a reference and we need to be resolved
            # Note that this will raise an exception if called when a reference
            # cannot be resolve due to a non-existent ColorCorrection.
            if self.cc and isinstance(self.cc, ColorCorrectionRef):
                resolved_cc = self.cc.cc
                if resolved_cc and resolved_cc.element is not None:
                    cd_xml.append(resolved_cc.element)

        return cd_xml

    # =========================================================================

    def parse_xml_color_correction(
        self, xml_element: ElementTree.Element
    ) -> bool:
        """Parse ColorDecision XML element to find ColorCorrection or reference.

        Searches for either a ColorCorrection or ColorCorrectionRef element
        within the ColorDecision and creates the appropriate object.

        Args:
            xml_element (ElementTree.Element): ColorDecision XML element to
                parse.

        Returns:
            bool: True if ColorCorrection or ColorCorrectionRef was found and
                parsed successfully, False otherwise.

        """
        cc_elem = xml_element.find("ColorCorrection")
        if cc_elem is None:
            # Perhaps we're a ColorCorrectionRef?
            cc_elem = xml_element.find("ColorCorrectionRef")
            if cc_elem is None:
                # No ColorCorrection or CCRef? This is a bad ColorDecision
                return False
            else:
                # Parse the ColorCorrectionRef
                ref_id = cc_elem.attrib["ref"]
                self.cc = ColorCorrectionRef(ref_id)  # pylint: disable=C0103
                self.cc.parent = self
        else:
            from . import parse

            # Parse the ColorCorrection
            self.cc = parse.parse_cc(cc_elem)
            self.cc.parent = self

        return True

    # =========================================================================

    def parse_xml_color_decision(
        self, xml_element: ElementTree.Element
    ) -> None:
        """Parse ColorDecision XML element and populate this instance.

        Parses a ColorDecision XML element to extract descriptions,
        input/viewing descriptions, ColorCorrection or ColorCorrectionRef, and
        MediaRef.

        Args:
            xml_element (ElementTree.Element): ColorDecision XML element to
                parse.

        Raises:
            ParseError: If ColorDecision element is missing required
                ColorCorrection or ColorCorrectionRef child element.

        """
        # Grab our descriptions and add them to the cd.
        self.parse_xml_descs(xml_element)
        # See if we have a viewing description.
        self.parse_xml_viewing_desc(xml_element)
        # See if we have an input description.
        self.parse_xml_input_desc(xml_element)

        # Grab our ColorCorrection
        if not self.parse_xml_color_correction(xml_element):
            raise ParseError(
                "ColorDecisions require at least one ColorCorrection or "
                "ColorCorrectionRef node, but neither was found."
            )

        # Grab our MediaRef (if found)
        self.parse_xml_media_ref(xml_element)

    # =========================================================================

    def parse_xml_media_ref(self, xml_element: ElementTree.Element) -> None:
        """Parse ColorDecision XML element to find and create MediaRef.

        Searches for a MediaRef element within the ColorDecision and creates
        a MediaRef instance if found.

        Args:
            xml_element (ElementTree.Element): ColorDecision XML element to
                parse.

        """
        media_ref_elem = xml_element.find("MediaRef")
        if media_ref_elem is not None:
            ref_uri = media_ref_elem.attrib["ref"]
            self.media_ref = MediaRef(ref_uri=ref_uri)

    # =========================================================================

    @classmethod
    def reset_members(cls) -> None:
        """Clear the class-level members dictionary.

        Removes all ColorDecision instances from the members dictionary.
        Useful for testing or when starting with a clean state.

        """
        cls.members = {}

    # =========================================================================

    def set_parentage(self) -> None:
        """Set parent attribute of child objects to reference this instance.

        Updates the parent attribute of the contained ColorCorrection or
        ColorCorrectionRef and MediaRef (if present) to point to this
        ColorDecision instance.

        """
        if self.cc is not None:
            self.cc.parent = self
        if self.media_ref:  # Media ref objects are optional
            self.media_ref.parent = self


# ==============================================================================


class MediaRef(AscXMLBase):
    """Reference to media files or directories for color correction context.

    Container for media file or directory paths that should be referenced
    in relation to color corrections being performed. Supports both individual
    files and image sequences, with automatic sequence detection and path
    manipulation capabilities.

    URIs can include protocols (e.g., 'http://') but many path manipulation
    methods work best with local file paths. The class provides comprehensive
    path parsing and sequence detection for film and TV workflows.

    Example:
        >>> media = MediaRef("footage/shot_001.0001.exr")
        >>> print(media.is_seq)  # True
        >>> print(media.seq)  # "shot_001.####.exr"
        >>> print(media.exists)

    """

    members: dict[str, list["MediaRef"]] = {}
    """Dictionary mapping reference URIs to lists of MediaRef instances that
    point to them. Multiple MediaRef instances can reference the same URI."""

    def __init__(
        self, ref_uri: str, parent: Optional["ColorDecision"] = None
    ) -> None:
        super().__init__()
        # Parse URI components and store original URI for preservation
        protocol, directory, filename = self._split_uri(ref_uri)
        self._ref_info = MediaRefInfo(
            protocol=protocol,
            directory=directory,
            filename=filename,
            original_uri=ref_uri,
        )
        self.parent: ColorDecision | None = parent

        # Cache for sequence information - computed lazily
        self._sequence_info: SequenceInfo | None = None

        self._change_membership()

    # Properties ==============================================================

    @property
    def directory(self) -> str:
        """Return directory portion of the URI path.

        Returns:
            str: Directory path without protocol or filename. Empty string
                if URI points to a file in the current directory.

        """
        return self._ref_info.directory

    @directory.setter
    def directory(self, value: str) -> None:
        """Set directory portion of the URI path.

        Updates the directory component and resets cached sequence information.
        Also updates class membership dictionary with new URI. Clears
        original_uri since the URI is being modified.

        Args:
            value (str): New directory path to set.

        Raises:
            ValidationError: If value is not a string.

        """
        if type(value) is str:
            old_ref = self.ref
            self._ref_info.directory = value
            # Clear original URI since we're modifying components
            self._ref_info.original_uri = ""
            self._change_membership(old_ref=old_ref)
            self._reset_cached_properties()
        else:
            raise ValidationError(
                f"Directory must be set with a string, not {type(value)}"
            )

    @property
    def exists(self) -> bool:
        """Check if the referenced path exists in the file system.

        Returns:
            bool: True if the file or directory exists, False otherwise.

        """
        return Path(self.path).exists()

    @property
    def filename(self) -> str:
        """Return filename portion of the URI path.

        Returns:
            str: Filename with extension, or empty string if URI points
                to a directory only.

        """
        return self._ref_info.filename

    @filename.setter
    def filename(self, value: str) -> None:
        """Set filename portion of the URI path.

        Updates the filename component and resets cached sequence information.
        Also updates class membership dictionary with new URI. Clears
        original_uri since the URI is being modified.

        Args:
            value (str): New filename to set, including extension.

        Raises:
            ValidationError: If value is not a string.

        """
        if type(value) is str:
            old_ref = self.ref
            self._ref_info.filename = value
            # Clear original URI since we're modifying components
            self._ref_info.original_uri = ""
            self._change_membership(old_ref=old_ref)
            self._reset_cached_properties()
        else:
            raise ValidationError(
                f"Filename must be set with a string, not {type(value)}"
            )

    @property
    def is_abs(self) -> bool:
        """Check if the path is absolute.

        Returns:
            bool: True if path is absolute, False if relative.

        """
        return Path(self.path).is_absolute()

    @property
    def is_dir(self) -> bool:
        """Check if the path points to a directory.

        Returns:
            bool: True if path is a directory, False if file or non-existent.

        """
        return Path(self.path).is_dir()

    @property
    def is_seq(self) -> bool:
        """Check if the path represents an image sequence.

        Detects sequences by analyzing filenames for frame number patterns
        like digits, # padding, or %d formatting. For directories, scans
        contained files for sequence patterns.

        Returns:
            bool: True if path represents an image sequence, False otherwise.

        """
        if self._sequence_info is None:
            self._get_sequences()
        return self._sequence_info.is_sequence if self._sequence_info else False

    @property
    def path(self) -> str:
        """Return complete file path without URI protocol.

        Uses the original URI if available to preserve exact formatting.
        If original_uri has been cleared due to property changes, uses
        intelligent separator detection based on directory pattern.

        Returns:
            str: Complete file path without protocol. Returns directory
                if no filename, or '.' if both directory and filename are
                empty.

        """
        # If we have original URI, extract path portion preserving separators
        if self._ref_info.original_uri:
            uri = self._ref_info.original_uri
            # Remove protocol if present
            if "://" in uri:
                uri = uri.split("://", 1)[1]
            return uri

        # Fallback to reconstruction using intelligent separator detection
        if self._ref_info.filename:
            if self._ref_info.directory:
                separator = self._ref_info._detect_separator(
                    self._ref_info.directory
                )
                return f"{self._ref_info.directory}{separator}{self._ref_info.filename}"
            else:
                return self._ref_info.filename
        else:
            return self._ref_info.directory if self._ref_info.directory else "."

    @property
    def protocol(self) -> str:
        """Return URI protocol without '://' suffix.

        Returns:
            str: Protocol portion of URI (e.g., 'http', 'file', 'ftp').
                Empty string if no protocol is present.

        """
        return self._ref_info.protocol

    @protocol.setter
    def protocol(self, value: str) -> None:
        """Set URI protocol.

        Automatically removes '://' suffix if present. Updates class
        membership dictionary and resets cached properties. Clears original_uri
        since the URI is being modified.

        Args:
            value (str): Protocol to set (e.g., 'http', 'file'). Can include
                '://' suffix which will be automatically removed.

        Raises:
            ValidationError: If value is not a string.

        """
        if type(value) is str:
            # If :// was appended we'll remove it.
            if value.endswith("://"):
                value = value.removesuffix("://")
            old_ref = self.ref
            self._ref_info.protocol = value
            # Clear original URI since we're modifying components
            self._ref_info.original_uri = ""
            self._change_membership(old_ref=old_ref)
            # We probably don't need to reset the cached properties, but we
            # will just to be safe.
            self._reset_cached_properties()
        else:
            raise ValidationError(
                f"Protocol must be set with a string, not {type(value)}"
            )

    @property
    def ref(self) -> str:
        """Return complete URI including protocol, directory, and filename.

        Returns:
            str: Complete URI string. Includes protocol with '://' if present,
                followed by directory and filename components.

        """
        return self._ref_info.to_uri()

    @ref.setter
    def ref(self, uri: str) -> None:
        """Set complete URI and parse into components.

        Parses the URI into protocol, directory, and filename components
        while preserving the original URI format for exact reconstruction.
        Updates class membership dictionary and resets all cached properties.

        Args:
            uri (str): Complete URI string to parse and set.

        Raises:
            ValidationError: If uri is not a string.

        """
        if type(uri) is str:
            old_ref = self.ref
            # Parse components and store original URI
            protocol, directory, filename = self._split_uri(uri)
            self._ref_info = MediaRefInfo(
                protocol=protocol,
                directory=directory,
                filename=filename,
                original_uri=uri,
            )
            self._change_membership(old_ref=old_ref)
            self._reset_cached_properties()
        else:
            raise ValidationError(
                f"URI must be set with a string, not {type(uri)}"
            )

    @property
    def seq(self) -> str | None:
        """Return first detected image sequence with # padding notation.

        Converts frame number patterns to # padding format (e.g.,
        'image.0001.exr' becomes 'image.####.exr').

        Returns:
            Optional[str]: First sequence with # padding, or None if no
                sequences detected.

        """
        if self._sequence_info is None:
            self._get_sequences()
        if not self._sequence_info or not self._sequence_info.is_sequence:
            return None

        return (
            self._sequence_info.sequences[0]
            if self._sequence_info.sequences
            else None
        )

    @property
    def seqs(self) -> list[str]:
        """Return all detected image sequences with # padding notation.

        For directories, returns all unique sequence patterns found.
        For files, returns single-item list if file is part of a sequence.

        Returns:
            List[str]: All sequences with # padding notation. Empty list
                if no sequences detected.

        """
        if self._sequence_info is None:
            self._get_sequences()
        if not self._sequence_info or not self._sequence_info.is_sequence:
            return []

        return (
            self._sequence_info.sequences
            if self._sequence_info.sequences
            else []
        )

    # Private Methods =========================================================

    def _change_membership(self, old_ref: str | None = None) -> None:
        """Update class members dictionary when URI reference changes.

        Removes this instance from the old URI's member list and adds it
        to the new URI's member list. Creates new member list if the new
        URI is not already tracked. Cleans up empty member lists.

        Args:
            old_ref (Optional[str]): Previous URI reference to remove this
                instance from. If None or not found, removal is skipped.

        """
        if old_ref:
            try:
                MediaRef.members[old_ref].remove(self)
            except (KeyError, ValueError):
                # Either the key doesn't exist or we're not in the list.
                # Either way, it doesn't matter to us.
                pass
            else:
                # Now that we're removed, we need to see if the list is empty,
                # and if so, delete the key ref.
                if not MediaRef.members[old_ref]:
                    del MediaRef.members[old_ref]
        try:
            MediaRef.members[self.ref].append(self)
        except KeyError:
            MediaRef.members[self.ref] = [self]

    # =========================================================================

    def _get_sequences(self) -> None:  # pylint: disable=R0912
        """Analyze path to detect image sequences and cache results.

        Examines the path to determine if it represents an image sequence
        by looking for frame number patterns. For directories, scans all
        files to find sequence patterns. Results are cached in _sequence_info.

        Sequence detection patterns:
        - Numeric frame numbers: image.0001.exr -> image.####.exr
        - Percent formatting: image.%04d.exr (preserved as-is)
        - Hash padding: image.####.exr (already in target format)

        """
        re_exp = r"(^[ \w_.-]+[_.])([0-9]+)(\.[a-zA-Z0-9]{3}$)"
        re_exp_percent = r"(^[ \w_.-]+[_.])(%[0-9]+d)(\.[a-zA-Z0-9]{3}$)"
        match = re.compile(re_exp)

        if self.is_dir and not self.exists:
            # It doesn't exist, so we can't tell if it's a sequence
            if config.config.halt_on_error:
                raise ValidationError(
                    f"Cannot determine if non-existent directory {self.path} "
                    f"contains an image sequence."
                )
            else:
                self._sequence_info = SequenceInfo(
                    is_sequence=False, sequences=[]
                )
        elif self.is_dir and self.exists:
            file_list = [
                f.name for f in Path(self.path).iterdir() if f.is_file()
            ]
            files = [f for f in file_list if match.search(f)]
            if not files:
                self._sequence_info = SequenceInfo(
                    is_sequence=False, sequences=[]
                )
            else:
                seqs = []
                for image in files:
                    found = match.search(image)
                    if found is not None:
                        padding = "#" * len(found.group(2))
                        filename = found.group(1) + padding + found.group(3)
                        if filename not in seqs:
                            seqs.append(filename)
                self._sequence_info = SequenceInfo(
                    is_sequence=True, sequences=seqs
                )
        else:
            found = match.search(self.filename)
            if found is not None:
                padding = "#" * len(found.group(2))
                self._sequence_info = SequenceInfo(
                    is_sequence=True,
                    sequences=[found.group(1) + padding + found.group(3)],
                )
            else:
                # We'll finally check for %d style padding
                match = re.compile(re_exp_percent)
                found = match.search(self.filename)
                if found is not None:
                    self._sequence_info = SequenceInfo(
                        is_sequence=True, sequences=[self.filename]
                    )
                else:
                    self._sequence_info = SequenceInfo(
                        is_sequence=False, sequences=[]
                    )

    # =========================================================================

    def _reset_cached_properties(self) -> None:
        """Reset cached sequence information to force re-computation.

        Clears the _sequence_info cache so that sequence detection will
        be performed again on next access to sequence-related properties.

        """
        self._sequence_info = None

    # =========================================================================

    @staticmethod
    def _split_uri(uri: str) -> tuple[str, str, str]:
        """Parse URI into protocol, directory, and filename components.

        Separates a URI into its constituent parts while preserving the
        original path format including relative path indicators. Handles
        both Unix (/) and Windows (\\) path separators.

        Args:
            uri (str): URI string to parse.

        Returns:
            Tuple[str, str, str]: Three-tuple of (protocol, directory,
                filename). Protocol is empty string if not present.
                Directory preserves original format including './' prefixes.

        """
        if "://" in uri:
            protocol = uri.split("://")[0]
            uri = uri.split("://")[1]
        else:
            protocol = ""

        # Handle both Unix and Windows path separators
        # Find the last occurrence of either separator type
        last_forward_slash = uri.rfind("/")
        last_backslash = uri.rfind("\\")

        # Use the separator that appears last in the string
        if last_forward_slash == -1 and last_backslash == -1:
            # No separators found - entire URI is filename
            directory = ""
            ref_file = uri
        elif last_forward_slash > last_backslash:
            # Forward slash is the last separator
            directory = uri[:last_forward_slash]
            ref_file = uri[last_forward_slash + 1 :]
        else:
            # Backslash is the last separator (or they're equal and both exist)
            directory = uri[:last_backslash]
            ref_file = uri[last_backslash + 1 :]

        return protocol, directory, ref_file

    # Public Methods ==========================================================

    def build_element(self) -> ElementTree.Element:
        """Build XML ElementTree Element representing this MediaRef.

        Creates a MediaRef XML element with the 'ref' attribute containing
        the complete URI.

        Returns:
            ElementTree.Element: XML element with MediaRef tag and ref
                attribute.

        """
        media_ref_xml = ElementTree.Element("MediaRef")
        media_ref_xml.attrib = {"ref": self.ref}

        return media_ref_xml

    # =========================================================================

    @classmethod
    def reset_members(cls) -> None:
        """Clear the class-level members dictionary.

        Removes all MediaRef instances from the members dictionary.
        Useful for testing or when starting with a clean state.

        """
        cls.members = {}
