# 🚴 Jenson USA: Autonomous Marketing & Analytics Engine
## A Self-Healing Multi-Agent System built with LangGraph, Gemini 2.0 Flash & SQLite

This project is a high-performance **Autonomous AI Engine** that serves two major business functions: 
1. **AI Data Analyst:** Allows users to ask complex business questions about the [Jenson USA bicycle database](https://shell.cloud.google.com/?show=ide%2Cterminal) in plain English.
2. **Autonomous Marketing Engine:** Proactively identifies customers, analyzes demographics (**Age/Genre**), and generates personalized outreach using [Gemini 2.0 Flash](https://console.cloud.google.com/gen-app-builder/locations/global/engines/jenson-customer-assistant_1773803979636/preview/search?project=project-450e81d6-945c-48ed-b6e).

---

## 🍳 The "Kitchen" Analogy: How it Works
To understand the technical complexity of this system, imagine a professional restaurant kitchen:

1. **The Order (Input):** The user asks a question (e.g., *"What is the median price of our bikes?"*) or the system identifies "Pending" customers in the [Bikes.db](https://shell.cloud.google.com/?show=ide%2Cterminal).
2. **The Prep Chef (SQL Writer):** Reads the requirements and writes a recipe (**SQL Query**). He is trained to handle "messy" ingredients like null IDs and integer-based currency.
3. **The Cook (DB Executor):** Takes the recipe and tries to prepare the data.
   - **Success?** He puts the raw data on the clipboard.
   - **Mistake?** If he "burns" the data (SQL Error), he sends it **BACK** to the Prep Chef to try again. This is the **LangGraph "Self-Healing" loop**.
4. **The Server (Business Analyst/Marketer):** Once the data is ready, the server either plates a Markdown Report or uses AI to craft a personalized email and logs the result in [campaign_summary.csv](https://shell.cloud.google.com/?show=ide%2Cterminal).

---

## 🛠️ Technical Challenges Overcome
* **The "Ghost ID" Problem:** The `customer_id` column was populated with NULL values. I implemented a **ROWID bridge** in the SQL logic to link orders to customers successfully.
* **Currency Scaling:** Prices were stored as raw integers (e.g., `59999` for `$599.99`). The agent automatically applies `CAST(... AS FLOAT) / 100.0` to ensure financial accuracy.
* **Self-Correction Loop:** Using LangGraph's cyclic edges, the agent catches its own SQL syntax errors and fixes them in real-time without crashing.

---

## 🚀 Phase 2: Autonomous Marketing Expansion
The system now synchronizes with the [jenson-customer-data-store](https://console.cloud.google.com/gen-app-builder/locations/global/engines/jenson-customer-assistant_1773803979636/data/schema?project=project-450e81d6-945c-48ed-b6e).

### 🧠 "Genre-Aware" Intelligence
The agent uses **Genre** and **Age** fields for high-level personalization:
* **Dynamic Tone Mapping:** Automatically switches between "High-Energy" (youth/adrenaline) and "Professional" (senior/comfort).
* **Targeted Content:** Uses AI to suggest specific bike categories and local trails based on the [Customer Schema](https://console.cloud.google.com/gen-app-builder/locations/global/engines/jenson-customer-assistant_1773803979636/data/schema?project=project-450e81d6-945c-48ed-b6e).

### 🛠️ Operational Files
* **`deploy_agent.py`:** A production wrapper that polls the database every 60 seconds for new "pending" customers.
* **`marketing_agent2.py`:** The advanced LangGraph state machine handling customer processing.
* **`campaign_summary.csv`:** A live-updating analytics dashboard of all AI actions.

---

## 📊 Sample Capabilities
* **Analytics:** *"Who are the top 5 VIP customers by total revenue?"*
* **Marketing:** Identifying a **25-year-old Female** and generating a high-energy email about mountain biking trails.
* **Marketing:** Identifying a **60-year-old Male** and generating a professional invitation for a scenic tour.

---

## ⚙️ Installation & Setup
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/vidhyachenji40-cmyk/ai-langgraph-sql-agent.git](https://github.com/vidhyachenji40-cmyk/ai-langgraph-sql-agent.git)
   cd ai-langgraph-sql-agent
