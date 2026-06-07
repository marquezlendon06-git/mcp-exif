# mcp-exif

A Python [MCP](https://modelcontextprotocol.io/) server that wraps [ExifTool](https://exiftool.org/)
and exposes file metadata read/write operations as tools for Claude and other
MCP-compatible AI clients.

## Requirements

- Python 3.10+
- [ExifTool](https://exiftool.org/) installed and accessible — either:
  - the standalone `exiftool(-k).exe` (renamed to `exiftool.exe` and placed on PATH), or
  - the Perl script + Perl on PATH (e.g. [Strawberry Perl](https://strawberryperl.com/))

## Setup

### Windows — automated

Run `install.bat` from the project root. It checks your Python/ExifTool setup,
creates a virtual environment in `.venv`, installs dependencies, and generates
a `.env` file from `.env.example`:

```bat
install.bat
```

### Manual (Windows / macOS / Linux)

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure ExifTool path
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux
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

## Available tools

| Tool | Description |
|---|---|
| `read_metadata` | Read all or specific tags from a file |
| `write_metadata` | Write tag values to a file |
| `strip_metadata` | Remove all metadata from a file |
| `copy_metadata` | Copy metadata from one file to another |
| `exiftool_version` | Return ExifTool version and executable path |

## Wiring into Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "exiftool": {
      "command": "C:\\path\\to\\mcp-exif\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\mcp-exif\\server.py"],
      "env": {
        "EXIFTOOL_PATH": "perl C:/Tools/exiftool-master/exiftool"
      }
    }
  }
}
```

## Wiring into Claude Code (CLI)

```bash
claude mcp add exiftool \
  "C:\path\to\mcp-exif\.venv\Scripts\python.exe" \
  "C:\path\to\mcp-exif\server.py"
```

See [CLAUDE.md](CLAUDE.md) for full documentation, including project structure
and notes on ExifTool's stay-open mode.
