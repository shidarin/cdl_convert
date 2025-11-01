#!/usr/bin/env python
"""CDL Convert Command Line Interface

This module provides the main entry point for the cdl_convert command-line
tool, with argument parsing, validation, and error reporting.

Public Functions:
    parse_args() -> argparse.Namespace
        Parse command line arguments using modern argparse features with
        improved validation and error messages.

    main() -> None  
        Main script runner, this calls parse_args, determines the input and
        output extensions, calls the correct parser and determines how to
        fulfill the output requested.

    cli_main() -> None
        Entry point wrapper that handles top-level exceptions and provides
        clean exit codes for different error conditions.

Example Usage:
    $ cdl_convert input.ale output.ccc
    $ cdl_convert --input-format ale --output-format ccc input.txt output.xml
    $ cdl_convert --verbose --halt-on-error input.cdl output.cc

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

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from typing import Optional

# cdl_convert imports

from . import config, parse, write
from .collection import ColorCollection
from .exceptions import FormatError
from .utils import sanity_check

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = ['cli_main', 'main', 'parse_args']

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def supports_color() -> bool:
    """Check if terminal supports color output"""
    return (
        hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and
        sys.platform != 'win32'  # Basic Windows check
    )

def colorize(text: str, color: str) -> str:
    """Add color to text if terminal supports it"""
    if supports_color():
        return f"{color}{text}{Colors.END}"
    return text

def print_error(message: str, suggestion: Optional[str] = None) -> None:
    """Print error message with color and optional suggestion"""
    error_text = colorize("ERROR:", Colors.RED + Colors.BOLD)
    print(f"{error_text} {message}", file=sys.stderr)
    
    if suggestion:
        suggestion_text = colorize("SUGGESTION:", Colors.YELLOW + Colors.BOLD)
        print(f"{suggestion_text} {suggestion}", file=sys.stderr)

def print_warning(message: str) -> None:
    """Print warning message with color"""
    warning_text = colorize("WARNING:", Colors.YELLOW + Colors.BOLD)
    print(f"{warning_text} {message}", file=sys.stderr)

def print_info(message: str, verbose: bool = False) -> None:
    """Print info message, only if verbose mode is enabled"""
    if verbose:
        info_text = colorize("INFO:", Colors.BLUE + Colors.BOLD)
        print(f"{info_text} {message}")

def print_success(message: str) -> None:
    """Print success message with color"""
    success_text = colorize("SUCCESS:", Colors.GREEN + Colors.BOLD)
    print(f"{success_text} {message}")

# ==============================================================================
# PUBLIC FUNCTIONS
# ==============================================================================


def parse_args(validate_files=True):
    """Uses argparse to parse command line arguments
    
    Args:
        validate_files (bool): Whether to validate that input files exist.
            Default True.

    """
    # Get supported formats for help text
    input_formats = sorted(parse.INPUT_FORMATS.keys())
    output_formats = sorted(write.OUTPUT_FORMATS.keys())
    
    parser = ArgumentParser(
        description="Convert between ASC Color Decision List (CDL) formats",
        epilog=f"Supported input formats: {', '.join(input_formats)}\n"
               f"Supported output formats: {', '.join(output_formats)}",
        formatter_class=RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the CDL file to be converted"
    )
    
    parser.add_argument(
        "-i", "--input",
        help=f"Specify input format when auto-detection fails. "
             f"Choices: {', '.join(input_formats)}"
    )
    
    parser.add_argument(
        "-o", "--output",
        help=f"Output format(s), comma-separated for multiple outputs. "
             f"Choices: {', '.join(output_formats)}. Default: cc"
    )
    
    parser.add_argument(
        "-d", "--destination",
        type=Path,
        help="Output directory for converted files. Default: ./converted/"
    )
    
    parser.add_argument(
        "--halt",
        action='store_true',
        help="Stop processing on first error instead of using default values. "
             "Useful for strict validation of CDL files. Turn this on if "
             "you want the conversion process to fail and not continue,"
             "rather than relying on default behavior for bad values. Examples"
             " are clipping negative values to 0.0 for Slope, Power and "
             "Saturation, and automatically generating a new id for a "
             "ColorCorrect if no or a bad id is given." 
    )
    
    parser.add_argument(
        "--no-output",
        action='store_true',
        help="Parse files without writing output. Useful with --halt and"
             " --check for validation-only runs."
    )
    
    parser.add_argument(
        "--check",
        action='store_true',
        help="Check for unusual color correction values. Flags "
             "slope/power/saturation outside 0.1-3.0 range and offset outside "
             "-1.0 to 1.0 range."
    )
    
    parser.add_argument(
        "--single",
        action='store_true',
        help="Write each color decision to a separate file instead of "
             "collections. Converts one input file to multiple output files."
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action='store_true',
        help="Enable verbose output with detailed processing information"
    )
    
    parser.add_argument(
        "--debug",
        action='store_true',
        help="Enable debug output with extensive diagnostic information"
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        # Provide more helpful error message for common issues
        if e.code == 2:  # argparse error
            parser.print_help()
        raise

    # Validate input file exists (if validation is enabled)
    if validate_files:
        input_path = Path(args.input_file)
        if not input_path.exists():
            suggestion = "Check the file path for typos or ensure the file exists"
            if hasattr(args, 'verbose') and (args.verbose or getattr(args, 'debug', False)):
                print_error(f"Input file not found: {input_path}", suggestion)
            raise FormatError(f"Input file not found: {input_path}")
        
        if not input_path.is_file():
            suggestion = "Provide a file path, not a directory"
            if hasattr(args, 'verbose') and (args.verbose or getattr(args, 'debug', False)):
                print_error(f"Input path is not a file: {input_path}", suggestion)
            raise FormatError(f"Input path is not a file: {input_path}")

    # Validate and normalize input format (maintain backward compatibility)
    if args.input:
        if args.input.lower() not in parse.INPUT_FORMATS:
            suggestion = f"Use supported formats: {', '.join(input_formats)}"
            if hasattr(args, 'verbose') and (args.verbose or getattr(args, 'debug', False)):
                print_error(f"Unsupported input format: {args.input}", suggestion)
            raise FormatError(f"The input format: {args.input} is not supported")
        args.input = args.input.lower()

    # Validate and normalize output formats
    if args.output:
        output_types = [fmt.strip().lower() for fmt in args.output.split(',')]
        invalid_formats = [fmt for fmt in output_types if fmt not in write.OUTPUT_FORMATS]
        
        if invalid_formats:
            suggestion = f"Use supported formats: {', '.join(output_formats)}. Example: 'cc,ccc'"
            if args.verbose or args.debug:
                print_error(f"Unsupported output format(s): {', '.join(invalid_formats)}", suggestion)
            raise FormatError(f"Unsupported output format(s): {', '.join(invalid_formats)}")
        
        args.output = output_types
    else:
        args.output = ['cc']

    # Set default destination if not provided
    if not args.destination:
        args.destination = Path('./converted/')

    # Apply halt configuration (backward compatibility)
    if args.halt:
        config.config.halt_on_error = True

    return args

# ==============================================================================
# MAIN
# ==============================================================================


def main(validate_files=True):  # pylint: disable=R0912
    """Main conversion function with enhanced error reporting and output
    
    Args:
        validate_files (bool): Whether to validate that input files exist.
            Default True.
    """
    try:
        args = parse_args(validate_files=validate_files)
    except FormatError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Argument parsing failed: {e}")
        sys.exit(1)

    # Set up verbose/debug output
    verbose = args.verbose or args.debug
    debug = args.debug

    if args.no_output:
        print_info("Dry run initiated, no files will be written.", verbose)

    if debug:
        print_info(f"Input file: {args.input_file}", True)
        print_info(f"Input format: {args.input or 'auto-detect'}", True)
        print_info(f"Output formats: {', '.join(args.output)}", True)
        print_info(f"Destination: {args.destination}", True)

    filepath = Path(args.input_file).resolve()
    destination_dir = Path(args.destination).resolve()

    if not destination_dir.exists():
        print_info(f"Destination directory {destination_dir} does not exist.", verbose)
        if not args.no_output:
            print_info("Creating destination directory.", verbose)
            try:
                destination_dir.mkdir(parents=True, exist_ok=True)
                print_success(f"Created destination directory: {destination_dir}")
            except OSError as e:
                print_error(f"Failed to create destination directory: {e}")
                sys.exit(1)
        else:
            print_info("--no-output provided. Skipping directory creation.", verbose)

    if not args.input:
        filetype_in = filepath.suffix.removeprefix('.').lower()
        print_info(f"Auto-detected input format: {filetype_in}", verbose)
    else:
        filetype_in = args.input
        print_info(f"Using specified input format: {filetype_in}", verbose)

    try:
        print_info(f"Parsing {filepath} as {filetype_in} format...", verbose)
        color_decisions = parse.parse_file(filepath, filetype_in)
        print_success(f"Successfully parsed {filepath}")
    except Exception as e:
        print_error(f"Failed to parse {filepath}: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    def write_single_file(cdl, ext):
        """Writes a single color correction file with error handling"""
        try:
            cdl.determine_dest(ext, destination_dir)
            print_info(f"Writing CDL {cdl.id} to {cdl.file_out}", verbose)
            if not args.no_output:
                write.OUTPUT_FORMATS[ext](cdl)
                print_success(f"Wrote {cdl.id} as {ext} format")
            else:
                print_info(f"Dry run: would write {cdl.id} to {cdl.file_out}", verbose)
        except Exception as e:
            print_error(f"Failed to write CDL {cdl.id}: {e}")
            if debug:
                import traceback
                traceback.print_exc()
            if args.halt:
                sys.exit(1)

    def write_collection_file(col, ext):
        """Writes a collection file with enhanced error handling"""
        try:
            col.type = ext
            col.determine_dest(destination_dir)
            print_info(f"Writing collection to {col.file_out}", verbose)
            if not args.no_output:
                write.OUTPUT_FORMATS[ext](col)
                print_success(f"Wrote collection as {ext} format")
            else:
                print_info(f"Dry run: would write collection to {col.file_out}", verbose)
        except Exception as e:
            print_error(f"Failed to write collection: {e}")
            if debug:
                import traceback
                traceback.print_exc()
            if args.halt:
                sys.exit(1)

    if color_decisions:
        # Sanity Check
        if args.check:
            print_info("Performing sanity checks on color correction values...", verbose)
            try:
                if config.config.is_collection_format(filetype_in):
                    for color_correct in color_decisions.color_corrections:
                        sanity_check(color_correct)
                    for decision in color_decisions.color_decisions:
                        if not decision.is_ref:
                            sanity_check(decision.cc)
                else:
                    sanity_check(color_decisions)
                print_success("Sanity checks completed")
            except Exception as e:
                print_warning(f"Sanity check found issues: {e}")
                if args.halt:
                    sys.exit(1)

        # Writing
        for ext in args.output:
            if config.config.is_single_format(ext) or args.single:
                if config.config.is_collection_format(filetype_in):
                    for color_correct in color_decisions.color_corrections:
                        write_single_file(color_correct, ext)
                    for decision in color_decisions.color_decisions:
                        if not decision.is_ref:
                            write_single_file(decision.cc, ext)
                else:
                    write_single_file(color_decisions, ext)
            else:
                if config.config.is_collection_format(filetype_in):
                    # If we read a collection type, color_decisions is
                    # already a ColorCollection.
                    write_collection_file(color_decisions, ext)
                else:
                    # If we read a single, non-collection file, we need to
                    # create a collection for exporting.
                    #
                    # Since we only read a single file, we can safely use that
                    # filepath as the input_file.
                    #
                    # If we read a group of files, we would want to default to
                    # the generic collection naming.
                    collection = ColorCollection(input_file=filepath)
                    collection.append_child(color_decisions)
                    write_collection_file(collection, ext)
    else:
        print_error("No color decisions found in input file")
        sys.exit(1)


def cli_main():
    """CLI entry point with backward-compatible error handling"""
    try:
        main()
    except KeyboardInterrupt:
        print_error("Operation cancelled by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except FormatError as e:
        # Maintain backward compatibility - just print error and exit
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # For unexpected errors, provide helpful information
        print_error(f"Unexpected error: {e}")
        print_error("This may be a bug. Please report it with the input file if possible.")
        sys.exit(1)
