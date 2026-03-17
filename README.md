# 🚴 Jenson USA: Ad-Hoc AI Analytics Engine
### A Self-Healing Multi-Agent System built with LangGraph & Claude 3.5

This project is an **AI-powered Data Analyst** that allows users to ask complex business questions about the Jenson USA bicycle database in plain English. 

The system uses a **Multi-Agent Architecture** to translate natural language into SQL, execute it against a SQLite database, and transform raw data into executive-level reports.

---

## 🍳 The "Kitchen" Analogy: How it Works
To understand the technical complexity of this system, imagine a professional restaurant kitchen:

1.  **The Order (Input):** The user asks a question (e.g., *"What is the median price of our bikes?"*). This goes onto a **Shared Clipboard** (Agent State).
2.  **The Prep Chef (SQL Writer):** He reads the order and writes a recipe (**SQL Query**) on the clipboard. He is trained to handle "messy" ingredients like `null` IDs and integer-based currency.
3.  **The Cook (DB Executor):** He takes the recipe and tries to prepare the data.
    * **Success?** He puts the raw data on the clipboard.
    * **Mistake?** If he "burns" the data (SQL Error), he writes the error on the clipboard and sends it **BACK** to the Prep Chef to try again. This is the **LangGraph "Self-Healing" loop**.
4.  **The Server (Business Analyst):** Once the data is ready, the server takes the results and plates them beautifully into a **Markdown Report** for the customer.

---

## 🛠️ Technical Challenges Overcome

* **The "Ghost ID" Problem:** The `customer_id` column in the database was populated with `NULL` values. I implemented a **ROWID bridge** in the SQL logic to link orders to customers successfully.
* **Currency Scaling:** Prices were stored as raw integers (e.g., `59999` for `$599.99`). The agent was programmed to automatically apply `CAST(... AS FLOAT) / 100.0` to ensure financial accuracy.
* **Self-Correction Loop:** Using LangGraph's cyclic edges, the agent can catch its own SQL syntax errors and fix them in real-time without crashing the program.

---

## 🚀 Key Features
- **Natural Language to SQL:** Translates human questions into complex SQLite queries.
- **Advanced Analytics:** Handles Medians, Window Functions (Cumulative Sums), and `EXISTS` clauses.
- **State Management:** Uses a shared state to pass information between specialized agents.
- **Interactive CLI:** Users can query the database live through the terminal.

---

## 📊 Sample Queries Supported
- *"Find the product with the highest total sales for each category."*
- *"List all products that have never been ordered using an EXISTS clause."*
- *"Who are the top 5 VIP customers by total revenue?"*
- *"Calculate the cumulative sum of quantities sold for each product over time."*

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/vidhyachenji40-cmyk/ai-langgraph-sql-agent.git](https://github.com/vidhyachenji40-cmyk/ai-langgraph-sql-agent.git)
   cd ai-langgraph-sql-agent
