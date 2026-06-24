# Lead Scout Test Plan

This document outlines a structured test plan for the Lead Scout multi-agent pipeline. It consists of 5 test cases designed to evaluate the boundaries, robustness, and adaptation capabilities of the `researcher_agent`, `writer_agent`, and `saver_agent`.

---

## Pipeline Test Cases

### 1. High-Profile Tech Giant: **OpenAI**
* **Company Type**: High search volume, extremely rapid news cycle, tech-focused.
* **What it checks**:
  * **Researcher Agent**: Tests if the agent can parse through a massive volume of real-time search results to extract the most *current* and *relevant* B2B news, rather than getting bogged down in consumer-facing drama or stale information.
  * **Writer Agent**: Tests if the agent can draft a highly specific email highlighting relevant enterprise pain points (e.g., API reliability, safety, compute scale) without resorting to generic templates or getting overwhelmed by the sheer amount of data.
* **Why it matters**: Large companies have high noise-to-signal ratios in search results. Verifying that the Researcher retrieves current business announcements (e.g., new model releases, enterprise partnerships) and the Writer avoids generalities ensures Lead Scout remains useful for high-profile accounts.

### 2. Highly Ambiguous / Common Name: **Target**
* **Company Type**: Common word, multiple entities (retail giant Target Corp vs. general targets/goals vs. other target-named companies).
* **What it checks**:
  * **Researcher Agent**: Evaluates how the agent constructs search queries and handles ambiguity. Does it correctly identify the retail giant "Target" (or specify if it needs clarification), or does it merge search results of unrelated companies?
  * **Writer Agent**: Checks if the email is coherent. If the Researcher fails and returns mixed data (e.g., mixing a local boutique named "Target" with Target Corp), the email will likely be a confusing hallucination.
* **Why it matters**: Many B2B prospects have common nouns as company names (e.g., *Apex*, *Bloom*, *Target*). Understanding how the pipeline handles ambiguous search terms identifies whether additional guardrails (e.g., requiring a website domain alongside the company name) are necessary.

### 3. Stealth/Early-Stage Startup: **Cognition Labs** (or a local niche business)
* **Company Type**: Low digital footprint, minimal news, sparse search results.
* **What it checks**:
  * **Researcher Agent**: Verifies if the agent adheres to its instructions: *"If search results are thin, say so honestly rather than guessing. If nothing notable, say 'No major recent news found.'"*
  * **Writer Agent**: Tests if the agent can write a compelling, simple outreach email focusing purely on the company's core mission (`WHAT THEY DO`), without inventing or hallucinating fake news to fill in the blanks.
* **Why it matters**: Hallucinations are a major risk for sales agents. If a company has no news, the pipeline must fail gracefully (honestly reporting thin search results) rather than generating fake funding rounds or fake product launches.

### 4. Non-English / International Enterprise: **ASML**
* **Company Type**: Large European semiconductor manufacturer, operations globally, source materials/news often in Dutch or non-US contexts.
* **What it checks**:
  * **Researcher Agent**: Checks if the agent can successfully retrieve, translate, and synthesize non-English or highly specialized international news sources and produce a clean English briefing.
  * **Writer Agent**: Tests if the writer agent can frame the email respecting the regional/industry context (e.g., global supply chain issues) rather than defaulting to US-centric business assumptions.
* **Why it matters**: B2B sales are global. Ensuring the search and translation capabilities work smoothly allows sales reps to target international prospects without manual translation prep.

### 5. Traditional Brick-and-Mortar: **Caterpillar Inc.**
* **Company Type**: Heavy machinery, manufacturing, non-tech industry.
* **What it checks**:
  * **Researcher Agent**: Assesses if the agent can correctly identify industrial pain points (e.g., manufacturing efficiency, supply chain bottlenecks, dealer network management) instead of software-centric ones.
  * **Writer Agent**: Evaluates if the agent's pitch remains general and industry-appropriate (*"stay general... since you don't know what the sender actually sells"*), avoiding software/SaaS clichés like "automating your digital workflows" when pitching heavy machinery.
* **Why it matters**: A major weakness of generic LLM writers is defaulting to tech/SaaS jargon. This test ensures the Writer agent can adapt its tone and pitch to traditional industries, making the outreach sound natural and human.
