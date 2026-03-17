import sqlite3
import os
import anthropic
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

# 1. SETUP
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

class AgentState(TypedDict):
    question: str
    sql: str
    results: str
    error: str
    attempts: int

client = anthropic.Anthropic(api_key=api_key)
DB_PATH = "Bikes.db"

# 2. NODES (The Logic)

def sql_writer(state: AgentState):
    """The SQL Specialist: Trained on the specific quirks of Bikes.db."""
    print(f"\n[NODE: WRITER] Drafting SQL for: {state['question']}")
    
    system_msg = """You are a Senior SQLite Expert for Jenson USA.
    
    CRITICAL DATABASE RULES:
    1. JOINING CUSTOMERS: The 'customer_id' column in 'customers' is NULL. Use 'c.ROWID = o.customer_id'.
    2. CURRENCY: 'list_price' is an integer (59999 = $599.99). ALWAYS use (CAST(list_price AS FLOAT) / 100.0).
    3. DISCOUNTS: 'discount' is an integer (2 = 2%). ALWAYS use (CAST(discount AS FLOAT) / 100.0).
    4. REVENUE FORMULA: (Price/100.0 * Quantity) * (1.0 - Discount/100.0).
    5. MEDIAN: SQLite doesn't have MEDIAN(). Use: ORDER BY col LIMIT 1 OFFSET (SELECT COUNT(*) FROM table) / 2.
    
    TABLES: customers, orders, order_items, products, categories, stores, staffs, stocks.
    
    Return ONLY raw SQL. No markdown, no backticks."""

    res = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=system_msg,
        messages=[{"role": "user", "content": state['question']}]
    )
    return {"sql": res.content[0].text.strip(), "attempts": state['attempts'] + 1}

def db_executor(state: AgentState):
    """The Database Engine: Executes and handles zero-result diagnostics."""
    print(f"[NODE: EXECUTOR] Querying {DB_PATH}...")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(state['sql'])
            rows = cur.fetchall()
            
            if not rows:
                return {"results": "EMPTY_RESULT", "error": "No data found for this query."}
            return {"results": str(rows), "error": ""}
    except Exception as e:
        return {"error": str(e)}

def business_analyst(state: AgentState):
    """The Analyst: Turns raw tuples into executive-level insights."""
    print("[NODE: ANALYST] Preparing report...")
    
    if "EMPTY_RESULT" in state['results']:
        return {"results": "⚠️ The query executed successfully, but no records matched your criteria."}

    system_msg = """You are a Senior Business Analyst. 
    Summarize the SQL results into a professional Markdown report.
    Use tables where appropriate. Format all currency as $0.00."""
    
    res = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system_msg,
        messages=[{"role": "user", "content": f"Question: {state['question']}\nData: {state['results']}"}]
    )
    return {"results": res.content[0].text.strip()}

# 3. GRAPH CONSTRUCTION
workflow = StateGraph(AgentState)

workflow.add_node("writer", sql_writer)
workflow.add_node("executor", db_executor)
workflow.add_node("analyst", business_analyst)

workflow.set_entry_point("writer")
workflow.add_edge("writer", "executor")

def router(state):
    if state["error"] and state["attempts"] < 2:
        return "writer" # Retry once on error
    return "analyst"

workflow.add_conditional_edges("executor", router)
workflow.add_edge("analyst", END)

app = workflow.compile()

# 4. INTERACTIVE INTERFACE
if __name__ == "__main__":
    print("\n" + "="*50)
    print("JENSON USA: AD-HOC AI ANALYTICS ENGINE")
    print("="*50)
    print("System Online. Ask about sales, inventory, or staff performance.")
    print("(Type 'exit' or 'quit' to stop)")

    while True:
        user_input = input("\n🔍 Query: ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("Shutting down... Goodbye!")
            break
            
        initial_state = {
            "question": user_input, 
            "attempts": 0, 
            "error": "", 
            "sql": "", 
            "results": ""
        }
        
        try:
            final_output = app.invoke(initial_state)
            print("\n" + "-"*30)
            print(final_output['results'])
            print("-"*30)
        except Exception as e:
            print(f"❌ Error: {e}")
