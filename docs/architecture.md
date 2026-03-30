# DomainScanner - System Architecture

**Version**: 1.0  
**Last Updated**: March 2025

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Scanning Modes](#scanning-modes)
3. [Threading Model](#threading-model)
4. [Data Flow](#data-flow)
5. [Design Decisions](#design-decisions)
6. [Performance Considerations](#performance-considerations)
7. [Error Handling](#error-handling)

---

## System Overview

DomainScanner is a multithreaded Python tool for automated web reconnaissance. It discovers hidden infrastructure (subdomains, virtual hosts, directories) by testing words from a wordlist against a target.

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│           User Input Layer (main_tool_loop)             │
│  - Validates domain/IP input                            │
│  - Selects scan mode (DNS/VHost/Page)                   │
│  - Loads wordlist                                       │
└────────────────┬────────────────────────────────────────┘
                 │
┌─────────────────▼────────────────────────────────────────┐
│         Dispatch Layer (run_scan)                        │
│  - Initializes ThreadPoolExecutor (MAX_THREADS=100)     │
│  - Submits tasks to thread pool                         │
│  - Collects results as completed                        │
└────────────────┬────────────────────────────────────────┘
                 │
┌─────────────────▼────────────────────────────────────────┐
│    Worker Layer (Scan Functions)                        │
│  ├─ scan_dns(url, total_scans)                          │
│  ├─ scan_vhost(ip, url, total_scans)                    │
│  └─ scan_page(base_url, page_word, total_scans)         │
│                                                          │
│  Each worker:                                           │
│  - Makes HTTP request with timeout                      │
│  - Checks response status code                          │
│  - Reports non-404 results                              │
│  - Updates progress counter (thread-safe)               │
└─────────────────────────────────────────────────────────┘
```

### Key Modules

| Module | Purpose | Key Dependencies |
|--------|---------|------------------|
| `requests` | HTTP client for making requests | External library |
| `socket` | DNS resolution, network operations | Python stdlib |
| `concurrent.futures` | ThreadPoolExecutor for parallel scanning | Python stdlib |
| `threading` | Lock for thread-safe output | Python stdlib |
| `os`, `sys` | File and terminal I/O | Python stdlib |

---

## Scanning Modes

### DNS Mode

**Purpose**: Discover live subdomains via DNS resolution

**Flow**:
```
Input: domain = "example.com", wordlist = ["admin", "api", "mail", ...]
       ↓
For each word in wordlist:
  Creates URL: "admin.example.com"
  Makes HTTP request to "http://admin.example.com"
  Checks response status:
    - 404 → Not found, skip
    - 200, 301, 403, etc. → Found, report
       ↓
Output: List of subdomains with HTTP status codes
```

**Example**:
```bash
python DomainScanner
> Enter domain: example.com
> Scan: (d)ns, (v)host, or (p)age? d
> Wordlist: (default uses pro-combined.txt)

[+] Found (DNS): www.example.com (Status: 200)
[+] Found (DNS): api.example.com (Status: 200)
[+] Found (DNS): admin.example.com (Status: 403)
```

**Use Case**: Map externally accessible subdomains during reconnaissance

---

### VHost Mode

**Purpose**: Discover virtual hosts hosted on a specific IP address

**Flow**:
```
Input: domain = "example.com", wordlist = ["admin", "api", "mail", ...]
       ↓
Step 1: Resolve "example.com" to IP (e.g., 192.0.2.1)
       ↓
Step 2: For each word in wordlist:
  Creates vhost: "admin.example.com"
  Makes HTTP request to "http://192.0.2.1"
  Sets Host header: "admin.example.com"
  Checks response status:
    - 404 → Not found, skip
    - 200, 301, 403, etc. → Found (vhost is configured)
       ↓
Output: List of vhosts found on that IP
```

**Why this matters**:
- Many domains share a single IP address
- DNS records may not exist but vhosts are still configured
- Useful for finding internal/development domains
- Can reveal subdomain typos or internal naming

**Example**:
```bash
> Enter domain: example.com
> Domain example.com resolves to IP: 192.0.2.1
> Scan: (d)ns, (v)host, or (p)age? v

[+] Found (VHost): internal.example.com (Status: 200)
[+] Found (VHost): staging.example.com (Status: 403)
[+] Found (VHost): dev-api.example.com (Status: 200)
```

---

### Page Mode

**Purpose**: Enumerate hidden directories and files on a web server

**Flow**:
```
Input: domain = "example.com", wordlist = ["admin", "api", ".git", "config.php", ...]
       ↓
For each word in wordlist:
  Creates URL: "http://example.com/admin"
  Makes HTTP request
  Checks response status:
    - 404 → Not found, skip
    - 200, 301, 403, etc. → Found, report
       ↓
Output: List of accessible pages/directories
```

**Example**:
```bash
> Enter domain: example.com
> Scan: (d)ns, (v)host, or (p)age? p

[+] Found Page: http://example.com/api (Status: 200)
[+] Found Page: http://example.com/admin (Status: 403)
[+] Found Page: http://example.com/.git (Status: 301)
[+] Found Page: http://example.com/config.php (Status: 200)
```

**Use Case**: Find administrative panels, API endpoints, configuration files, version control repositories

---

## Threading Model

### Architecture

**Single-threaded vs Multithreaded**:

| Aspect | Single Thread | With ThreadPool |
|--------|---------------|-----------------|
| Scanning 5,000 URLs at 1 req/sec | 83 minutes | ~50 seconds |
| Server load (rate limiting) | Low | Higher |
| Responsiveness | Blocked | Interactive |
| Complexity | Simple | Moderate |

### Implementation

**ThreadPoolExecutor Pattern**:

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    # Submit all tasks at once
    futures = {executor.submit(scan_function, args): item for item in wordlist}
    
    # Process results as they complete (not in order)
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            found_items.append(result)
```

**Why this approach**:
- At most 100 threads running simultaneously (configurable)
- Tasks complete out-of-order (faster overall than waiting for each)
- Memory efficient (doesn't load all results at once)
- Easy to implement with standard library

### Thread-Safe Output

**Problem**: Multiple threads writing to stdout simultaneously = garbled text

```
[+] Found: www.example.com (Status: 200)[*] Progress: 200/5000
[+] F[*] Pround: api.example.com (Status: 200)ogress: 201/5000
```

**Solution**: Use threading.Lock()

```python
print_lock = threading.Lock()  # Protects stdout writes

def scan_dns(url, total_scans):
    # ... HTTP request ...
    if response.status_code != 404:
        with print_lock:  # Acquire lock, do this atomically
            sys.stdout.write(f"[+] Found (DNS): {url}\n")
    
    with print_lock:  # Another critical section
        progress_counter += 1
        sys.stdout.write(f"\r[*] Progress: {progress_counter}/{total_scans}")
```

**global State**:
```python
print_lock = threading.Lock()       # Prevents output corruption
progress_counter = 0                # Tracks completed requests
```

---

## Data Flow

### Complete Request Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│              User starts scan (main_tool_loop)          │
│  - Collects domain, IP, scan mode, wordlist path        │
└────────────┬────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────┐
│           Input Validation (clean_and_validate_target)  │
│  - Checks if input is valid IP or domain               │
│  - Normalizes format                                    │
│  - Returns: (type, value, error_msg)                    │
└────────────┬────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────┐
│        Wordlist Loading (run_scan)                      │
│  - Opens wordlist file                                  │
│  - Strips whitespace from each line                     │
│  - Counts total entries for progress display            │
└────────────┬────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────┐
│      Task Submission (ThreadPoolExecutor)               │
│  - Creates 100 worker threads                           │
│  - Submits scan task for each wordlist entry            │
│  - Returns futures (handles to pending tasks)           │
└────────────┬────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────┐
│       Parallel Execution (scan_dns/vhost/page)          │
│  - Each thread makes HTTP request with 5-second timeout │
│  - Parses response status code                          │
│  - If status != 404, treats as "found"                  │
│  - Thread-safe: Updates progress_counter with lock      │
└────────────┬────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────┐
│        Result Collection (as_completed)                 │
│  - Collects return values from completed futures        │
│  - Builds list of found items                           │
│  - Handles KeyboardInterrupt gracefully                 │
└────────────┬────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────┐
│          Summary & Display (run_scan)                   │
│  - Prints total time elapsed                            │
│  - Lists all found items                                │
│  - Shows count of results                               │
└─────────────────────────────────────────────────────────┘
```

### HTTP Request Details

Each scan function makes requests like this:

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Host': url_to_test  # For vhost scans
}

response = requests.get(
    target_url,
    timeout=HTTP_TIMEOUT,  # 5 seconds
    headers=headers,
    allow_redirects=False  # Don't follow 301/302
)

status_code = response.status_code
# 200 = OK, 301 = Moved, 403 = Forbidden, 404 = Not Found, etc.
```

---

## Design Decisions

### Why ThreadPoolExecutor Instead of async/await?

**ThreadPoolExecutor**: 
- Easier to understand and debug
- Works well with blocking I/O (HTTP requests)
- Less boilerplate than async code
- Good enough for typical use cases

**async/await** (not used):
- More complex syntax
- Steeper learning curve
- Minimal performance benefit for this use case

**Decision**: ThreadPoolExecutor is pragmatic for a scanning tool

---

### Why Not Decrease Timeout to Speed Up Scans?

**Current**: 5 second timeout

**Tradeoff**:
| Timeout | Pro | Con |
|---------|-----|-----|
| 1 second | Fast | Misses slow/legitimate responses |
| 3 seconds | Faster | Some false negatives on slow networks |
| **5 seconds** | **Good balance** | **Moderate speed** |
| 10 seconds | No false negatives | Very slow on non-existent hosts |

**Decision**: 5 seconds is the right balance for most targets

---

### Why 100 Threads by Default?

**Testing shows**:
- 50 threads: Slower on most networks
- 100 threads: Good throughput, reasonable load
- 200 threads: Diminishing returns, rate-limiting likely
- 500+ threads: Often triggers WAF/rate limiting

**Decision**: 100 is optimal for typical targets

---

### Why Report All Non-404 Status Codes?

**Status codes reported**:
- 200 (OK) → Definitely found
- 301/302 (Redirect) → Likely found
- 403 (Forbidden) → Found but access denied
- 401 (Unauthorized) → Found but needs auth
- 500 (Server Error) → Unusual but found

**Why not filter to just 200?**
- 403 responses reveal protected areas (valuable intel)
- 301 redirects confirm existence
- Security researchers need to see the whole picture

---

## Performance Considerations

### Factors Affecting Speed

| Factor | Impact | Control |
|--------|--------|---------|
| Wordlist size | 5,000 words vs 50,000 words = 10x time | Choose appropriate list |
| Thread count | More threads = more speed (until rate limited) | Edit `MAX_THREADS` |
| Target response time | Slow server = slow scan | Can't control |
| Network bandwidth | Local network vs internet affects latency | Can't control |
| HTTP timeout | 5 sec vs 1 sec timeout = 5x faster on non-existent | Edit `HTTP_TIMEOUT` |
| Rate limiting | Target blocks scanner after N requests | Use smaller thread count |

### Benchmark Examples

**Test environment**: 4-core CPU, 100 Mbps internet, pro-combined.txt (50,000 entries)

| Scenario | Time | Notes |
|----------|------|-------|
| Fast target (1ms responses) | ~8 minutes | Limited by thread count and network |
| Medium target (50ms responses) | ~45 minutes | More realistic scenario |
| Slow target (500ms responses) | ~100+ minutes | Consider reducing thread count |
| Rate-limited target | Varies | Blocks after threshold, slows down |

### Optimization Tips

1. **Use smaller wordlist for quick reconnaissance**
   ```bash
   # Use small.txt instead of pro-combined.txt
   # Results in 5-10 minutes instead of 50+ minutes
   ```

2. **Reduce thread count if rate-limited**
   ```python
   MAX_THREADS = 10  # Instead of 100
   # Slower but won't trigger WAF
   ```

3. **Increase timeout for slow networks**
   ```python
   HTTP_TIMEOUT = 10  # Instead of 5
   # Takes longer per request but fewer false negatives
   ```

4. **Run overnight for large scans**
   ```bash
   # Just start the scan and let it run
   ```

---

## Error Handling

### Network Errors Handled

```python
try:
    response = requests.get(url, timeout=HTTP_TIMEOUT)
except requests.exceptions.ConnectionError:
    # Target server refused connection / network unreachable
    return None  # Skip this entry
except requests.exceptions.RequestException:
    # General request error (timeout, DNS error, etc)
    return None  # Skip this entry
except socket.timeout:
    # DNS lookup timed out
    return None  # Skip this entry
```

**Behavior**: 
- Errors are silently skipped (doesn't crash the scan)
- Progress continues with remaining entries
- User still sees overall results

### User Interruption

**Keyboard Interrupt (Ctrl+C)**:
```python
try:
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
except KeyboardInterrupt:
    print("[!] Scan interrupted by user. Stopping threads...")
    executor.shutdown(wait=False, cancel_futures=True)
```

**Behavior**: 
- Cancels remaining tasks
- Prints partial results
- Exits gracefully (no orphaned threads)

### Input Validation

```python
def clean_and_validate_target(raw_target):
    if not raw_target:
        return None, None, "Input cannot be empty."
    
    # Checks if input is valid IP
    if is_valid_ip(target):
        return 'ip', target, None
    
    # Checks if input is valid domain
    if '.' not in domain:
        return None, None, "Invalid domain format. Must contain a '.'"
    
    return 'domain', domain, None
```

---

## Security & Ethics

### What This Tool Does

✅ Discovers infrastructure through legitimate HTTP requests  
✅ Uses public wordlists of common subdomains/directories  
✅ Reports HTTP status codes from public endpoints  
✅ **Legal for authorized security testing**

### What This Tool Doesn't Do

❌ Exploit vulnerabilities  
❌ Bypass authentication  
❌ Modify server state  
❌ Access restricted data  
❌ Evade detection/WAF

### Legal Use

Always obtain written permission before scanning a target you don't own. Unauthorized scanning may violate:
- Computer Fraud and Abuse Act (CFAA) - USA
- Computer Misuse Act (CMA) - UK
- Computer Law Section 119 - Thailand
- Similar laws in most jurisdictions

---

**Last Updated**: March 2025
