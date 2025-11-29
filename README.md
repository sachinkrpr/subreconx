# SubReconX

```
   ███████╗██╗   ██╗██████╗ ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗██╗  ██╗
   ██╔════╝██║   ██║██╔══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║╚██╗██╔╝
   ███████╗██║   ██║██████╔╝██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║ ╚███╔╝
   ╚════██║██║   ██║██╔══██╗██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║ ██╔██╗
   ███████║╚██████╔╝██████╔╝██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║██╔╝ ██╗
   ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝
```

**Advanced Subdomain Reconnaissance Tool v1.0**

A powerful and efficient subdomain enumeration and reconnaissance tool designed for authorized penetration testing and security research. SubReconX automates the process of discovering subdomains, checking their availability, and performing service version detection.

## Features

- **Subdomain Discovery**: Leverages `subfinder` for comprehensive subdomain enumeration
- **Live Status Checking**: Multi-threaded ping checks to identify online/offline subdomains
- **Service Detection**: Parallel nmap scanning with version detection (`-sV`)
- **Real-time Results**: Live display of scan progress and results as they complete
- **Beautiful UI**: Rich terminal interface with colored output, tables, and progress bars
- **Automated Reporting**: Saves detailed results to timestamped text files
- **High Performance**: Utilizes all CPU cores for maximum speed

## Prerequisites

### Required Tools

1. **Python 3.x** with pip
2. **subfinder** - Subdomain discovery tool
3. **nmap** - Network scanning tool

### Python Dependencies

- `rich` - Terminal formatting and display

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sachinkrpr/subreconx.git
cd subreconx
```

### 2. Install Python Dependencies

```bash
pip install rich
```

### 3. Install Required Tools

**Install subfinder:**
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

**Install nmap:**
```bash
# Ubuntu/Debian
sudo apt-get install nmap

# macOS
brew install nmap

# Fedora/RHEL
sudo dnf install nmap
```

### 4. Make Script Executable

```bash
chmod +x subreconx.py
```

## Usage

### Basic Syntax

```bash
python subreconx.py -d <domain> [options]
```

### Arguments

| Argument | Description | Required | Default |
|----------|-------------|----------|---------|
| `-d, --domain` | Target domain to scan | Yes | - |
| `-p, --parallel` | Number of parallel nmap scans | No | 5 |

### Examples

**Basic scan:**
```bash
python subreconx.py -d example.com
```

**Scan with 10 parallel nmap processes:**
```bash
python subreconx.py -d example.com -p 10
```

**Scan without protocol prefix:**
```bash
python subreconx.py -d https://example.com
# Automatically cleaned to: example.com
```

## How It Works

SubReconX operates in 4 distinct phases:

### Phase 1: Subdomain Discovery
Uses `subfinder` to enumerate all discoverable subdomains for the target domain.

### Phase 2: Online Status Check
Performs multi-threaded ping checks on all discovered subdomains to determine which are reachable.

### Phase 3: Service Scanning
Runs parallel `nmap -sV` scans on online subdomains to detect:
- Open ports
- Running services
- Service versions

### Phase 4: Results Saving
Generates a comprehensive report with:
- All discovered subdomains
- Online/offline status
- Detailed nmap scan results
- Timestamp and metadata

## Output

### Terminal Output
- Colored tables showing discovered subdomains
- Real-time scan progress with progress bars
- Immediate display of port scan results
- Summary statistics

### File Output
Results are automatically saved to:
```
subreconx_<domain>_<timestamp>.txt
```

Example: `subreconx_example_com_20250129_143022.txt`

The report includes:
- Complete subdomain list
- Online/offline categorization
- Full nmap scan outputs
- Scan metadata (date, target, statistics)

## Performance Tips

- **Parallel Scans**: Increase `-p` value for faster scanning (default: 5)
  - Recommended: 5-10 for home connections
  - Recommended: 10-20 for high-bandwidth connections
- **CPU Utilization**: Ping checks automatically use all CPU cores
- **Timeout Settings**: Subfinder timeout: 300s, Nmap timeout: 180s per host

## Legal Disclaimer

**IMPORTANT**: This tool is designed for authorized security testing only.

- Only use on domains you own or have explicit permission to test
- Unauthorized scanning may be illegal in your jurisdiction
- The author is not responsible for misuse or damage caused by this tool
- Always comply with applicable laws and regulations
- Respect rate limits and terms of service

## Troubleshooting

**Error: subfinder is not installed**
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
# Add $GOPATH/bin to your PATH
```

**Error: Rich not installed**
```bash
pip install rich
```

**Error: nmap not found**
```bash
# Install nmap using your system package manager (see Installation section)
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Created by**: [sachinkrpr](https://github.com/sachinkrpr)

## Acknowledgments

- [ProjectDiscovery](https://github.com/projectdiscovery) for subfinder
- [Nmap Project](https://nmap.org/) for nmap
- [Rich Library](https://github.com/Textualize/rich) for beautiful terminal output

---

**Version**: 1.0
**Last Updated**: 2025

For bug reports and feature requests, please open an issue on GitHub.
