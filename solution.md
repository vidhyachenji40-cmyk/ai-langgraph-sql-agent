# 🛠️ Technical Deep-Dive: Jenson USA Database Fixes

This agent doesn't just write SQL; it solves specific data integrity issues found in the `Bikes.db` source.

### 1. The ROWID Bridge
**Problem:** The `customer_id` column in the `customers` table was `NULL`.
**Solution:** I utilized the SQLite `ROWID` as the primary key to successfully join customers to their orders.

### 2. Scaled Currency Logic
**Problem:** Prices were stored as integers (e.g., 59999).
**Solution:** The agent automatically injects `CAST(list_price AS FLOAT) / 100.0` into every query to provide accurate dollar amounts.

### 3. Self-Correction (The LangGraph Advantage)
**Problem:** LLMs sometimes hallucinate SQL syntax or table names.
**Solution:** If the database returns an error, the system routes the error back to the LLM. It analyzes the error message and fixes its own code before the user sees it.
