# Ripgrep MCP Server

This is an [MCP](https://modelcontextprotocol.io) server implementation based on [ripgrep](https://github.com/BurntSushi/ripgrep) that allows searching content in a specified folder through the MCP protocol.

## Features

- Provides file content search functionality via MCP protocol
- Uses ripgrep for high-performance text searching
- Supports custom search flags

## File Descriptions

- `rg.py`: Main MCP server program
- `rg.exe`: ripgrep executable (must be in the same directory as `rg.py`)

## Usage

1. Ensure `rg.exe` is in the same directory as `rg.py`
2. Run the server specifying the folder to search:
   ```bash
   python rg.py /path/to/search/folder
   ```
3. Connect to the server through an MCP-compatible client

## Dependencies

- Python 3.x
- ripgrep (rg.exe)

## License

MIT