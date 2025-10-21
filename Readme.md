# Domain Scanner

A fast, multi-threaded subdomain scanner written in Python. Designed for ethical hacking reconnaissance, it features smart input parsing and flexible wordlist options.

**Creator:** https://github.com/Suryao07/

---
<img width="995" height="403" alt="Screenshot From 2025-10-22 00-44-38" src="https://github.com/user-attachments/assets/1ff13bf4-6bcb-4a04-8a85-5fc9ba5e2b3a" />




## Features

* **Multi-threaded:** Uses 100 threads by default for fast scanning.
* **Smart Input:** Accepts domains (`google.com`) or full URLs (`https://google.com/path`).
* **Progress Bar:** Shows scan progress every 100 attempts.![Uploading banner.png…]()

* **Flexible Wordlists:** Use your own custom path or the bundled default wordlists.

---

## Installation

Follow these steps to get the tool running.

### 1. Clone the Repository

First, download the tool and move into the new directory.
```bash
git clone [https://github.com/Suryao07/Domain-Scanner.git](https://github.com/Suryao07/Domain-Scanner.git)
cd Domain-Scanner
````

### 2\. Install Dependencies

The tool only requires the `requests` library.

```bash
pip3 install requests
```

### 3\. Make the Tool Executable

This is a critical step to make the script runnable.

```bash
chmod +x DomainScanner
```

### 4\. Download the Main Wordlist (IMPORTANT)

The tool's main wordlist (`pro.txt`) is too large for GitHub (26MB). You must download it manually.

  * **Download Link:** `https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/dns-Jhaddix.txt`

This command will download the file, **rename it to `pro.txt`**, and **paste it directly into your `wordlists` folder** where the tool expects it.

```bash
wget [https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/dns-Jhaddix.txt](https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/dns-Jhaddix.txt) -O wordlists/pro.txt
```

-----

## Usage

After installation, you can run the tool directly from your terminal:

```bash
./DomainScanner
```

### Wordlists

This tool is designed to work with the `wordlists/` directory.

  * **Default List (`pro.txt`):** After you download this list (see Installation step 4), you can use it by just pressing **Enter** at the wordlist prompt.
  * **Other Bundled Lists:** The repository includes these smaller lists you can use by typing their name:
      * `small.txt`
      * `medium.txt`
      * `large.txt`
      * `pro-combined.txt`

**Example (using the default `pro.txt`):**

```
[+] Enter domain (e.g., tryhackme.com): tryhackme.com
[+] Enter path or default wordlist name (default: pro.txt): 
[*] Starting scan...
```

**Example (using `small.txt`):**

```
[+] Enter domain (e.g., tryhackme.com): tryhackme.com
[+] Enter path or default wordlist name (default: pro.txt): small.txt
[*] Starting scan...
```

**Example (using a custom path):**

```
[+] Enter domain (e.g., tryhackme.com): tryhackme.com
[+] Enter path or default wordlist name (default: pro.txt): /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
[*] Starting scan...
```

-----

## Legal Disclaimer

**Warning:** This tool is for educational purposes only. Unauthorized scanning of domains may be illegal and unethical. Always obtain permission before scanning any domain.

```
```
