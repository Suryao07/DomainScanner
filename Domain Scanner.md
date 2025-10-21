# Domain Scanner

A simple, fast, multi-threaded subdomain scanner written in Python.

**Creator:** https://github.com/Suryao07/

![Banner of Domain Scanner Tool](https://user-images.githubusercontent.com/YOUR_USER_ID/YOUR_IMAGE_ID) 
*(**Note:** You'll need to run the tool, take a screenshot of the banner, and upload it here)*

---

## Features

* **Multi-threaded:** Uses 100 threads by default for fast scanning.
* **Smart Input:** Accepts domains (`google.com`) or full URLs (`https://google.com/path`).
* **Progress Bar:** Shows scan progress every 100 attempts.
* **Flexible Wordlists:** Use your own custom path or bundled default wordlists.

## Installation

This tool works best on Linux (like Kali, Parrot, or Ubuntu).

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Suryao07/Your-Repo-Name.git](https://github.com/Suryao07/Your-Repo-Name.git)
    cd Your-Repo-Name
    ```

2.  **Install dependencies:**
    (It only requires the `requests` library)
    ```bash
    pip3 install requests
    ```

3.  **Make the tool executable:**
    This is the most important step!
    ```bash
    chmod +x DomainScanner
    ```

## Usage

You can now run the tool directly from your terminal.

```bash
./DomainScanner

Wordlists

This tool comes with a wordlists/ directory. You can use any of these by just typing their name.

    small.txt (Fastest scan)

    medium.txt (Balanced scan)

    large.txt (Large scan)

    pro.txt (Professional list - Recommended Default)

    pro-combined.txt (Combined professional list)

Example (using default pro.txt):

[+] Enter domain (e.g., tryhackme.com): tryhackme.com
[+] Enter path or default wordlist name (default: pro.txt): 
[*] Starting scan...

Example (using small.txt):

[+] Enter domain (e.g., tryhackme.com): tryhackme.com
[+] Enter path or default wordlist name (default: pro.txt): small.txt
[*] Starting scan...

Example (using your own custom path):

[+] Enter domain (e.g., tryhackme.com): tryhackme.com
[+] Enter path or default wordlist name (default: pro.txt): /usr/share/seclists/Discovery/DNS/dns-Jhaddix.txt
[*] Starting scan...

Legal Disclaimer

Warning: This tool is for educational purposes only. Unauthorized scanning of domains may be illegal and unethical. Always obtain permission before scanning any domain.
