"""
Script to find and kill a process using a specific port.
"""

import os
import sys
import subprocess
import signal

def find_process_by_port(port):
    """Find the process ID using the specified port."""
    try:
        # For macOS and Linux
        if os.name == 'posix':
            # Use lsof to find the process
            result = subprocess.run(
                ["lsof", "-i", f":{port}"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header line
                    # Extract PID from the second column
                    pid = lines[1].split()[1]
                    return int(pid)
        
        # For Windows
        elif os.name == 'nt':
            # Use netstat to find the process
            result = subprocess.run(
                ["netstat", "-ano", "|", "findstr", f":{port}"],
                capture_output=True,
                text=True,
                shell=True,
                check=False
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                if lines:
                    # Extract PID from the last column
                    pid = lines[0].strip().split()[-1]
                    return int(pid)
    
    except Exception as e:
        print(f"Error finding process: {str(e)}")
    
    return None

def kill_process(pid):
    """Kill the process with the specified PID."""
    try:
        # For macOS and Linux
        if os.name == 'posix':
            os.kill(pid, signal.SIGTERM)
            print(f"Process with PID {pid} terminated.")
            return True
        
        # For Windows
        elif os.name == 'nt':
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
            print(f"Process with PID {pid} terminated.")
            return True
    
    except Exception as e:
        print(f"Error killing process: {str(e)}")
    
    return False

def main():
    """Main function to find and kill a process using a specific port."""
    if len(sys.argv) < 2:
        port = 8002  # Default port
    else:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    print(f"Finding process using port {port}...")
    pid = find_process_by_port(port)
    
    if pid:
        print(f"Found process with PID {pid} using port {port}.")
        if kill_process(pid):
            print(f"Successfully killed process using port {port}.")
        else:
            print(f"Failed to kill process using port {port}.")
    else:
        print(f"No process found using port {port}.")

if __name__ == "__main__":
    main()
