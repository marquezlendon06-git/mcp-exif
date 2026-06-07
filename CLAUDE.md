# mcp-exif

Python MCP server that wraps [ExifTool](https://exiftool.org/) and exposes metadata
read/write operations as tools for Claude and other MCP-compatible AI clients.

## Requirements

- Python 3.10+
- [ExifTool](https://exiftool.org/) installed and accessible (see Configuration)
- Perl (if using the ExifTool Perl script rather than the standalone exe)

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure ExifTool path
copy .env.example .env
# Edit .env and set EXIFTOOL_PATH to point at your ExifTool installation
```

## Configuration

Copy `.env.example` to `.env` and set `EXIFTOOL_PATH`:

| Scenario | Value |
|---|---|
| Windows — Perl script at `C:\Tools\exiftool-master\` | `perl C:/Tools/exiftool-master/exiftool` |
| Windows — standalone `exiftool.exe` on PATH | `exiftool` |
| macOS / Linux — system-installed | `exiftool` |

## Running the server

```bash
python server.py
```

The server communicates over stdio (standard MCP transport).

## Available Tools

| Tool | Description |
|---|---|
| `read_metadata` | Read all or specific tags from a file |
| `write_metadata` | Write tag values to a file |
| `strip_metadata` | Remove all metadata from a file |
| `copy_metadata` | Copy metadata from one file to another |
| `exiftool_version` | Return ExifTool version and executable path |

### Tool details

#### `read_metadata(file_path, tags?)`
Returns a dict of tag names → values. Pass `tags` to filter
(e.g. `["EXIF:Make", "GPS:GPSLatitude"]`); omit for everything.

#### `write_metadata(file_path, tags, overwrite_original?)`
`tags` is a dict of tag names → values
(e.g. `{"EXIF:Artist": "Alice", "IPTC:Keywords": ["travel"]}`).
`overwrite_original` defaults to `True` (no `_original` backup file created).

#### `strip_metadata(file_path, overwrite_original?)`
Removes all metadata blocks from the file.

#### `copy_metadata(source_path, dest_path, overwrite_original?)`
Copies all metadata from `source_path` into `dest_path`.

#### `exiftool_version()`
Returns `{"version": "13.59", "executable": "..."}`.

## Wiring into Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "exiftool": {
      "command": "C:\\Users\\Johny English\\Desktop\\Claude\\mcp-exif\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\Johny English\\Desktop\\Claude\\mcp-exif\\server.py"],
      "env": {
        "EXIFTOOL_PATH": "perl C:/Tools/exiftool-master/exiftool"
      }
    }
  }
}
```

## Wiring into Claude Code (CLI)

Run once to register:

```bash
claude mcp add exiftool \
  "C:\Users\Johny English\Desktop\Claude\mcp-exif\.venv\Scripts\python.exe" \
  "C:\Users\Johny English\Desktop\Claude\mcp-exif\server.py"
```

Or add manually to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "exiftool": {
      "command": "C:\\Users\\Johny English\\Desktop\\Claude\\mcp-exif\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\Johny English\\Desktop\\Claude\\mcp-exif\\server.py"]
    }
  }
}
```

## Project structure

```
mcp-exif/
├── CLAUDE.md          # This file
├── server.py          # MCP server — all tools defined here
├── requirements.txt   # pip dependencies
├── pyproject.toml     # Project metadata and packaging
├── .env.example       # Environment variable template
├── .env               # Your local config (git-ignored)
└── .gitignore
```

## ExifTool stay-open mode

`pyexiftool` automatically uses ExifTool's `-stay_open` flag when used as a
context manager, keeping a single ExifTool process alive for the duration of
each tool call. This avoids the ~200 ms Perl startup cost on every request.
For a persistent daemon approach (single process across all calls), replace
the per-call `with ExifToolHelper(...) as et:` blocks in `server.py` with a
module-level `et = ExifToolHelper(...); et.run()` and call `et.terminate()`
on shutdown.
