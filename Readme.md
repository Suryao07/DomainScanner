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
 
* **Dual-Mode Scanning:** Can be switched to scan for **subdomains** or **directories** with a simple flag.
* **Wordlist Flexibility:** Natively supports the use of any custom wordlist. Several common lists are already included in the `/wordlists` directory.
* **Simple & Clean Output:** Provides clear, actionable output, showing exactly what was found (Status 200) and what was not (Status 404).
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
python domainscanner.py --help
Example 1: Subdomain Scanning
This command scans example.com for subdomains using the included small.txt wordlist.

Bash

python domainscanner.py --mode subdomain --domain example.com --wordlist wordlists/small.txt
Sample Output:

=========================================
      DomainScanner | Subdomain Mode
=========================================
[+] Target Domain: example.com
[+] Wordlist: wordlists/small.txt
...
[+] FOUND (200): [www.example.com](https://www.example.com)
[+] FOUND (200): blog.example.com
[-] NOT FOUND (404): dev.example.com
[-] NOT FOUND (404): test.example.com
...
[+] Scan Complete.
Example 2: Directory & Page Scanning
This command scans http://example.com for hidden directories and pages using the common_pages.txt wordlist.

Bash

python domainscanner.py --mode directory --domain [http://example.com](http://example.com) --wordlist wordlists/common_pages.txt
Sample Output:

=========================================
     DomainScanner | Directory Mode
=========================================
[+] Target URL: [http://example.com](http://example.com)
[+] Wordlist: wordlists/common_pages.txt
...
[+] FOUND (200): [http://example.com/admin](http://example.com/admin)
[+] FOUND (200): [http://example.com/login.html](http://example.com/login.html)
[+] FORBIDDEN (403): [http://example.com/.git](http://example.com/.git)
[-] NOT FOUND (404): [http://example.com/config.php](http://example.com/config.php)
...
[+] Scan Complete.
🗺️ Project Roadmap
This tool is a solid foundation, but I plan to add more advanced features to improve its performance and capabilities. This demonstrates my commitment to continuous learning and improving my code.

[ ] Multi-threading: Implement threading (concurrent.futures) to send multiple requests at once, drastically increasing scan speed.

[ ] Colorized Output: Add colorama or termcolor to make results more readable (e.g., Green for 200, Yellow for 403, Red for 404).

[ ] Save to File: Add a -o or --output flag to save all "Found" results to a .txt report.

[ ] Status Code Filtering: Add flags like --hide-404 or --show-403 to let the user filter the noise.

[ ] Recursive Scanning: Add an option to scan for directories within found directories.

[Details] Improved Error Handling: Add more robust handling for connection timeouts, SSL certificate errors, and invalid domains.

⚖️ License
This project is distributed under the MIT License. See the LICENSE file for more information.

👤 Author
Surya Pratap Singh

GitHub: Suryao07

LinkedIn: www.linkedin.com/in/surya-pratap-singh-61a41130a

Feel free to reach out with any questions or suggestions!
