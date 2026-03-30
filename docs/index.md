# DomainScanner Documentation

Welcome to the DomainScanner documentation. This guide covers everything you need to understand, install, and extend the tool.

## 📚 Documentation Structure

### **For First-Time Users**
Start here to understand what DomainScanner does and how to get started.

- **[README.md](../Readme.md)** — Project overview, why it exists, features, quick start, examples
- **[Installation Guide](../Readme.md#installation)** — Step-by-step setup for all platforms

### **For Understanding How It Works**
Dig into the internals and design decisions.

- **[Architecture](./architecture.md)** — System design, threading model, scanning modes, data flow
- **[API Reference](./api.md)** — Complete function documentation, constants, examples, error handling

### **For Code Improvements & History**
Understand what was fixed and why.

- **[Improvements](./improvements.md)** — Bug fixes, enhancements, before/after comparisons

---

## 🎯 Quick Navigation by Use Case

### I want to scan for subdomains
→ Read [README.md - Example 1: Subdomain Enumeration](../Readme.md#example-1-subdomain-enumeration)

### I want to scan for virtual hosts
→ Read [README.md - Example 3: VHost Discovery](../Readme.md#example-3-vhost-discovery)

### I want to discover directories/files
→ Read [README.md - Example 2: Directory & Page Discovery](../Readme.md#example-2-directory--page-discovery)

### I want to understand the code
→ Read [Architecture](./architecture.md) + [API Reference](./api.md)

### I want to modify the tool
→ Read [API Reference - Extending the Tool](./api.md#extending-the-tool)

### I want to know what bugs were fixed
→ Read [Improvements](./improvements.md)

---

## 📖 Reading Paths by Audience

### Security Professional
1. README (full overview)
2. Architecture (how it scans, threading, performance)
3. API Reference (constants you can tune)
4. Try the examples

### Python Developer
1. README (features overview)
2. Architecture (design decisions)
3. API Reference (full function docs, error handling)
4. Read the source code (DomainScanner script)
5. Improvements (what was fixed)

### Penetration Tester
1. README (examples)
2. Wordlists explained
3. API Reference (constants - tune MAX_THREADS, HTTP_TIMEOUT)
4. Run scans against your test domains

### Student / Learning
1. README (what it does)
2. Architecture (how threading works, async patterns)
3. API Reference (function breakdown)
4. Read the source code line-by-line
5. Modify and extend it

---

## 🔗 Quick Reference

| Item | Location | Purpose |
|------|----------|---------|
| Install instructions | README | Get up and running |
| Usage examples | README | Real commands and output |
| System design | Architecture | How requests are sent in parallel |
| Function reference | API Reference | What each function does |
| Constants explained | API Reference | How to tune performance |
| Bug fixes | Improvements | What was patched and why |
| Wordlists | docs/index.md | Where to find lists of subdomains |
| Source code | DomainScanner | The actual implementation |

---

## 📊 Key Statistics

- **Functions documented**: 10+
- **Configuration constants**: 5 (tunable)
- **Scanning modes**: 3 (DNS, VHost, Page)
- **Default thread pool size**: 100 (configurable)
- **Supported Python**: 3.9+
- **External dependencies**: 1 (requests library)
- **Default wordlists included**: 5

---

## ❓ Common Questions

**Q: What's the difference between DNS, VHost, and Page scans?**
→ See [Architecture - Scanning Modes](./architecture.md#scanning-modes)

**Q: How do I tune performance?**
→ See [API Reference - Configuration](./api.md#constants--configuration)

**Q: Can I use my own wordlist?**
→ Yes. See [README - Wordlists](../Readme.md#wordlists)

**Q: What are the bugs that were fixed?**
→ See [Improvements - Issues Fixed](./improvements.md#issues-fixed)

**Q: How does the threading work?**
→ See [Architecture - Threading Model](./architecture.md#threading-model)

---

## 🛠 File Structure

```
DomainScanner/
├── Readme.md                    # Main documentation (start here!)
├── DomainScanner               # Main script (executable)
├── requirements.txt            # Python dependencies
├── wordlists/
│   ├── small.txt              # ~500 subdomains
│   ├── medium.txt             # ~5,000 subdomains
│   ├── large.txt              # ~20,000+ subdomains
│   ├── pro-combined.txt        # High-quality combined list
│   └── common_pages.txt        # Common directories/files
├── docs/
│   ├── index.md               # This file
│   ├── architecture.md        # System design
│   ├── api.md                 # Function reference
│   └── improvements.md        # Code fixes
└── LICENSE.txt                # MIT License
```

---

## 📝 License

DomainScanner is released under the MIT License. See [LICENSE.txt](../LICENSE.txt).

---

**Last Updated**: March 2025  
**Maintainer**: https://github.com/Suryao07/
