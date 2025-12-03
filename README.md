# Embedded QA Automation Framework (Python + Jenkins)

This project is a demo automation framework for an Embedded / Firmware QA or SDET role.

It includes:
- REST API tests (Python + requests)
- CoAP API tests (Python + aiocoap)
- UI tests (Python + Selenium)
- Embedded device simulation via TCP echo server
- Networking tests for TCP/UDP
- SSL/TLS certificate validation tests
- Jenkins CI pipeline with stages for each test type

Run locally:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
