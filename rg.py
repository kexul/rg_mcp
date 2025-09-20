#!/usr/bin/env python3
import time
import subprocess
import os
from fastmcp import FastMCP

FOLDER = None


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
    # Initialize FastMCP server
    mcp = FastMCP(name="rg_mcp", instructions="MCP server using ripgrep to search content in a folder. Before searching, you must first set an absolute path using set_search_path tool.")
    
    # Add tool to set search folder
    @mcp.tool(name="set_search_path", description="Set the folder path for searching files (must be an absolute path)")
    def set_search_path(path: str):
        """
        Set the folder path where files will be searched (must be an absolute path)
        
        Args:
            path: The absolute folder path to set for searching
        """
        global FOLDER
        
        # Check if the path is absolute
        if not os.path.isabs(path):
            return f"Error: Path must be absolute. Received relative path: '{path}'"
        
        # Normalize the path
        normalized_path = os.path.normpath(path)
        
        # Check if the path exists and is a directory
        if not os.path.exists(normalized_path):
            return f"Error: Path '{normalized_path}' does not exist"
        
        if not os.path.isdir(normalized_path):
            return f"Error: Path '{normalized_path}' is not a directory"
        
        FOLDER = normalized_path
        return f"Search path set to: {normalized_path}"
    
    # Add search tool
    @mcp.tool(name="search_files", description="Search for content in files using ripgrep")
    def search_files(pattern: str):
        """
        Search for a pattern in the specified folder using ripgrep
        
        Args:
            pattern: The search pattern
        """
        global FOLDER
        if FOLDER is None:
            return 'Search folder not set, please use set_search_path tool to set the search folder first!'
        return search_with_ripgrep(pattern, FOLDER)
    

    mcp.run()


if __name__ == "__main__":
    main()