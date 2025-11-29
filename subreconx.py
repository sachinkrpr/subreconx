#!/usr/bin/env python3
"""
SubReconX - Advanced Subdomain Reconnaissance Tool
For authorized penetration testing only
Created by: sachinkrpr
"""

import subprocess
import sys
import os
import argparse
import concurrent.futures
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
except ImportError:
    print("[!] Rich not installed. Run: pip install rich")
    sys.exit(1)

console = Console()

# ============================================================================
# BANNER
# ============================================================================

def print_banner():
    banner = """[bold red]
   ███████╗██╗   ██╗██████╗ ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗██╗  ██╗
   ██╔════╝██║   ██║██╔══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║╚██╗██╔╝
   ███████╗██║   ██║██████╔╝██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║ ╚███╔╝ 
   ╚════██║██║   ██║██╔══██╗██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║ ██╔██╗ 
   ███████║╚██████╔╝██████╔╝██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║██╔╝ ██╗
   ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝
[/bold red]
[white]                  Advanced Subdomain Reconnaissance Tool v1.0[/white]
[dim]                         Created by: [bold yellow]sachinkrpr[/bold yellow][/dim]
"""
    console.print(banner)

# ============================================================================
# SUBDOMAIN DISCOVERY
# ============================================================================

def run_subfinder(domain):
    """Run subfinder to find subdomains"""
    
    subdomains = []
    
    with Progress(
        SpinnerColumn(style="red"),
        TextColumn("[bold white]{task.description}[/bold white]"),
        console=console
    ) as progress:
        task = progress.add_task("Running subfinder...", total=None)
        
        try:
            result = subprocess.run(
                ["subfinder", "-d", domain, "-silent"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            subdomains = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
        except FileNotFoundError:
            console.print("[bold red][!] Error: subfinder is not installed[/bold red]")
            console.print("[yellow]    Install: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest[/yellow]")
            sys.exit(1)
        except subprocess.TimeoutExpired:
            console.print("[bold red][!] Subfinder timed out[/bold red]")
    
    return subdomains

# ============================================================================
# PING CHECK
# ============================================================================

def ping_single(subdomain):
    """Ping a single subdomain"""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", subdomain],
            capture_output=True,
            text=True,
            timeout=5
        )
        return subdomain, result.returncode == 0
    except:
        return subdomain, False

def check_online_subdomains(subdomains):
    """Check which subdomains are online using max threads"""
    
    online = []
    offline = []
    
    # Use max CPU cores
    max_threads = os.cpu_count() or 10
    
    with Progress(
        SpinnerColumn(style="red"),
        TextColumn("[bold white]{task.description}[/bold white]"),
        BarColumn(complete_style="red", finished_style="green"),
        TextColumn("[white]{task.completed}/{task.total}[/white]"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Pinging subdomains...", total=len(subdomains))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {executor.submit(ping_single, sub): sub for sub in subdomains}
            
            for future in concurrent.futures.as_completed(futures):
                subdomain, is_online = future.result()
                if is_online:
                    online.append(subdomain)
                else:
                    offline.append(subdomain)
                progress.advance(task)
    
    return online, offline

# ============================================================================
# NMAP SCANNING
# ============================================================================

def nmap_scan(subdomain):
    """Run nmap -sV scan on a subdomain"""
    try:
        result = subprocess.run(
            ["nmap", "-sV", subdomain],
            capture_output=True,
            text=True,
            timeout=180
        )
        return subdomain, result.stdout
    except FileNotFoundError:
        return subdomain, "[!] nmap not installed"
    except subprocess.TimeoutExpired:
        return subdomain, "[!] Scan timed out"
    except Exception as e:
        return subdomain, f"[!] Error: {str(e)}"

def parse_nmap_output(output):
    """Parse nmap output to extract port info"""
    ports = []
    lines = output.split('\n')
    
    for line in lines:
        if '/tcp' in line or '/udp' in line:
            parts = line.split()
            if len(parts) >= 3:
                ports.append({
                    'port': parts[0],
                    'state': parts[1],
                    'service': ' '.join(parts[2:])
                })
    
    return ports

def run_parallel_nmap(online_subdomains, parallel_count=5):
    """Run nmap scans in parallel and display results as they complete"""
    
    scan_results = {}
    total = len(online_subdomains)
    completed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_count) as executor:
        futures = {executor.submit(nmap_scan, sub): sub for sub in online_subdomains}
        
        for future in concurrent.futures.as_completed(futures):
            subdomain, result = future.result()
            scan_results[subdomain] = result
            completed += 1
            
            # Display result immediately
            display_scan_result(subdomain, result, completed, total)
    
    return scan_results

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_subdomains(subdomains, domain):
    """Display found subdomains in a table"""
    
    table = Table(
        title=f"[bold red]★ Subdomains Found for {domain} ★[/bold red]",
        show_header=True,
        header_style="bold white",
        border_style="red"
    )
    
    table.add_column("#", style="red", width=6)
    table.add_column("Subdomain", style="white")
    
    for i, sub in enumerate(subdomains, 1):
        table.add_row(str(i), sub)
    
    console.print(table)

def display_online_status(online, offline):
    """Display online/offline status"""
    
    # Online table
    if online:
        table = Table(
            title=f"[bold green]★ Online Subdomains ({len(online)}) ★[/bold green]",
            show_header=True,
            header_style="bold white",
            border_style="green"
        )
        
        table.add_column("#", style="green", width=6)
        table.add_column("Subdomain", style="white")
        table.add_column("Status", style="green")
        
        for i, sub in enumerate(online, 1):
            table.add_row(str(i), sub, "● ONLINE")
        
        console.print(table)
    
    # Offline table
    if offline:
        table = Table(
            title=f"[bold red]★ Offline Subdomains ({len(offline)}) ★[/bold red]",
            show_header=True,
            header_style="bold white",
            border_style="red"
        )
        
        table.add_column("#", style="red", width=6)
        table.add_column("Subdomain", style="dim white")
        table.add_column("Status", style="red")
        
        for i, sub in enumerate(offline, 1):
            table.add_row(str(i), sub, "○ OFFLINE")
        
        console.print(table)

def display_scan_result(subdomain, nmap_output, index, total):
    """Display single nmap scan result immediately"""
    
    ports = parse_nmap_output(nmap_output)
    
    console.print(f"\n[bold red][{index}/{total}][/bold red] [white]Scan Complete:[/white] [bold red]{subdomain}[/bold red]")
    console.print("[dim]" + "-" * 50 + "[/dim]")
    
    if ports:
        table = Table(
            show_header=True,
            header_style="bold white",
            border_style="red"
        )
        
        table.add_column("Port", style="red", width=12)
        table.add_column("State", style="green", width=10)
        table.add_column("Service/Version", style="white")
        
        for port in ports:
            state_color = "green" if port['state'] == 'open' else "red"
            table.add_row(
                port['port'],
                f"[{state_color}]{port['state']}[/{state_color}]",
                port['service']
            )
        
        console.print(table)
    else:
        console.print("[yellow]No open ports found[/yellow]")

# ============================================================================
# SAVE RESULTS
# ============================================================================

def save_results(domain, subdomains, online, offline, scan_results, filename):
    """Save results to txt file"""
    
    with open(filename, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("   SubReconX - Reconnaissance Report\n")
        f.write("   Created by: sachinkrpr\n")
        f.write("=" * 70 + "\n")
        f.write(f"Target: {domain}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"[TOTAL SUBDOMAINS: {len(subdomains)}]\n")
        f.write("-" * 50 + "\n")
        for sub in subdomains:
            f.write(f"  {sub}\n")
        
        if online:
            f.write(f"\n[ONLINE: {len(online)}]\n")
            f.write("-" * 50 + "\n")
            for sub in online:
                f.write(f"  [UP] {sub}\n")
        
        if offline:
            f.write(f"\n[OFFLINE: {len(offline)}]\n")
            f.write("-" * 50 + "\n")
            for sub in offline:
                f.write(f"  [DOWN] {sub}\n")
        
        if scan_results:
            f.write(f"\n[NMAP SCAN RESULTS]\n")
            f.write("=" * 70 + "\n")
            for subdomain, result in scan_results.items():
                f.write(f"\n--- {subdomain} ---\n")
                f.write(result)
                f.write("\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("End of Report - Generated by SubReconX\n")
        f.write("=" * 70 + "\n")
    
    console.print(f"\n[bold green]✓ Results saved to:[/bold green] [white]{filename}[/white]")

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SubReconX - Advanced Subdomain Reconnaissance Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python subreconx.py -d example.com
  python subreconx.py -d example.com -p 10
        """
    )
    
    parser.add_argument(
        "-d", "--domain",
        required=True,
        help="Target domain to scan"
    )
    parser.add_argument(
        "-p", "--parallel",
        type=int,
        default=5,
        help="Number of parallel nmap scans (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Clean domain
    domain = args.domain.replace("https://", "").replace("http://", "").strip("/")
    
    console.print(Panel(
        f"[bold white]Target:[/bold white] [red]{domain}[/red]\n"
        f"[bold white]Parallel Scans:[/bold white] [red]{args.parallel}[/red]",
        title="[bold red]★ Scan Configuration ★[/bold red]",
        border_style="red"
    ))
    
    # Step 1: Find subdomains
    console.print("\n[bold red][PHASE 1][/bold red] [white]Subdomain Discovery[/white]")
    console.print("[dim]" + "-" * 50 + "[/dim]")
    
    subdomains = run_subfinder(domain)
    
    if not subdomains:
        console.print("[bold red][!] No subdomains found[/bold red]")
        sys.exit(1)
    
    console.print(f"[bold green]✓ Found {len(subdomains)} subdomains[/bold green]\n")
    display_subdomains(subdomains, domain)
    
    # Step 2: Ping check
    console.print("\n[bold red][PHASE 2][/bold red] [white]Checking Online Status[/white]")
    console.print("[dim]" + "-" * 50 + "[/dim]")
    
    online, offline = check_online_subdomains(subdomains)
    
    console.print(f"\n[bold green]✓ Online: {len(online)}[/bold green] | [bold red]✗ Offline: {len(offline)}[/bold red]\n")
    display_online_status(online, offline)
    
    # Step 3: Nmap scanning (parallel with live results)
    scan_results = {}
    
    if online:
        console.print("\n[bold red][PHASE 3][/bold red] [white]Nmap Service Scanning[/white]")
        console.print("[dim]" + "-" * 50 + "[/dim]")
        console.print(f"[white]Scanning [red]{len(online)}[/red] online subdomain(s) with [red]{args.parallel}[/red] parallel scans...[/white]\n")
        
        scan_results = run_parallel_nmap(online, args.parallel)
    
    # Step 4: Save results
    console.print("\n[bold red][PHASE 4][/bold red] [white]Saving Results[/white]")
    console.print("[dim]" + "-" * 50 + "[/dim]")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"subreconx_{domain.replace('.', '_')}_{timestamp}.txt"
    
    save_results(domain, subdomains, online, offline, scan_results, filename)
    
    # Final summary
    console.print("\n" + "=" * 50)
    console.print(Panel(
        f"[bold white]Total Subdomains:[/bold white] [red]{len(subdomains)}[/red]\n"
        f"[bold white]Online:[/bold white] [green]{len(online)}[/green]\n"
        f"[bold white]Offline:[/bold white] [red]{len(offline)}[/red]\n"
        f"[bold white]Scanned:[/bold white] [red]{len(scan_results)}[/red]",
        title="[bold red]★ SubReconX Complete ★[/bold red]",
        border_style="red"
    ))

if __name__ == "__main__":
    main()
