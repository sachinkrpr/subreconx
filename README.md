# SubReconX

**Advanced Subdomain Reconnaissance Tool**

SubReconX is a powerful Python-based tool designed for authorized penetration testing and bug bounty hunting. It automates the process of subdomain discovery, live host checking, and service scanning.

## Features

-   **Subdomain Discovery**: Utilizes `subfinder` to discover subdomains for a target.
-   **Live Host Check**: Verifies which subdomains are online using Ping and HTTP/HTTPS requests.
-   **Port Scanning**: Performs service version detection (`-sV`) on online subdomains using `nmap`.
-   **Parallel Execution**: Supports multi-threaded scanning for faster results.
-   **Rich Output**: Beautiful console output with progress bars and tables using the `rich` library.
-   **Reporting**: Automatically saves detailed results to a text file.

## Prerequisites

Before using SubReconX, ensure you have the following installed:

1.  **Python 3.x**
2.  **Subfinder** (Required for subdomain discovery)
    ```bash
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    ```
    *Make sure your Go bin directory is in your system PATH.*
3.  **Nmap** (Required for port scanning)
    -   **Windows**: Download and install from [nmap.org](https://nmap.org/download.html).
    -   **Linux**: `sudo apt install nmap`

## Installation

1.  Clone this repository or download the script.
2.  Install the required Python dependencies:

```bash
pip install requests rich
```

## Usage

Run the tool using Python:

```bash
python subreconx.py -d <domain> [options]
```

### Options

-   `-d`, `--domain`: Target domain to scan (Required).
-   `-p`, `--parallel`: Number of parallel Nmap scans (Default: 5).

### Examples

**Basic Scan:**
```bash
python subreconx.py -d example.com
```

**Scan with increased parallelism:**
```bash
python subreconx.py -d example.com -p 10
```

## Output

The tool will display real-time progress in the console. Upon completion, a report file will be generated in the current directory with the naming format: `subreconx_<domain>_<timestamp>.txt`.

## Disclaimer

This tool is for **educational purposes and authorized testing only**. Do not use this tool on any network or system without explicit permission from the owner. The author is not responsible for any misuse or damage caused by this tool.
