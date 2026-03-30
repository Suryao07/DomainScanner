#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DomainScanner: Multi-threaded enumeration for subdomains, virtual hosts, and pages.

This tool automates reconnaissance by efficiently testing multiple targets in parallel.
It supports three scan modes:
  - DNS: Discover live subdomains via DNS resolution
  - VHost: Enumerate virtual hosts on a specific IP
  - Page: Discover hidden directories and files on a web server

Creator: https://github.com/Suryao07/
"""

import os
import sys
import shutil
import requests
import re
import time
import threading
import concurrent.futures
import socket
import ctypes
from urllib.parse import urlparse

LETTER = {
    "A": [" ___ ",
          " / _ \\ ",
          "/ /_\\ \\",
          "|  _  |",
          "| | | |",
          "\\_| |_/" ],
    "D": 
["______ ",
          "|  _  \\",
          "| | | |",
          "| | | |",
          "| |/ / ",
          "|___/  "],
    "O": [" _____ ",
          "/  _  \\",
          "| | | |",
          "| | | |",
          "\\ \\_/ /",
          " \\___/ "],
    "M": ["__  __ ",
          "|  \\/  |",
          "| .  . |",
          "| |\\/| |",
          "| |  | |",
 
          "|_|  |_|"],
    "I": [" _____ ",
           "|_   _|",
           "  | |  ",
           "  | |  ",
           " _| |_ ",
           " \\___/ "]
         
           ,
    "N": [" _   _ ",
          "| \\ | |",
          "|  \\| |",
          "| . ` |",
          "| |\\  |",
          "\\_| \\_/"],
    "S": [" _____ ",
          "/  ___|",
          "\\ `--. ",
          " `--. \\",
          "/\\__/ /",
          "\\____/ "],
    "C": [" _____ ",
          "/  __ \\",
          "| /  \\/",
          "| | ",
          "| \\__/\\",
          " \\____/"],
    "E": [" _____ ",
           "| ___|",
           "| |__  ",
           "|  __| ",
           "| |___ ",
           "\\____/"]
                    ,
    "R": ["______ ",
          "| ___ \\",
          "| |_/ /",
          "|  / /",
          "| |\\ \\ ",
          "\\_| \\_|"],
    " ": ["  ", "  ", "  ", "  ", "  ", "  "]
}

# ANSI color codes for terminal output
RED_BOLD = "\033[1;31m"
GREEN_BOLD = "\033[1;32m"
CYAN_BOLD = "\033[1;36m"
YELLOW_BOLD = "\033[1;33m" 
RESET = "\033[0m"

# Configuration constants
CREATOR_INFO = "             Tool Created By: https://github.com/Suryao07/"
MAX_THREADS = 100  # Maximum concurrent requests. Reduce if hitting rate limits
HTTP_TIMEOUT = 5   # Timeout in seconds for HTTP requests
DNS_TIMEOUT = 5    # Timeout in seconds for DNS lookups
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'

# Global state for thread-safe progress tracking
print_lock = threading.Lock()  # Prevents garbled output in multithreading
progress_counter = 0  # Tracks completed scans across threads
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_WORDLIST_DIR = os.path.join(SCRIPT_DIR, "wordlists")
DEFAULT_SUBDOMAIN_WORDLIST = "pro-combined.txt"
DEFAULT_PAGE_WORDLIST = "common_pages.txt"

def enable_windows_ansi():
    """
    Enable ANSI color escape sequences on Windows consoles.
    Allows colored terminal output on Windows 10+ without third-party libraries.
    Safe to call on non-Windows systems (returns early).
    """
    if os.name != "nt":
        return
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # Standard output handle
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    except Exception:
        pass  # Silently fail if ANSI is not supported

def render_banner(text):
    """
    Convert text into ASCII art banner using predefined letter glyphs.
    
    Args:
        text (str): The text to render. Converted to uppercase. Unsupported chars render as space.
    
    Returns:
        str: Multi-line ASCII art representation of the text.
    """
    text = text.upper()
    rows = len(next(iter(LETTER.values())))
    out_lines = []
    for r in range(rows):
        row_parts = []
        for ch in text:
            glyph = LETTER.get(ch, LETTER[" "])
            row_parts.append(glyph[r])
        out_lines.append("   ".join(row_parts))
    return "\n".join(out_lines)


def print_red_banner(text, center=True, padding=0):
    """
    Print a colored ASCII art banner to stdout.
    
    Args:
        text (str): Text to render as banner.
        center (bool): If True, centers the banner in terminal. Defaults to True.
        padding (int): Left padding in spaces. Defaults to 0.
    """
    # Generate banner from text (was missing - caused bug)
    banner = render_banner(text)
    
    if center:
        try:
            term_width = shutil.get_terminal_size().columns
        except Exception:
            term_width = 80
        centered_lines = []
        for line in banner.splitlines():
            padded = (" " * padding) + line
            centered_lines.append(padded.center(term_width))
        banner = "\n".join(centered_lines)
    sys.stdout.write(RED_BOLD + banner + RESET + "\n")

def scan_dns(url, total_scans):
    """
    Scan a single subdomain via DNS resolution.
    
    Args:
        url (str): Subdomain to test (e.g., "admin.example.com").
        total_scans (int): Total number of scans for progress tracking.
    
    Returns:
        str: The URL if found (status != 404), None otherwise.
        
    Side effects:
        - Updates global progress_counter
        - Prints results using thread-safe lock
    """
    global progress_counter
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(f"http://{url}", timeout=HTTP_TIMEOUT, headers=headers, allow_redirects=False)
        
        if response.status_code != 404:
            with print_lock:
                sys.stdout.write(f"\r{GREEN_BOLD}[+] Found (DNS): {url} {YELLOW_BOLD}(Status: {response.status_code}){RESET}\n")
            return url 
        
        return None
         
    except (requests.exceptions.ConnectionError, requests.exceptions.RequestException):
        return None 
        
    finally:
        with print_lock:
            progress_counter += 1
            if progress_counter % 100 == 0 or progress_counter == total_scans:
                padding = " " * 10 
                sys.stdout.write(f"\r{YELLOW_BOLD}[*] Progress: {progress_counter}/{total_scans} scans completed.{RESET}{padding}")
                sys.stdout.flush()


def scan_vhost(ip_address, url_to_test, total_scans):
    """
    Scan a single virtual host on a specific IP address.
    
    Args:
        ip_address (str): IP address to test (e.g., "192.0.2.1").
        url_to_test (str): Domain/vhost to test in Host header (e.g., "api.example.com").
        total_scans (int): Total number of scans for progress tracking.
    
    Returns:
        str: The vhost URL if found (status != 404), None otherwise.
        
    Side effects:
        - Updates global progress_counter
        - Prints results using thread-safe lock
    """
    global progress_counter
    try:
        custom_headers = {
            'User-Agent': USER_AGENT,
            'Host': url_to_test  # Send vhost in Host header
        }
        
        response = requests.get(f"http://{ip_address}", timeout=HTTP_TIMEOUT, headers=custom_headers, allow_redirects=False)
        
        if response.status_code != 404:
            with print_lock:
                sys.stdout.write(f"\r{GREEN_BOLD}[+] Found (VHost): {url_to_test} {YELLOW_BOLD}(Status: {response.status_code}){RESET}\n")
            return url_to_test
        
        return None
         
    except (requests.exceptions.ConnectionError, requests.exceptions.RequestException):
        return None 
        
    finally:
        with print_lock:
            progress_counter += 1
            if progress_counter % 100 == 0 or progress_counter == total_scans:
                padding = " " * 10 
                sys.stdout.write(f"\r{YELLOW_BOLD}[*] Progress: {progress_counter}/{total_scans} scans completed.{RESET}{padding}")
                sys.stdout.flush()


def scan_page(base_url, page_word, total_scans):
    """
    Scan for a single page or directory on a web server.
    
    Args:
        base_url (str): Base URL to scan (e.g., "http://example.com").
        page_word (str): Path to test (e.g., "admin", ".git", "config.php").
        total_scans (int): Total number of scans for progress tracking.
    
    Returns:
        str: Full URL if found (status != 404), None otherwise.
        
    Side effects:
        - Updates global progress_counter
        - Prints results using thread-safe lock
    """
    global progress_counter
    target_url = f"{base_url}/{page_word}"
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(target_url, timeout=HTTP_TIMEOUT, headers=headers, allow_redirects=False)

        if response.status_code != 404:
            with print_lock:
                sys.stdout.write(f"\r{GREEN_BOLD}[+] Found Page: {target_url} {YELLOW_BOLD}(Status: {response.status_code}){RESET}\n")
            return target_url
        
        return None

    except (requests.exceptions.ConnectionError, requests.exceptions.RequestException):
        return None 
        
    finally:
        with print_lock:
            progress_counter += 1
            if progress_counter % 100 == 0 or progress_counter == total_scans:
                padding = " " * 10 
                sys.stdout.write(f"\r{YELLOW_BOLD}[*] Progress: {progress_counter}/{total_scans} scans completed.{RESET}{padding}")
                sys.stdout.flush()

def is_valid_ip(ip_str):
    """
    Validate if a string is a valid IPv4 address.
    
    Args:
        ip_str (str): String to validate.
    
    Returns:
        bool: True if valid IPv4, False otherwise.
    """
    parts = ip_str.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def clean_and_validate_target(raw_target):
    """
    Clean and validate user input (domain or IP address).
    
    Args:
        raw_target (str): Raw user input.
    
    Returns:
        tuple: (input_type, value, error_msg)
            - input_type: 'ip' or 'domain', or None if invalid
            - value: Cleaned input value
            - error_msg: Error message if invalid, None otherwise
    """
   
    if not raw_target:
        return None, None, "Input cannot be empty."
    
    target = raw_target.strip()

    # Check if input is a plain IP address
    if is_valid_ip(target):
        return 'ip', target, None

    # Try to parse as URL or domain
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
    try:
        parsed_url = urlparse(target)
        domain = parsed_url.netloc
        domain = domain.split(':', 1)[0]  # Remove port if present
        
        if not domain:
             return None, None, "Invalid format. Could not extract domain."
        
        # Check if extracted domain is actually an IP
        if is_valid_ip(domain):
            return 'ip', domain, None
        
        # Domain must contain at least one dot
        if '.' not in domain:
            return None, None, "Invalid domain format. Must contain a '.'"
            
        return 'domain', domain, None

    except Exception as e:
        return None, None, f"An error occurred during parsing: {e}"

def run_scan(scan_mode, target_ip, base_domain, wordlist_path, total_scans):
    """
    Execute a threaded scan using the specified mode.
    
    Args:
        scan_mode (str): 'dns', 'vhost', or 'page'.
        target_ip (str): IP address for vhost scans, None for others.
        base_domain (str): Domain to scan or base URL for page scans.
        wordlist_path (str): Path to wordlist file.
        total_scans (int): Total lines in wordlist (for progress display).
    
    Returns:
        None (results are printed to stdout)
    """
    global progress_counter
    progress_counter = 0 
    found_items = []
    start_time = time.time() 

    # Select scan function and display mode info
    if scan_mode == 'vhost':
        sys.stdout.write(CYAN_BOLD + f"\n[*] Starting VHost scan on: {target_ip} (for {base_domain})\n" + RESET)
        scan_function = scan_vhost
    elif scan_mode == 'page':
        base_url = f"http://{base_domain}" 
        sys.stdout.write(CYAN_BOLD + f"\n[*] Starting Page scan on: {base_url}\n" + RESET)
        scan_function = scan_page
    else:  # default to 'dns'
        sys.stdout.write(CYAN_BOLD + f"\n[*] Starting DNS scan on: {base_domain}\n" + RESET)
        scan_function = scan_dns
        
    sys.stdout.write(CYAN_BOLD + f"[*] Using wordlist: {wordlist_path} ({total_scans} words) with {MAX_THREADS} threads\n" + RESET)
    sys.stdout.write(CYAN_BOLD + ("-" * 30) + "\n" + RESET)

    # Load wordlist
    try:
        with open(wordlist_path, 'r') as file:
            wordlist = [line.strip() for line in file if line.strip()]
    except Exception as e:
        sys.stdout.write(RED_BOLD + f"[-] Error reading wordlist during scan: {e}\n" + RESET)
        return

    # Submit tasks to thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        if scan_mode == 'vhost':
            futures = {executor.submit(scan_function, target_ip, f"{sub}.{base_domain}", total_scans): sub for sub in wordlist}
        elif scan_mode == 'page':
            futures = {executor.submit(scan_function, base_url, sub, total_scans): sub for sub in wordlist}
        else:  # dns
            futures = {executor.submit(scan_function, f"{sub}.{base_domain}", total_scans): sub for sub in wordlist}
        
        # Collect results as they complete
        try:
             for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    found_items.append(result)
                    
        except KeyboardInterrupt:
            sys.stdout.write(f"\n{RED_BOLD}[!] Scan interrupted by user. Stopping threads...{RESET}\n")
            executor.shutdown(wait=False, cancel_futures=True) 
    
    # Move cursor to new line after progress bar
    sys.stdout.write("\n") 
    
    end_time = time.time()
    
    # Print summary
    sys.stdout.write(CYAN_BOLD + ("-" * 30) + "\n" + RESET)
    sys.stdout.write(f"{CYAN_BOLD}[*] Scan complete in {end_time - start_time:.2f} seconds.{RESET}\n")
    if found_items:
        if scan_mode == 'page':
            sys.stdout.write(CYAN_BOLD + f"\n[+] Found {len(found_items)} responsive pages/directories (non-404):\n" + RESET)
        else:
            sys.stdout.write(CYAN_BOLD + f"\n[+] Found {len(found_items)} responsive subdomains (non-404):\n" + RESET)
        for item in found_items:
            sys.stdout.write(CYAN_BOLD + f"  - {item}\n" + RESET)
    else:
        if scan_mode == 'page':
            sys.stdout.write(CYAN_BOLD + "[-] No responsive (non-404) pages or directories found.\n" + RESET)
        else:
            sys.stdout.write(CYAN_BOLD + "[-] No responsive (non-404) subdomains found.\n" + RESET)
    return

def main_tool_loop():
    """
    Main interactive loop for the scanner.
    
    Prompts user for target domain/IP and scan mode, validates input, 
    and executes appropriate scan. Runs continuously until user exits.
    """
    print_red_banner("DOMAIN SCANNER", center=True, padding=0)
    enable_windows_ansi()
    info_text = "\nThis tool scans for subdomains, VHosts, and pages.\n"
    sys.stdout.write(CYAN_BOLD + info_text + RESET)
    sys.stdout.write(CYAN_BOLD + CREATOR_INFO + RESET + "\n")
    
    # Legal warning
    warning = (
        "\nWarning: This tool is for educational purposes only.\n"
        "Unauthorized scanning of domains may be illegal and unethical.\n"
        "Always obtain permission before scanning any domain.\n"
        f"\n{YELLOW_BOLD}Type 'exit' or press CTRL+C to quit.{RESET}\n"
    )
    sys.stdout.write(RED_BOLD + warning + RESET)

    while True:
        sys.stdout.write("\n" + ("-" * 40) + "\n")
        domain_to_scan = None
        ip_to_scan = None
        scan_mode = 'dns'
        
        try:
            raw_domain_input = input(f"{YELLOW_BOLD}[+] Enter domain or IP (e.g., example.com): {RESET}")
            if raw_domain_input.lower() == 'exit':
                break
            
            input_type, value, error_msg = clean_and_validate_target(raw_domain_input)
            
            if error_msg:
                sys.stdout.write(f"{RED_BOLD}[-] Error: {error_msg}{RESET}\n")
                continue

            if input_type == 'ip':
                # Try to resolve IP to hostname
                try:
                    hostname, _, _ = socket.gethostbyaddr(value)
                    sys.stdout.write(f"{GREEN_BOLD}[*] IP {value} resolves to hostname: {hostname}{RESET}\n")
                except socket.timeout:
                    sys.stdout.write(f"{RED_BOLD}[-] DNS lookup timed out for IP {value}.{RESET}\n")
                except (socket.herror, socket.gaierror):
                    sys.stdout.write(f"{RED_BOLD}[-] IP {value} does not resolve to a hostname.{RESET}\n")
                
                scan_choice = input(f"{YELLOW_BOLD}[?] Do you want to scan this IP for pages? (y/n): {RESET}").lower()
                if scan_choice.startswith('y'):
                    scan_mode = 'page'
                    domain_to_scan = value
                    ip_to_scan = None
                else:
                    sys.stdout.write(f"{CYAN_BOLD}[*] No scan will be performed.{RESET}\n")
                    continue
            
            elif input_type == 'domain':
                # Resolve domain to IP and offer scan modes
                domain_to_scan = value
                try:
                    # Set timeout for DNS operation
                    socket.setdefaulttimeout(DNS_TIMEOUT)
                    ip_address = socket.gethostbyname(value)
                    sys.stdout.write(f"{GREEN_BOLD}[*] Domain {value} resolves to IP: {ip_address}{RESET}\n")
                    
                    scan_choice = input(f"{YELLOW_BOLD}[?] Scan: (d)ns, (v)host, or (p)age? (default: d): {RESET}").lower()
                    if scan_choice.startswith('v'):
                        scan_mode = 'vhost'
                        ip_to_scan = ip_address
                    elif scan_choice.startswith('p'):
                        scan_mode = 'page'
                        ip_to_scan = None
                    else:
                        scan_mode = 'dns'
                        ip_to_scan = None
                        
                except socket.timeout:
                    sys.stdout.write(f"{RED_BOLD}[-] DNS lookup timed out for {value}. Try again.{RESET}\n")
                    continue
                except socket.gaierror:
                    sys.stdout.write(f"{RED_BOLD}[-] Error: Could not resolve domain {value} to an IP. VHost scan not possible.{RESET}\n")
                    scan_choice = input(f"{YELLOW_BOLD}[?] Scan: (d)ns or (p)age? (default: d): {RESET}").lower()
                    if scan_choice.startswith('p'):
                        scan_mode = 'page'
                    else:
                        scan_mode = 'dns'
                    ip_to_scan = None
                finally:
                    socket.setdefaulttimeout(None)  # Reset to default

            if domain_to_scan:
                # Select appropriate default wordlist based on scan mode
                if scan_mode == 'page':
                    default_list_name = DEFAULT_PAGE_WORDLIST
                    sys.stdout.write(f"{YELLOW_BOLD}[!] Note: Page scanning selected. Using page/directory wordlist.{RESET}\n")
                else:
                    default_list_name = DEFAULT_SUBDOMAIN_WORDLIST
                    sys.stdout.write(f"{YELLOW_BOLD}[!] Note: Subdomain scanning selected. Using subdomain wordlist.{RESET}\n")
                
                wordlist_input = input(f"{YELLOW_BOLD}[+] Enter path or default wordlist name (default: {default_list_name}): {RESET}") or default_list_name
                
                if wordlist_input.lower() == 'exit':
                    break

                # Resolve wordlist path
                wordlist_path = None
                
                if os.path.isfile(wordlist_input):
                    wordlist_path = wordlist_input
                else:
                    potential_path = os.path.join(DEFAULT_WORDLIST_DIR, wordlist_input)
                    if os.path.isfile(potential_path):
                        wordlist_path = potential_path

                if not wordlist_path:
                    sys.stdout.write(RED_BOLD + f"[-] Error: Wordlist not found at '{wordlist_input}' or '{potential_path}'\n" + RESET)
                    continue
                
                # Validate wordlist and get line count
                try:
                    with open(wordlist_path, 'r') as f:
                        total_scans = sum(1 for line in f if line.strip())
                    if total_scans == 0:
                        sys.stdout.write(RED_BOLD + f"[-] Error: Wordlist '{wordlist_path}' is empty.\n" + RESET)
                        continue
                except Exception as e:
                    sys.stdout.write(RED_BOLD + f"[-] Error reading wordlist: {e}\n" + RESET)
                    continue
                
                # Execute the scan
                run_scan(scan_mode, ip_to_scan, domain_to_scan, wordlist_path, total_scans) 
                     
        except EOFError:
             break
        except KeyboardInterrupt:
             break


if __name__ == "__main__":
    """
    Entry point for DomainScanner.
    Handles graceful shutdown and error reporting.
    """
    try:
        main_tool_loop()
        sys.stdout.write(f"\n{CYAN_BOLD}Exiting scanner. Goodbye!{RESET}\n")
    except KeyboardInterrupt:
        sys.stdout.write(f"\n{RED_BOLD}[!] Exiting scanner. Goodbye!{RESET}\n")
        sys.exit(0)
    except Exception as e:
        sys.stdout.write(f"\n{RED_BOLD}[!] An unexpected error occurred: {e}{RESET}\n")
