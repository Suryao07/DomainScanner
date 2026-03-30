# DomainScanner - API Reference

**Version**: 1.0  
**Last Updated**: March 2025

Complete function and configuration documentation for DomainScanner.

---

## Table of Contents

1. [Constants & Configuration](#constants--configuration)
2. [Function Reference](#function-reference)
3. [Data Structures](#data-structures)
4. [Error Handling](#error-handling)
5. [Threading & Concurrency](#threading--concurrency)
6. [Code Examples](#code-examples)
7. [Extending the Tool](#extending-the-tool)

---

## Constants & Configuration

### Threading Configuration

```python
MAX_THREADS = 100
```
- **Type**: `int`
- **Purpose**: Maximum number of concurrent threads in the thread pool
- **Range**: 1-500 (tested up to 200)
- **Tuning advice**:
  - Use 10-20 for aggressive targets with WAF protection
  - Use 100+ for cooperative targets with no rate limiting
  - Use 200+ for fast local networks
  - Higher values = faster scans but more target load
- **Default**: 100 is optimal for typical internet targets

**Example**:
```python
MAX_THREADS = 50  # For rate-limited targets
```

---

### HTTP Configuration

```python
HTTP_TIMEOUT = 5
```
- **Type**: `int` (seconds)
- **Purpose**: Timeout for HTTP requests to target server
- **Range**: 1-30 (practical)
- **Tuning advice**:
  - 1-2 seconds: Fast but misses slow responses
  - 5 seconds: **Recommended (default)**
  - 10+ seconds: Thorough but slower
- **Behavior**: If request takes longer than N seconds, it's treated as not found

**Example**:
```python
HTTP_TIMEOUT = 3  # For faster scanning on fast networks
```

---

### DNS Configuration

```python
DNS_TIMEOUT = 5
```
- **Type**: `int` (seconds)
- **Purpose**: Timeout for DNS resolution operations
- **Used in**: Domain-to-IP resolution, reverse lookups
- **Range**: 1-30 (practical)
- **Behavior**: If DNS query takes longer than N seconds, operation fails gracefully

**Example**:
```python
DNS_TIMEOUT = 10  # For unreliable DNS servers
```

---

### HTTP User-Agent

```python
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
```
- **Type**: `str`
- **Purpose**: User-Agent header sent with all HTTP requests
- **Why needed**: Some servers block requests without valid User-Agent
- **Customization**: Can modify to use different browser signatures

**Example**:
```python
USER_AGENT = 'curl/7.80.0'  # Pretend to be curl
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) ...'  # Pretend to be Linux Firefox
```

---

### Wordlist Configuration

```python
DEFAULT_SUBDOMAIN_WORDLIST = "pro-combined.txt"
DEFAULT_PAGE_WORDLIST = "common_pages.txt"
```
- **Type**: `str` (filename)
- **Purpose**: Default wordlists for DNS and Page scans
- **Location**: `wordlists/` directory in project root

---

### Built-in Wordlists

| File | Entries | Best For | Time |
|------|---------|----------|------|
| `small.txt` | 500 | Quick reconnaissance | 1-2 min |
| `medium.txt` | 5,000 | Balanced approach | 10-20 min |
| `large.txt` | 20,000+ | Thorough enumeration | 50+ min |
| `pro-combined.txt` | High-quality subset | Default (recommended) | 30-45 min |
| `common_pages.txt` | 1,000+ | Directory discovery | 10-15 min |

---

## Function Reference

### `enable_windows_ansi()`

Enables ANSI color escape sequences on Windows consoles.

```python
def enable_windows_ansi():
    """
    Enable ANSI color escape sequences on Windows consoles.
    Allows colored terminal output on Windows 10+ without third-party libraries.
    Safe to call on non-Windows systems (returns early).
    """
```

**Parameters**: None

**Returns**: None

**Side effects**:
- Modifies Windows console mode to support ANSI colors
- No effect on macOS/Linux (safe to call)

**Example**:
```python
enable_windows_ansi()  # Must call this in main_tool_loop
# Now colored output like f"{RED_BOLD}Error{RESET}" displays correctly
```

**Why it matters**: Without this, colored output appears as raw escape codes on Windows

---

### `is_valid_ip(ip_str)`

Validates if a string is a valid IPv4 address.

```python
def is_valid_ip(ip_str):
    """
    Validate if a string is a valid IPv4 address.
    
    Args:
        ip_str (str): String to validate.
    
    Returns:
        bool: True if valid IPv4, False otherwise.
    """
```

**Parameters**:
- `ip_str` (str): Potential IP address to validate

**Returns**:
- `True` if valid IPv4 (e.g., "192.0.2.1")
- `False` if invalid (e.g., "999.999.999.999", "example.com", "")

**Validation rules**:
- Must have exactly 4 octets (parts separated by dots)
- Each octet must be 0-255
- Must be numeric (no letters)

**Example**:
```python
is_valid_ip("192.0.2.1")      # True
is_valid_ip("10.0.0.1")       # True
is_valid_ip("999.0.0.1")      # False (octet > 255)
is_valid_ip("192.0.2")        # False (only 3 octets)
is_valid_ip("example.com")    # False (not numeric)
```

---

### `clean_and_validate_target(raw_target)`

Cleans and validates user input (domain or IP address).

```python
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
```

**Parameters**:
- `raw_target` (str): User-provided string (domain, IP, or URL)

**Returns**:
- Tuple of `(input_type, value, error_msg)`
  - `input_type`: 'ip', 'domain', or None
  - `value`: The cleaned/extracted target
  - `error_msg`: Error description if validation failed

**Example**:
```python
# IP address
type, val, err = clean_and_validate_target("192.0.2.1")
# Returns: ('ip', '192.0.2.1', None)

# Plain domain
type, val, err = clean_and_validate_target("example.com")
# Returns: ('domain', 'example.com', None)

# URL format
type, val, err = clean_and_validate_target("http://example.com:8080")
# Returns: ('domain', 'example.com', None)  # Port stripped

# Invalid input
type, val, err = clean_and_validate_target("localhost")
# Returns: (None, None, "Invalid domain format. Must contain a '.'")
```

---

### `scan_dns(url, total_scans)`

Scan a single subdomain via DNS resolution and HTTP.

```python
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
```

**Parameters**:
- `url` (str): Full subdomain to test (e.g., "admin.example.com")
- `total_scans` (int): Total entries in wordlist (for progress reporting)

**Returns**:
- URL string if found (status != 404)
- `None` if not found or error

**How it works**:
1. Makes HTTP request to `http://admin.example.com`
2. Checks response status code
3. If status != 404, reports as found
4. Updates progress counter (thread-safe)

**Example**:
```python
result = scan_dns("api.example.com", 5000)
if result:
    print(f"Found: {result}")  # "api.example.com"
```

**Thread behavior**: 
- Called by 100+ threads simultaneously
- Each thread processes one subdomain
- Progress updates appear every 100 scans

---

### `scan_vhost(ip_address, url_to_test, total_scans)`

Scan a single virtual host on a specific IP address.

```python
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
```

**Parameters**:
- `ip_address` (str): IP to target (e.g., "192.0.2.1")
- `url_to_test` (str): Vhost domain to send in Host header
- `total_scans` (int): Total scans for progress tracking

**Returns**:
- Vhost URL string if found (status != 404)
- `None` if not found or error

**How it works**:
1. Makes HTTP request to IP address
2. Sets Host header to the test domain
3. Server responds based on configured vhosts
4. If status != 404, vhost is active on that IP

**Example**:
```python
# Scanning 192.0.2.1 for vhost "api.example.com"
result = scan_vhost("192.0.2.1", "api.example.com", 5000)
# Makes request: GET http://192.0.2.1 with Host: api.example.com
# If 200, returns "api.example.com"
```

**Use case**: Finding internal/uncommon vhosts on shared hosting

---

### `scan_page(base_url, page_word, total_scans)`

Scan for a single page or directory on a web server.

```python
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
```

**Parameters**:
- `base_url` (str): Base URL (e.g., "http://example.com")
- `page_word` (str): Path to append (e.g., "admin", ".git")
- `total_scans` (int): Total scans for progress tracking

**Returns**:
- Full URL string if found (status != 404)
- `None` if not found or error

**How it works**:
1. Constructs URL: `http://example.com` + `/admin`
2. Makes HTTP request
3. If status != 404, reports as found
4. Updates progress counter

**Example**:
```python
result = scan_page("http://example.com", "admin", 1000)
# URL tested: http://example.com/admin
# Returns "http://example.com/admin" if status != 404

result = scan_page("http://example.com", ".git", 1000)
# URL tested: http://example.com/.git
```

**Common findings**:
- `/admin` → Admin panel
- `/api` → API endpoints
- `.git` → Exposed git repository
- `config.php` → Configuration files
- `web.config` → IIS configuration

---

### `run_scan(scan_mode, target_ip, base_domain, wordlist_path, total_scans)`

Execute a threaded scan using the specified mode.

```python
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
```

**Parameters**:
- `scan_mode` (str): One of 'dns', 'vhost', or 'page'
- `target_ip` (str): IP address (only used for vhost mode)
- `base_domain` (str): Domain or base URL
- `wordlist_path` (str): Path to wordlist file
- `total_scans` (int): Line count of wordlist

**Returns**: None (prints results directly)

**How it works**:
1. Initializes ThreadPoolExecutor with 100 threads
2. Submits scan task for each wordlist entry
3. Collects results as threads complete
4. Prints summary with timing and results

**Example**:
```python
# DNS scan
run_scan(
    scan_mode='dns',
    target_ip=None,
    base_domain='example.com',
    wordlist_path='wordlists/small.txt',
    total_scans=500
)

# VHost scan
run_scan(
    scan_mode='vhost',
    target_ip='192.0.2.1',
    base_domain='example.com',
    wordlist_path='wordlists/small.txt',
    total_scans=500
)
```

---

### `main_tool_loop()`

Main interactive loop for the scanner.

```python
def main_tool_loop():
    """
    Main interactive loop for the scanner.
    
    Prompts user for target domain/IP and scan mode, validates input, 
    and executes appropriate scan. Runs continuously until user exits.
    """
```

**Parameters**: None

**Returns**: None

**Flow**:
1. Displays banner
2. Prompts for domain/IP
3. Validates input
4. Determines scan mode options
5. Prompts for wordlist
6. Calls `run_scan()`
7. Loops until user types "exit" or Ctrl+C

**User interaction**:
```
Enter domain or IP (e.g., example.com): example.com
Domain example.com resolves to IP: 192.0.2.1
Scan: (d)ns, (v)host, or (p)age? (default: d): d
Enter path or default wordlist name (default: pro-combined.txt): 
```

**Error handling**:
- Invalid input → Prompts again
- DNS timeout → Shows error, tries alternate modes
- Wordlist not found → Prompts for new path
- Ctrl+C → Graceful exit

---

## Data Structures

### Configuration Dictionary (implicit)

While no explicit dict is used, these constants form the "configuration":

```python
CONFIG = {
    'MAX_THREADS': 100,
    'HTTP_TIMEOUT': 5,
    'DNS_TIMEOUT': 5,
    'USER_AGENT': 'Mozilla/5.0 ...',
    'DEFAULT_WORDLIST': 'pro-combined.txt'
}
```

To modify behavior, edit these constants at the top of the script.

---

### Global State

```python
print_lock = threading.Lock()     # Protects simultaneous stdout writes
progress_counter = 0              # Counts completed scan tasks
```

**Why global?**: Threading needs shared state to coordinate across threads

**Thread-safe usage**:
```python
with print_lock:
    progress_counter += 1
    sys.stdout.write(f"Progress: {progress_counter}\n")
```

---

## Error Handling

### HTTP Errors

```python
try:
    response = requests.get(url, timeout=HTTP_TIMEOUT, ...)
except requests.exceptions.ConnectionError:
    # Network unreachable, server refused connection
    return None
except requests.exceptions.RequestException:
    # General HTTP error (timeout, SSL error, etc)
    return None
```

**Behavior**: Errors are silently skipped; scan continues

---

### DNS Errors

```python
try:
    socket.setdefaulttimeout(DNS_TIMEOUT)
    ip_address = socket.gethostbyname(domain)
except socket.timeout:
    # DNS lookup timed out
    print("[!] DNS lookup timed out")
    return None
except socket.gaierror:
    # DNS lookup failed (host not found)
    print("[!] Could not resolve domain")
    return None
finally:
    socket.setdefaulttimeout(None)  # Reset
```

---

### File I/O Errors

```python
try:
    with open(wordlist_path, 'r') as f:
        wordlist = [line.strip() for line in f]
except FileNotFoundError:
    print(f"[-] Wordlist not found: {wordlist_path}")
    return
except IOError as e:
    print(f"[-] Error reading file: {e}")
    return
```

---

## Threading & Concurrency

### ThreadPoolExecutor Pattern

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    # Submit all tasks
    futures = {
        executor.submit(scan_function, arg): arg 
        for arg in wordlist
    }
    
    # Process as completed (not in order)
    for future in concurrent.futures.as_completed(futures):
        result = future.result()  # Blocks until task complete
        if result:
            found_items.append(result)
```

**Key points**:
- `max_workers=100`: At most 100 threads
- `executor.submit()`: Returns immediately (non-blocking)
- `as_completed()`: Process results as they finish
- `future.result()`: Block and get the return value

---

### Thread-Safe Output

```python
print_lock = threading.Lock()

# WRONG (corrupted output):
sys.stdout.write(f"Found: {item}\n")
progress_counter += 1

# CORRECT (thread-safe):
with print_lock:
    sys.stdout.write(f"Found: {item}\n")
with print_lock:
    progress_counter += 1
```

**Why?**: Lock ensures only one thread writes at a time

---

## Code Examples

### Example 1: Scan a single domain for subdomains

```python
import subprocess

# Run the main tool
subprocess.run(['python', 'DomainScanner'])
# Then:
# Enter domain: example.com
# Scan: dns
# Wordlist: pro-combined.txt (default)
```

### Example 2: Custom wordlist for page discovery

Create a file `my_paths.txt`:
```
admin
api
upload
form
backup
config
database
```

Then run:
```bash
python DomainScanner
> Enter domain: example.com
> Scan: (d)ns, (v)host, or (p)age? p
> Wordlist: my_paths.txt
```

### Example 3: Modify MAX_THREADS for rate-limited target

Edit `DomainScanner` script:
```python
MAX_THREADS = 10  # Instead of 100
```

Then run normally. Scanning will be slower but won't trigger WAF.

### Example 4: Use custom User-Agent

Edit script:
```python
USER_AGENT = 'curl/7.80.0'
```

All HTTP requests will identify as curl instead of browser.

---

## Extending the Tool

### Adding a New Scan Mode

To add a new scanning technique:

1. **Create a scan function** (following the pattern):
```python
def scan_custom(target, word, total_scans):
    """Your custom scan logic."""
    global progress_counter
    
    try:
        # Your HTTP request or network operation
        result = your_logic_here()
        
        if result:
            with print_lock:
                sys.stdout.write(f"[+] Found: {result}\n")
            return result
    
    except Exception:
        pass
    
    finally:
        with print_lock:
            progress_counter += 1
```

2. **Add mode selection in main_tool_loop()**:
```python
scan_choice = input("[?] Scan: (d)ns, (c)ustom? ").lower()
if scan_choice.startswith('c'):
    scan_mode = 'custom'
```

3. **Handle in run_scan()**:
```python
if scan_mode == 'custom':
    scan_function = scan_custom
    futures = {executor.submit(scan_function, target, word, total): word 
               for word in wordlist}
```

### Modifying Progress Reporting

Current: Progress every 100 scans

To change to every 50:
```python
if progress_counter % 50 == 0 or progress_counter == total_scans:
    sys.stdout.write(f"Progress: {progress_counter}/{total_scans}\n")
```

To show percentage:
```python
percent = (progress_counter / total_scans) * 100
sys.stdout.write(f"Progress: {percent:.1f}%\n")
```

### Using DomainScanner as a Library

While designed as a CLI tool, you can import it:

```python
import sys
sys.path.insert(0, '/path/to/DomainScanner')

from DomainScanner import scan_dns, run_scan, is_valid_ip

# Use functions directly
if is_valid_ip("192.0.2.1"):
    print("Valid IP")

# Run a scan programmatically
run_scan('dns', None, 'example.com', 'wordlists/small.txt', 500)
```

---

**Last Updated**: March 2025
