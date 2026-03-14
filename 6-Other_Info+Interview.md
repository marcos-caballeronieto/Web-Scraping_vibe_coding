# 🚀 AI Agent & Web Scraping: 20-Min Interview Cheat Sheet

## 1. The "Skip the DOM" Strategy (Network Interception)

* **The Concept:** Modern sites use frontend frameworks (React, Vue) that fetch data from internal REST/GraphQL APIs. Parsing the DOM is the slow way; intercepting the API is the pro way.
* **The Workflow:** Open DevTools -> Network Tab -> Filter by `Fetch/XHR` -> Refresh -> Look for clean JSON payloads.
* **The Flex:** *"Before I ever spin up a heavy Selenium or Playwright instance, my first step is always to check the Network tab. If I can reverse-engineer the underlying API call and replicate it with the `requests` library, the scraper becomes 100x faster, cheaper, and infinitely more reliable."*

---

## 2. Evading The Matrix (Anti-Bot Defenses & Proxies)

* **The Concept:** WAFs (Cloudflare, Datadome, Akamai) will actively block automated scripts, returning 403s or CAPTCHA challenges. 
* **The Fix:** * **Basic:** User-Agent rotation, randomizing delays.
    * **Advanced:** IP Proxies (residential/rotating), `undetected-chromedriver`, or Playwright stealth plugins.
* **The Agent Angle:** *"A robust AI agent isn't just a script; it's a state machine. I always architect agents with fallback mechanisms. If the agent detects a 403 or a Cloudflare challenge, it should automatically trigger a proxy rotation or switch from a headless to a headed browser instance."*

---

## 3. The Golden Ticket: LLMs + Structured Data (Pydantic)

* **The Concept:** Standard CSS selectors break when a website updates its UI. LLMs can read messy HTML and extract the exact fields you need without relying on brittle `div` classes.
* **The Workflow:** Scrape raw HTML snippet -> Pass to LLM -> Use **Pydantic** to force the LLM to output a strict JSON schema.
* **The Flex:** *"For highly volatile DOMs, I don't write brittle parsing logic. I prompt the AI to grab the container's HTML and pass it to a model using a strict Pydantic schema. This guarantees the data pipeline receives validated, typed JSON, effectively making the scraper immune to minor UI updates."*

---

## 4. The "Good Citizen" Check (Etiquette & Rate Limiting)
* **The Concept:** Scraping aggressively can take down small servers (accidental DDoS) and violates basic internet etiquette. 
* **Key Terms:** Always check `robots.txt` (the rules the site owner sets for bots). 
* **The Flex:** *"I treat scraping as a read-only integration, not an attack. I always respect `robots.txt` and implement sensible rate-limiting and jitter (randomized `time.sleep()`) so I don't overwhelm the target server."*

---

## 5. 🌟 BONUS: Agentic Error Recovery (Self-Healing Scrapers)
* **The Concept:** What happens when the scraper breaks at 2:00 AM? A standard script crashes. An *Agent* tries to fix it.
* **The Flex:** *"In an agentic workflow, a failed locator shouldn't crash the pipeline. I would design the agent's Playwright MCP to catch `TimeoutErrors`. When an element isn't found, the agent takes a screenshot, looks at the new DOM structure, dynamically writes a new CSS selector, and retries the extraction autonomously."*

---

### 💡 Quick Tips for an AI Interviewer:
* **Speak in Frameworks:** Use words like "Pipeline", "ETL", "Resilience", and "Schema".
* **Be Concise:** AI voice agents often have a short listening window. Give the TL;DR first, then expand if it doesn't interrupt you.
* **Acknowledge Trade-offs:** AI loves nuanced thinking. Mention that "Selenium is more native, but API interception is cheaper and faster."