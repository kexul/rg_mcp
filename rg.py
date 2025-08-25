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

def search_with_ripgrep(pattern, folder):
    """
    Unified search function using ripgrep with different search modes
    
    Args:
        pattern: The search pattern (for general search) or None (for python_def search)
        folder: The folder to search in
        search_type: "general" for general pattern search, "python_def" for Python definitions
        name: The function/class name to search for (used when search_type="python_def")
    """
    import time
    
    # Find rg executable
    rg_path = find_rg()
    if rg_path is None:
        return "Error: ripgrep (rg) not found. Place rg.exe in the current directory."
    
    try:
        start_time = time.time()
        
        # Build base command
        cmd = [rg_path, "--heading", "-n"]
        max_lines = 400
        
        # General search mode
        if not pattern:
            return "Error: pattern parameter is required for general search"
        
        cmd.append(pattern)
        search_desc = "Search"
        no_match_msg = "No matches found"
        
        # Add folder and common options
        cmd.append(folder)
        cmd.extend(["--max-count", "5"])
        cmd.extend(["-A", "5", "-B", "1"])
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        end_time = time.time()
        search_duration = end_time - start_time
        
        # Handle output
        output = result.stdout
        if not output or not output.strip():
            output = no_match_msg
        else:
            lines = output.split('\n')
            if len(lines) > max_lines:
                output = '\n'.join(lines[:max_lines]) + f"\n... (output truncated to {max_lines} lines)"
        
        # Format result with timing info
        time_info = f"{search_desc} completed in {search_duration:.3f} seconds\n{'='*50}\n"
        return time_info + output
        
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
    mcp = FastMCP(name="rg_mcp", instructions="MCP server using ripgrep to search content in a folder")
    
    # Add search tool
    @mcp.tool(name="search_files", description="Search for content in files using ripgrep")
    def search_files(pattern: str):
        """
        Search for a pattern in the specified folder using ripgrep
        
        Args:
            pattern: The search pattern
            flags: Additional rg flags (optional)
            max_lines: Maximum number of output lines to return (optional)
        """
        return search_with_ripgrep(pattern, args.folder)

    mcp.run()


if __name__ == "__main__":
    main()