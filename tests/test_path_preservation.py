#!/usr/bin/env python
"""Tests for URI path separator preservation in MediaRef functionality.

This module tests that MediaRef correctly preserves path separators exactly
as provided in source URIs, ensuring cross-platform CDL compatibility.
"""

import unittest
from cdl_convert.decision import MediaRef, MediaRefInfo


class TestPathSeparatorPreservation(unittest.TestCase):
    """Test that MediaRef preserves original path separators."""

    def test_windows_path_preservation(self):
        """Test Windows backslash separators are preserved."""
        uri = "C:\\Windows\\File\\test.txt"
        media_ref = MediaRef(uri)
        
        self.assertEqual(media_ref.ref, uri)
        self.assertEqual(media_ref.path, uri)
        self.assertEqual(media_ref.directory, "C:\\Windows\\File")
        self.assertEqual(media_ref.filename, "test.txt")
        
    def test_unix_path_preservation(self):
        """Test Unix forward slash separators are preserved."""
        uri = "/usr/local/bin/test.txt"
        media_ref = MediaRef(uri)
        
        self.assertEqual(media_ref.ref, uri)
        self.assertEqual(media_ref.path, uri)
        self.assertEqual(media_ref.directory, "/usr/local/bin")
        self.assertEqual(media_ref.filename, "test.txt")
        
    def test_mixed_separators_preservation(self):
        """Test mixed separator patterns are preserved exactly."""
        uri = "C:\\Windows/Mixed\\Path/file.txt"
        media_ref = MediaRef(uri)
        
        self.assertEqual(media_ref.ref, uri)
        self.assertEqual(media_ref.path, uri)
        # Should split on last separator (forward slash)
        self.assertEqual(media_ref.directory, "C:\\Windows/Mixed\\Path")
        self.assertEqual(media_ref.filename, "file.txt")


class TestProtocolPreservation(unittest.TestCase):
    """Test protocol handling with path preservation."""
    
    def test_protocol_with_windows_paths(self):
        """Test protocols preserve Windows-style paths."""
        uri = "file://C:\\Windows\\test.txt"
        media_ref = MediaRef(uri)
        
        self.assertEqual(media_ref.ref, uri)
        self.assertEqual(media_ref.protocol, "file")
        self.assertEqual(media_ref.path, "C:\\Windows\\test.txt")
        
    def test_protocol_with_mixed_paths(self):
        """Test protocols preserve mixed separator paths."""
        uri = "http://example.com\\windows/mixed\\path.jpg"
        media_ref = MediaRef(uri)
        
        self.assertEqual(media_ref.ref, uri)
        self.assertEqual(media_ref.protocol, "http")
        self.assertEqual(media_ref.path, "example.com\\windows/mixed\\path.jpg")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special path formats."""
    
    def test_unc_path_preservation(self):
        """Test UNC network paths are preserved."""
        uri = "\\\\server\\share\\file.dpx"
        media_ref = MediaRef(uri)
        
        self.assertEqual(media_ref.ref, uri)
        self.assertEqual(media_ref.directory, "\\\\server\\share")
        self.assertEqual(media_ref.filename, "file.dpx")
        
    def test_relative_path_preservation(self):
        """Test relative path indicators are preserved."""
        test_cases = [
            "../parent/file.txt",
            ".\\current\\file.txt", 
            "..\\parent/mixed\\file.txt"
        ]
        
        for uri in test_cases:
            with self.subTest(uri=uri):
                media_ref = MediaRef(uri)
                self.assertEqual(media_ref.ref, uri)
                self.assertEqual(media_ref.path, uri)
                
    def test_filename_only(self):
        """Test filename-only URIs work correctly."""
        uri = "filename.txt"
        media_ref = MediaRef(uri)
        
        self.assertEqual(media_ref.ref, uri)
        self.assertEqual(media_ref.directory, "")
        self.assertEqual(media_ref.filename, "filename.txt")


class TestMediaRefInfoPreservation(unittest.TestCase):
    """Test MediaRefInfo dataclass preservation behavior."""
    
    def test_original_uri_preservation(self):
        """Test MediaRefInfo returns original URI when available."""
        original_uri = "C:\\Windows\\File\\test.txt"
        info = MediaRefInfo(
            protocol="",
            directory="C:\\Windows\\File",
            filename="test.txt",
            original_uri=original_uri
        )
        
        self.assertEqual(info.to_uri(), original_uri)
        
    def test_fallback_windows_separator_detection(self):
        """Test MediaRefInfo fallback detects Windows separators."""
        info = MediaRefInfo(
            protocol="",
            directory="C:\\Windows\\File",
            filename="test.txt",
            original_uri=""  # Empty to trigger fallback
        )
        
        # Should detect backslashes and use backslash for joining
        self.assertEqual(info.to_uri(), "C:\\Windows\\File\\test.txt")
        
    def test_fallback_unix_separator_detection(self):
        """Test MediaRefInfo fallback detects Unix separators."""
        info = MediaRefInfo(
            protocol="",
            directory="/usr/local/bin",
            filename="test.txt",
            original_uri=""  # Empty to trigger fallback
        )
        
        # Should detect forward slashes and use forward slash for joining
        self.assertEqual(info.to_uri(), "/usr/local/bin/test.txt")
        
    def test_fallback_mixed_separator_defaults_to_forward(self):
        """Test MediaRefInfo fallback defaults to forward slash for mixed separators."""
        info = MediaRefInfo(
            protocol="",
            directory="C:\\Windows/Mixed\\Path",
            filename="test.txt",
            original_uri=""  # Empty to trigger fallback
        )
        
        # Should default to forward slash for mixed patterns
        self.assertEqual(info.to_uri(), "C:\\Windows/Mixed\\Path/test.txt")


class TestBackwardCompatibility(unittest.TestCase):
    """Test that existing MediaRef functionality still works."""
    
    def test_property_setters_use_intelligent_separator_detection(self):
        """Test that modifying properties uses intelligent separator detection."""
        media_ref = MediaRef("C:\\Windows\\test.txt")
        
        # Modify directory to another Windows path - should use backslash
        media_ref.directory = "D:\\NewPath"
        
        self.assertEqual(media_ref.directory, "D:\\NewPath")
        self.assertEqual(media_ref.filename, "test.txt")
        # Should detect backslashes and use backslash for joining
        self.assertEqual(media_ref.ref, "D:\\NewPath\\test.txt")
        
    def test_property_setters_unix_path_detection(self):
        """Test property setters detect Unix paths correctly."""
        media_ref = MediaRef("/old/path/file.txt")
        
        # Modify directory to Unix path - should use forward slash
        media_ref.directory = "/usr/local/bin"
        
        self.assertEqual(media_ref.directory, "/usr/local/bin")
        self.assertEqual(media_ref.filename, "file.txt")
        # Should detect forward slashes and use forward slash for joining
        self.assertEqual(media_ref.ref, "/usr/local/bin/file.txt")
        
    def test_ref_setter_preserves_new_format(self):
        """Test setting new ref preserves the new format."""
        media_ref = MediaRef("/old/path/file.txt")
        
        new_uri = "C:\\Windows\\new\\file.txt"
        media_ref.ref = new_uri
        
        self.assertEqual(media_ref.ref, new_uri)
        self.assertEqual(media_ref.path, new_uri)
        
    def test_path_property_uses_intelligent_separator_detection(self):
        """Test that path property also uses intelligent separator detection."""
        media_ref = MediaRef("C:\\Windows\\test.txt")
        
        # Modify filename - should clear original_uri and use intelligent detection
        media_ref.filename = "newfile.txt"
        
        # Both ref and path should use backslash since directory has backslashes
        self.assertEqual(media_ref.path, "C:\\Windows\\newfile.txt")
        self.assertEqual(media_ref.ref, "C:\\Windows\\newfile.txt")


if __name__ == '__main__':
    unittest.main()