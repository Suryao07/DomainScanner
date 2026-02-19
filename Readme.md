# DomainScanner 🕵️‍♂️
 
![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
 
A lightweight, efficient Python-based tool for web reconnaissance. `DomainScanner` automates the discovery of subdomains and hidden directories/files, which are critical first steps in any web application security assessment (VAPT).
 
This project was built to apply and demonstrate my skills in Python programming and my understanding of ethical hacking principles, specifically information gathering and enumeration.
 
---
<img width="995" height="403" alt="Screenshot From 2025-10-22 00-44-38" src="https://github.com/user-attachments/assets/c8c6ff86-0878-493f-8dd4-2a11b3bb162b" />
 
## 🎥 Live Demo
 
A recruiter's time is valuable. This 15-second demo shows the tool's core functionality in action.
 
**[CRITICAL: You MUST create a short GIF of your tool running and put it here. Use a free tool like GIPHY Capture, licecap, or ezgif.com to record your terminal. This is the single most important part of your README.]**
 
![Demo GIF of DomainScanner](https://your-link-to-a-demo-gif.gif)
 
---
 
## 📖 Table of Contents
 
* [About The Project](#-about-the-project)
* [Key Features](#-key-features)
* [How It Works](#-how-it-works)
* [Getting Started](#-getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage Examples](#-usage-examples)
  * [Scanning for Subdomains](#example-1-subdomain-scanning)
  * [Scanning for Directories/Pages](#example-2-directory--page-scanning)
* [Project Roadmap](#-project-roadmap)
* [License](#-license)
* [Author](#-author)
 
---
 
## 🎯 About The Project
 
As a cybersecurity student, I've used many industry-standard tools like DirBuster, GoBuster, and FFUF. While powerful, I wanted to build my own enumeration tool from scratch to gain a deeper understanding of *how* they work.
 
This project forced me to solve several key challenges:
* How to efficiently handle HTTP requests in Python.
* How to parse and manage wordlists of varying sizes.
* How to handle different HTTP response codes (200, 301, 403, 404).
* How to design a clean and usable Command-Line Interface (CLI).
 
This tool is the direct application of my Python programming skills to solve a real-world cybersecurity problem: **discovering a target's attack surface.**
 
---
 
## ✨ Key Features
 
* **Three Scan Modes:** DNS subdomain enumeration, Virtual Host (VHost) discovery, and page/directory brute-forcing.
* **CLI & Interactive Modes:** Provide a `-d` flag for fully scripted, non-interactive scans or run without flags for the guided interactive mode.
* **HTTPS Support:** Use `--https` to scan targets over HTTPS instead of HTTP.
* **Save Results to File:** Use `-o results.txt` to automatically save all found items to a file.
* **Status Code Filtering:** Use `--exclude-codes` to control which HTTP status codes are treated as "not found" (default: 404).
* **Wildcard DNS Detection:** Automatically detects wildcard DNS before subdomain/VHost scans to warn about potential false positives.
* **Configurable Threads & Timeout:** Tune performance with `--threads` and `--timeout`.
* **Wordlist Flexibility:** Natively supports custom wordlists. Several common lists are included in the `/wordlists` directory.
* **Connection Pooling:** Uses `requests.Session` for efficient HTTP connection reuse across all threads.
* **Lightweight & Portable:** Written in pure Python with minimal dependencies, making it fast and easy to run anywhere.
 
---
 
## ⚙️ How It Works
 
The tool operates in one of two modes:
 
1.  **Subdomain Mode (`--mode subdomain`):**
    * It takes a base domain (e.g., `example.com`).
    * It iterates through each word in the provided wordlist (e.g., `admin`, `dev`, `api`).
    * It prepends the word to the base domain (e.g., `admin.example.com`).
    * It attempts to make an HTTP request to that new URL.
    * If it receives a valid response (like a 200 OK status code), it reports the subdomain as "Found."
 
2.  **Directory Mode (`--mode directory`):**
    * It takes a full domain URL (e.g., `http://example.com`).
    * It iterates through each word in the wordlist (e.g., `admin.php`, `login`, `.git`).
    * It appends the word to the base URL (e.g., `http://example.com/admin.php`).
    * It sends an HTTP request and reports the status code. This can reveal hidden login pages (200), forbidden areas (403), or redirected pages (301).
 
---
 
## 🚀 Getting Started
 
Follow these simple steps to get a local copy up and running.
 
### Prerequisites
 
* Python 3.9 or newer
* `pip` (Python package installer)
 
### Installation
 
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Suryao07/domainscanner.git](https://github.com/Suryao07/domainscanner.git)
    cd domainscanner
    ```
 
2.  **Create a Python virtual environment (Recommended):**
    This isolates the project's dependencies from your system.
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
 
3.  **Install required dependencies:**
    *(You MUST create a file named `requirements.txt` and add the line `requests` to it, as your script needs it to run.)*
    ```bash
    pip install -r requirements.txt
    ```
 
---
 
## 💻 Usage Examples
 
All commands are run from within the `domainscanner` directory.
 
### Help Menu
To see all available commands and options, use the `-h` or `--help` flag.
```bash
python DomainScanner --help
```

### Interactive Mode
Run without any arguments to enter the guided interactive mode:
```bash
python DomainScanner
```

### Example 1: DNS Subdomain Scanning (CLI)
```bash
python DomainScanner -d example.com -m dns -w wordlists/small.txt
```

### Example 2: Directory & Page Scanning with Output File
```bash
python DomainScanner -d example.com -m page -o results.txt
```

### Example 3: HTTPS VHost Scan with Custom Threads & Timeout
```bash
python DomainScanner -d example.com -m vhost --https --threads 50 --timeout 10
```

### Example 4: Subdomain Scan Excluding Multiple Status Codes
```bash
# Exclude both 404 and 403 responses
python DomainScanner -d example.com -m dns --exclude-codes 404,403
```

### Example 5: Skip Wildcard DNS Detection
```bash
python DomainScanner -d example.com -m dns --no-wildcard
```

### All CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `-d`, `--domain` | Target domain or IP | — |
| `-m`, `--mode` | `dns`, `vhost`, or `page` | `dns` |
| `-w`, `--wordlist` | Path to wordlist file | Built-in default |
| `-o`, `--output` | Save results to file | — |
| `--threads` | Number of concurrent threads | 100 |
| `--timeout` | HTTP request timeout (seconds) | 5 |
| `--https` | Use HTTPS instead of HTTP | HTTP |
| `--exclude-codes` | Comma-separated status codes to exclude | 404 |
| `--no-wildcard` | Skip wildcard DNS detection | Enabled |

---

## 🗺️ Project Roadmap
This tool continues to evolve. Here are features added and planned:

- [x] **Multi-threading:** Uses `concurrent.futures.ThreadPoolExecutor` for fast parallel scanning.
- [x] **Colorized Output:** Terminal colors for clear, actionable output.
- [x] **Save to File:** `-o`/`--output` flag saves all found results to a report file.
- [x] **Status Code Filtering:** `--exclude-codes` lets you filter any status codes from results.
- [x] **CLI Argument Support:** Full `argparse`-based CLI for non-interactive/scripted usage.
- [x] **HTTPS Support:** `--https` flag for scanning HTTPS targets.
- [x] **Wildcard DNS Detection:** Automatically warns when wildcard DNS is detected.
- [x] **Connection Pooling:** Uses `requests.Session` for efficient connection reuse.
- [x] **Configurable Threads & Timeout:** `--threads` and `--timeout` flags.
- [x] **IP Octet Validation:** Properly validates IP addresses (0–255 per octet).
- [ ] **Recursive Scanning:** Scan for directories within found directories.
- [ ] **Resume Scan:** Save and resume interrupted scans.

---

## ⚖️ License
This project is distributed under the MIT License. See the LICENSE file for more information.

## 👤 Author
**Surya Pratap Singh**

* GitHub: [Suryao07](https://github.com/Suryao07)
* LinkedIn: [surya-pratap-singh](https://www.linkedin.com/in/surya-pratap-singh-61a41130a)

Feel free to reach out with any questions or suggestions!
