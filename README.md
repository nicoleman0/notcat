# notcat

notcat is a Python-based network utility tool similar to netcat, providing functionality for creating network connections, transferring files, and executing commands. Useful for when there is only Python installed on a system you are testing.

## Installation

1. Install the required dependency:

```bash
pip install pyfiglet
```

If you want to use this script on a system that does not allow for external modules to be installed, simply delete the pyfiglet code in the script, and it will run the same.

## Usage

Basic syntax:

```bash
python3 notcat.py -t target_host -p port [options]
```

### Options

- `-l, --listen`: Listen for incoming connections
- `-e, --execute=file`: Execute a file upon receiving connection
- `-c, --command`: Initialize a command shell
- `-u, --upload=destination`: Upload a file to the specified destination
- `-h, --help`: Show help message

### Examples

Listen for connections and start a command shell:

```bash
python3 notcat.py -t 192.168.0.1 -p 5555 -l -c
```

Execute a command upon connection:

```bash
python3 notcat.py -t 192.168.0.1 -p 5555 -l -e="cat /etc/passwd"
```

## Security Notice

This tool is for educational and testing purposes only. Always ensure you have proper authorization before using on any network or system. Do NOT use this tool against any government or military resources/institutions.
