Cortes AySA

Automated checker for water service interruptions reported by AySA for a given client account number.

The script drives a real Chrome browser via Selenium, submits a client account number on AySA's public "Cortes de Servicio" page, and intercepts the underlying API response (aysaCuentaEnCorte) using Chrome DevTools Protocol (CDP) network logs - without relying on any unmaintained third-party proxy library.

How It Works


Launches a Chrome instance with network/performance logging enabled (goog:loggingPrefs).
Navigates to AySA's service interruption lookup page.
Fills in the client account number and submits the search form.
Waits for the page's internal API call to resolve, then reads Chrome's performance log to find the network request matching aysaCuentaEnCorte.
Retrieves the raw response body for that request directly from Chrome via Network.getResponseBody (CDP).
Parses the JSON response and writes the result to aysa_results.json.
Logs execution details (start, errors, completion) to cortes_aysa.log.


This approach avoids selenium-wire, which is unmaintained and frequently breaks due to outdated transitive dependencies (blinker, pkg_resources, bundled mitmproxy). Instead, it uses Selenium's native CDP support, which only depends on selenium itself.

Requirements


Python 3.10+
Google Chrome installed (the script currently expects it at C:\Program Files\Google\Chrome\Application\chrome.exe on Windows - adjust options.binary_location if your installation path differs, or remove that line to let Selenium auto-detect it)
Internet access on first run, so webdriver-manager can download a matching ChromeDriver build


Installation


Clone the repository:


bash   git clone <repo-url>
   cd cortes_aysa


Create and activate a virtual environment:


bash   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS / Linux


Install dependencies:


bash   pip install -r requirements.txt

Environment Setup (.env)

The script reads configuration from a .env file located at the project root.


Create a file literally named .env (not .env.txt - on Windows, double-check the real filename with Get-ChildItem -Force, since File Explorer often hides known extensions).
Add the following variable:


env   CLIENT_ID=1234

CLIENT_ID is the AySA account number the script will query.
Replace 1234 for your specific client number


The script loads this file automatically at startup via load_dotenv().

Usage

Run the script from the project root with the virtual environment activated:

bashpython cortes_aysa.py

Output:


aysa_results.json - the parsed JSON response from AySA's API for the configured account.
cortes_aysa.log - execution log (timestamps, errors, completion status).


Project Structure

cortes_aysa/
|-- cortes_aysa.py        # Main script
|-- requirements.txt      # Python dependencies
|-- .env                  # Local environment variables (not committed)
|-- cortes_aysa.log       # Generated execution log (created on execution)
|-- aysa_results.json     # Generated output (latest query result)
|-- README.md

Future Improvements

Implementation of results folder to persist different jsons timeframes to have a backup of each of the results.
Database persistence: instead of overwriting aysa_results.json on every run, store each query result in a database (e.g. PostgreSQL, SQLite) with a timestamp, to build a history of service interruptions per account over time.
Notifications: alert the user automatically when a cut is detected or resolved, via:

Email (e.g. SMTP, SendGrid, Amazon SES)
Push notification to a mobile app
SMS / WhatsApp message (e.g. Twilio)



Scheduled execution: run the check periodically (cron job, Windows Task Scheduler, or a cloud scheduler) instead of manually, to detect interruptions proactively.
Multi-account support: allow checking multiple CLIENT_ID values in a single run, reading them from the .env file, a config file, or the database.
Headless mode: run Chrome headless for server/CI environments where no visible browser window is needed or available.
Retry & resilience: add retries with backoff for transient network/page-load failures, and explicit waits (WebDriverWait) instead of fixed time.sleep() calls.
Containerization: package the script in a Docker image with Chrome and ChromeDriver pre-installed, for consistent deployment across environments.
Web dashboard: expose collected data through a simple web UI showing interruption history and current status per account.


Disclaimer

This project interacts with a public website not controlled by the author. AySA may change its page structure or API at any time, which could break the selectors or network interception logic used here. This tool is intended for personal/informational use only.