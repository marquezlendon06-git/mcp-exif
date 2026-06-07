#!/usr/bin/env python3
"""ExifTool MCP Server — exposes ExifTool metadata operations as MCP tools."""

import os
from pathlib import Path
from typing import Any

import exiftool
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

EXIFTOOL_PATH = os.environ.get("EXIFTOOL_PATH", "exiftool")

mcp = FastMCP(
    "mcp-exif",
    instructions="Read and write file metadata using ExifTool (supports 300+ file formats).",
)


def _resolve(file_path: str) -> Path:
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    return path


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def read_metadata(file_path: str, tags: list[str] | None = None) -> dict[str, Any]:
    """Read metadata from a file.

    Args:
        file_path: Absolute or relative path to the file.
        tags: Optional list of specific tag names to extract (e.g. ["EXIF:Make",
              "EXIF:Model", "GPS:GPSLatitude"]). Returns all tags when omitted.

    Returns:
        Dictionary of tag names to values.
    """
    path = _resolve(file_path)
    with exiftool.ExifToolHelper(executable=EXIFTOOL_PATH) as et:
        if tags:
            results = et.get_tags(str(path), tags)
        else:
            results = et.get_metadata(str(path))
    return results[0] if results else {}


@mcp.tool()
def write_metadata(file_path: str, tags: dict[str, Any], overwrite_original: bool = True) -> str:
    """Write metadata tags to a file.

    Args:
        file_path: Absolute or relative path to the file.
        tags: Dictionary of tag names to values to write
              (e.g. {"EXIF:Artist": "John", "IPTC:Keywords": ["travel", "landscape"]}).
        overwrite_original: When True, overwrites the file in-place without
                            creating a backup (_original file). Defaults to True.

    Returns:
        Confirmation message.
    """
    path = _resolve(file_path)
    params = ["-overwrite_original"] if overwrite_original else []
    with exiftool.ExifToolHelper(executable=EXIFTOOL_PATH) as et:
        et.set_tags(str(path), tags, params=params)
    return f"Wrote {len(tags)} tag(s) to {path.name}"


@mcp.tool()
def strip_metadata(file_path: str, overwrite_original: bool = True) -> str:
    """Remove all metadata from a file.

    Args:
        file_path: Absolute or relative path to the file.
        overwrite_original: When True, overwrites in-place without a backup.

    Returns:
        Confirmation message.
    """
    path = _resolve(file_path)
    args = ["-all=", str(path)]
    if overwrite_original:
        args.insert(0, "-overwrite_original")
    with exiftool.ExifToolHelper(executable=EXIFTOOL_PATH) as et:
        et.execute(*args)
    return f"Stripped all metadata from {path.name}"


@mcp.tool()
def copy_metadata(source_path: str, dest_path: str, overwrite_original: bool = True) -> str:
    """Copy all metadata from a source file to a destination file.

    Args:
        source_path: File to copy metadata from.
        dest_path: File to copy metadata to.
        overwrite_original: When True, overwrites dest in-place without a backup.

    Returns:
        Confirmation message.
    """
    src = _resolve(source_path)
    dst = _resolve(dest_path)
    args = [f"-TagsFromFile", str(src), str(dst)]
    if overwrite_original:
        args.insert(0, "-overwrite_original")
    with exiftool.ExifToolHelper(executable=EXIFTOOL_PATH) as et:
        et.execute(*args)
    return f"Copied metadata from {src.name} to {dst.name}"


@mcp.tool()
def exiftool_version() -> dict[str, str]:
    """Return the ExifTool version and executable path being used.

    Returns:
        Dictionary with 'version' and 'executable' keys.
    """
    with exiftool.ExifToolHelper(executable=EXIFTOOL_PATH) as et:
        version = et.version
    return {"version": version, "executable": EXIFTOOL_PATH}


if __name__ == "__main__":
    mcp.run()
