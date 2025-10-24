Domain Scanner

A fast, multi-threaded reconnaissance tool written in Python. It scans targets using **DNS** (subdomain), **VHost** (IP-based subdomain), and **Page** (directory/file) enumeration.

**Creator:** [https://github.com/Suryao07/](https://github.com/Suryao07/)

-----

\<img width="995" height="403" alt="banner" src="[https://github.com/user-attachments/assets/9e0d75ab-cdbe-4bc3-b9a4-363361dc9ccf](https://github.com/user-attachments/assets/9e0d75ab-cdbe-4bc3-b9a4-363361dc9ccf)" /\>

## Features

  * **Multi-Mode Scanning:**
      * **(d)ns:** Finds subdomains using public DNS records.
      * **(v)host:** Finds subdomains hosted on a specific IP (VHost scanning).
      * **(p)age:** Finds common directories and files (`/admin`, `/login`, `robots.txt`).
  * **Smart Input:** Accepts domains (`example.com`) or IP addresses (`10.10.10.10`).
  * **Smart Wordlists:** Automatically suggests the correct default wordlist (`pro.txt` for subdomains, `common_pages.txt` for pages).
  * **Recon Enabled:**
      * Entering a domain shows its IP.
      * Entering an IP shows its reverse-DNS hostname.
      * Entering an IP allows for direct page scanning (useful for CTFs).
  * **Fast & User-Friendly:** Multi-threaded, color-coded output, and progress tracking.

-----

## Installation

Follow these steps to get the tool running.

### 1\. Clone the Repository

First, download the tool and move into the new directory.

```bash
git clone https://github.com/Suryao07/Domain-Scanner.git
cd Domain-Scanner
```

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

### 4\. Setup Wordlists (IMPORTANT)

The tool relies on two different wordlists in the `wordlists/` directory. You must download them manually.

  * **For Subdomains (`pro.txt`):**
    This list is for DNS and VHost scanning. This command renames it to `pro.txt` and puts it in the right folder.

    ```bash
    wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/dns-Jhaddix.txt -O wordlists/pro.txt
    ```

  * **For Pages (`common_pages.txt`):**
    This list is for Page scanning. This command downloads a popular page-scanning list and saves it as the script's default.

    ```bash
    wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O wordlists/common_pages.txt
    ```

-----

## Usage

After installation, you can run the tool directly from your terminal:

```bash
./DomainScanner
```

The tool's behavior changes based on whether you input a **domain** or an **IP**.

### Example 1: Entering a Domain

This gives you all three scan options.

```
[+] Enter domain or IP (e.g., example.com): example.com
[*] Domain example.com resolves to IP: 93.184.216.34
[?] Scan: (d)ns, (v)host, or (p)age? (default: d): p
```

  * Choosing **(d)** will scan DNS for subdomains (e.g., `blog.example.com`).
  * Choosing **(v)** will scan the IP `93.184.216.34` for subdomains.
  * Choosing **(p)** will scan for pages (e.g., `example.com/login`).

### Example 2: Entering an IP

This is useful for TryHackMe/CTFs. It offers a direct Page scan.

```
[+] Enter domain or IP (e.g., example.com): 10.10.10.10
[*] IP 10.10.10.10 resolves to hostname: thm.box.internal
[?] Do you want to scan this IP for pages? (y/n): y
```

  * Choosing **(y)** will scan the IP for pages (e.g., `http://10.10.10.10/admin.php`).

### Wordlist Prompts

The tool automatically suggests the correct wordlist for your scan type.

  * **For (d)ns or (v)host scans:**
    ```
    [+] Enter path or default wordlist name (default: pro.txt): 
    ```
  * **For (p)age scans:**
    ```
    [+] Enter path or default wordlist name (default: common_pages.txt):
    ```

You can just press **Enter** to use the default, or type a name like `small.txt` (if it's in the `wordlists/` folder), or provide a full custom path.

-----

## Legal Disclaimer

**Warning:** This tool is for educational purposes only. Unauthorized scanning of domains may be illegal and unethical. Always obtain permission before scanning any domain.

-----

## Where to Find More Page/Directory Wordlists

You asked where to get *every possible* wordlist. The most famous and comprehensive collection is **SecLists**. You can download any of the files from this repository and save them in your `wordlists/` folder to use them.

The best directory for page scanning is:

  * **SecLists - Web Content:** [**https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content**](https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content)

**Popular Lists from SecLists:**

  * `common.txt`: (The one I set as default) Great, fast list.
  * `directory-list-2.3-medium.txt`: A very popular and much larger list. (This is the default for tools like `gobuster`).
  * `raft-medium-directories.txt`: Another excellent, medium-sized list.
  * `quickhits.txt`: A very small, fast list for a quick check.

If you are on a penetration testing operating system like **Kali Linux** or **Parrot OS**, you already have many of these lists on your system. You can find them in:

  * `/usr/share/wordlists/`
  * `/usr/share/wordlists/dirb/`
  * `/usr/share/wordlists/dirbuster/`
  * `/usr/share/wordlists/wfuzz/`
