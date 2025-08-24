#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
from fastmcp import FastMCP


def find_rg():
    # Check if rg.exe exists in the current file's directory
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir_rg = os.path.join(current_file_dir, "rg.exe")
    if os.path.isfile(current_dir_rg):
        return current_dir_rg

def search_in_folder(pattern, folder, flags=""):
    """
    Search for a pattern in a folder using ripgrep
    """
    # Find rg executable
    rg_path = find_rg()
    if rg_path is None:
        return "Error: ripgrep (rg) not found. Place rg.exe in the current directory."
    
    try:
        # Build the rg command
        cmd = [rg_path, "--heading", "-n", pattern, folder]
        if flags:
            cmd.extend(flags.split())
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=folder)
        
        return result.stdout
    except FileNotFoundError:
        return "Error: ripgrep (rg) not found in PATH"
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP server using ripgrep to search content in a folder")
    parser.add_argument("folder", help="Folder to search in")
    args = parser.parse_args()
    
    # Validate folder exists
    if not os.path.exists(args.folder):
        print(f"Error: Folder '{args.folder}' does not exist")
        sys.exit(1)
    
    if not os.path.isdir(args.folder):
        print(f"Error: '{args.folder}' is not a directory")
        sys.exit(1)
    
    # Initialize FastMCP server
    mcp = FastMCP("rg-mcp-server")
    
    # Add search tool
    @mcp.tool(name="search_files", description="Search for content in files using ripgrep")
    def search_files(pattern: str, flags: str = ""):
        """
        Search for a pattern in the specified folder using ripgrep
        
        Args:
            pattern: The search pattern
            flags: Additional rg flags (optional)
        """
        return search_in_folder(pattern, args.folder, flags)
    
    
    # Start the server
    mcp.run()


if __name__ == "__main__":
    main()