import sqlite3
import os
import anthropic
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

# 1. LOAD SECRETS
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

# 3. NODES
def sql_writer(state: AgentState):
    print(f"\n[NODE: WRITER] Generating Revenue-Corrected SQL...")
    
    # DIVIDE BY 100.0: Corrects '59999' to '599.99' and '2' to '0.02'
    sql = """
    SELECT 
        c.first_name, 
        c.last_name, 
        SUM(
            (CAST(i.list_price AS FLOAT) / 100.0) * CAST(i.quantity AS FLOAT) * (1.0 - (CAST(i.discount AS FLOAT) / 100.0))
        ) as total_spent
    FROM customers c
    JOIN orders o ON c.ROWID = o.customer_id
    JOIN order_items i ON o.order_id = i.order_id
    GROUP BY c.ROWID
    ORDER BY total_spent DESC
    LIMIT 5;
    """
    return {"sql": sql, "attempts": state['attempts'] + 1}

def db_executor(state: AgentState):
    print(f"[NODE: EXECUTOR] Running SQL on {DB_PATH}...")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(state['sql'])
            rows = cur.fetchall()
            
            print(f"[DEBUG] Rows found: {len(rows)}")
            if rows:
                print(f"[DEBUG] Top Result: {rows[0][0]} {rows[0][1]} - ${rows[0][2]:.2f}")
            
            if not rows:
                return {"results": "EMPTY_RESULT", "error": ""}
            return {"results": str(rows), "error": ""}
    except Exception as e:
        return {"error": str(e)}

def business_analyst(state: AgentState):
    print(f"[NODE: ANALYST] Finalizing Executive Report (Claude Sonnet 4.6)...")
    
    if "EMPTY_RESULT" in state['results']:
        return {"results": "## ❌ Data Integrity Error\nCould not calculate revenue. Verify order_items table contents."}
    
    system_msg = """You are a Senior Business Analyst at Jenson USA. 
    Present this VIP customer data in a beautiful Markdown table. 
    Format currency with dollar signs and two decimal places.
    Add a brief 'Strategic Insight' section at the end."""
    
    res = client.messages.create(
        model="claude-sonnet-4-6", 
        max_tokens=1000,
        system=system_msg,
        messages=[{"role": "user", "content": f"Customer Revenue Data: {state['results']}"}]
    )
    return {"results": res.content[0].text.strip()}

# 4. GRAPH CONSTRUCTION
workflow = StateGraph(AgentState)

workflow.add_node("writer", sql_writer)
workflow.add_node("executor", db_executor)
workflow.add_node("analyst", business_analyst)

workflow.set_entry_point("writer")
workflow.add_edge("writer", "executor")

def router(state):
    if state["error"] and state["attempts"] < 2:
        return "writer"
    return "analyst"

workflow.add_conditional_edges("executor", router)
workflow.add_edge("analyst", END)

app = workflow.compile()

# 5. EXECUTION
if __name__ == "__main__":
    print("\n--- JENSON USA INTELLIGENCE DASHBOARD ---")
    inputs = {"question": "Top 5 VIPs by Revenue", "attempts": 0, "error": "", "sql": "", "results": ""}
    final_state = app.invoke(inputs)
    print(f"\n{final_state['results']}")