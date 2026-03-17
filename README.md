# AI LangGraph SQL Agent

This project uses **LangGraph** and **Anthropic Claude 3.5 Sonnet** to create an intelligent SQL agent that can query a SQLite database (`Bikes.db`) using natural language.

## 🤖 How the Agent Works

Unlike traditional AI scripts, this agent uses a **StateGraph** to handle complex reasoning.

### **The Logic Flow:**
1.  **Input:** User asks a question (e.g., "Which store has the most stock?").
2.  **SQL Writer Node:** The LLM analyzes the schema and generates a raw SQLite query.
3.  **Execution Node:** The agent runs the query against the database.
4.  **Self-Correction Loop:** * If the SQL fails (e.g., a typo in a column name), the agent captures the error, sends it back to the LLM, and **retries automatically**.
5.  **Output:** The agent delivers a clean, human-readable answer.

## 🚀 Example Usage

**User Question:** > "What are the top 3 most expensive products?"

**Agent Internal SQL:**
```sql
SELECT product_name, list_price 
FROM products 
ORDER BY list_price DESC 
LIMIT 3;
