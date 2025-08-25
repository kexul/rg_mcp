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

def search_in_folder(pattern, folder):
    """
    Search for a pattern in a folder using ripgrep
    """
    import time
    
    # Find rg executable
    rg_path = find_rg()
    if rg_path is None:
        return "Error: ripgrep (rg) not found. Place rg.exe in the current directory."
    
    try:
        # Build the rg command
        cmd = [rg_path, "--heading", "-n", pattern, folder]
        
        # Maximum matches per file for this pattern
        cmd.extend(["--max-count", str(5)])
        
        # Add context lines to see the full definition
        cmd.extend(["-A", "5", "-B", "1"])
        
        # Record start time
        start_time = time.time()
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        # Record end time and calculate duration
        end_time = time.time()
        search_duration = end_time - start_time
        
        # If max_lines is specified and ripgrep doesn't support --max-count for total lines,
        # we can also limit the output lines here as a fallback
        output = result.stdout
        if output is None:
            output = "No matches found"
        
        lines = output.split('\n')
        max_lines = 300
        if len(lines) > max_lines:
            output = '\n'.join(lines[:max_lines]) + f"\n... (output truncated to {max_lines} lines)"
        
        # Prepend search time to the output
        time_info = f"Search completed in {search_duration:.3f} seconds\n{'='*50}\n"
        return time_info + output
        
    except FileNotFoundError:
        return "Error: ripgrep (rg) not found in PATH"
    except Exception as e:
        return f"Error: {str(e)}"

def search_python_definitions(name, folder):
    """
    Search for Python function or class definitions using ripgrep
    """
    import time
    
    # Find rg executable
    rg_path = find_rg()
    if rg_path is None:
        return "Error: ripgrep (rg) not found. Place rg.exe in the current directory."
    
    # Combine all Python definition patterns into one regex with OR operator
    combined_pattern = rf"(^def\s+{name}\s*\(|^class\s+{name}\s*[\(:]|^\s+def\s+{name}\s*\(|^async\s+def\s+{name}\s*\(|^\s+async\s+def\s+{name}\s*\()"
    
    try:
        start_time = time.time()
        
        # Build the rg command - single execution
        cmd = [rg_path, "--heading", "-n", "-e", combined_pattern]
        
        # Only search Python files
        cmd.extend(["-t", "py"])
        
        # Add default exclusions
        cmd.extend([
            "--glob", "!**/__pycache__/**",
            "--glob", "!**/.venv/**",
            "--glob", "!**/venv/**",
            "--glob", "!**/site-packages/**",
            "--glob", "!**/.pytest_cache/**"
        ])
        
        cmd.extend([folder])
        
        # Maximum matches per file
        cmd.extend(["--max-count", str(5)])
        
        # Add context lines to see the full definition
        cmd.extend(["-A", "5", "-B", "1"])
        
        # Execute the command once
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        end_time = time.time()
        search_duration = end_time - start_time
        
        if not result.stdout.strip():
            return f"Search completed in {search_duration:.3f} seconds\n{'='*50}\nNo Python definitions found for '{name}'"
        
        # Parse results and categorize by type
        output = result.stdout
        lines = output.split('\n')
        
        # Limit output lines
        max_lines = 400
        if len(lines) > max_lines:
            output = '\n'.join(lines[:max_lines]) + f"\n... (output truncated to {max_lines} lines)"
        
        # Enhanced header with statistics
        time_info = f"Python definition search completed in {search_duration:.3f} seconds\n"
        time_info += f"{'='*50}\n"
        
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
        return search_in_folder(pattern, args.folder)

    @mcp.tool(name="search_definitions", description="Search for Python function or class definitions using ripgrep")
    def search_definitions(name: str):
        """
        Search for Python function or class definitions in the specified folder
        
        Args:
            name: The name of the function or class to search for
        """
        return search_python_definitions(name, args.folder)    # Start the server

    mcp.run()


if __name__ == "__main__":
    main()