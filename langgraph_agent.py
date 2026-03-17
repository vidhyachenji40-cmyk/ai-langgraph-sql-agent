import sqlite3
import os
import anthropic
from typing import TypedDict
from langgraph.graph import StateGraph, END

# 1. STATE DEFINITION
class AgentState(TypedDict):
    question: str
    sql: str
    results: str
    error: str
    attempts: int

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
DB_PATH = "Bikes.db"

# 2. NODES
def sql_writer(state: AgentState):
    print(f"\n[NODE: WRITER] Generating SQL... (Attempt {state['attempts'] + 1})")
    
    # If there's an error, we provide the failing SQL and the error message only.
    # We do NOT provide hints; the LLM must find the mistake itself.
    system_msg = "You are a SQLite expert. Provide ONLY the raw SQL query. No markdown, no explanation."
    
    user_msg = f"Database Schema: products, categories, stocks, stores, order_items, orders, customers, staffs, brands.\n\nQuestion: {state['question']}"
    
    if state['error']:
        user_msg += f"\n\nYour previous SQL failed: {state['sql']}\nSQLite Error: {state['error']}\nAnalyze the error and provide the corrected SQL."

    res = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=system_msg,
        messages=[{"role": "user", "content": user_msg}]
    )
    return {"sql": res.content[0].text.strip(), "attempts": state['attempts'] + 1}

def db_executor(state: AgentState):
    print("[NODE: EXECUTOR] Testing SQL...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(state['sql'])
        rows = cur.fetchall()
        # Grab column names for context
        cols = [description[0] for description in cur.description]
        conn.close()
        return {"results": f"Columns: {cols}\nRows: {rows}", "error": ""}
    except Exception as e:
        print(f"!! ERROR ENCOUNTERED: {e}")
        return {"error": str(e)}

def presenter(state: AgentState):
    print("[NODE: PRESENTER] Returning result.")
    if state['error']:
        return {"results": f"FAILED after {state['attempts']} attempts. Last error: {state['error']}"}
    return {"results": state['results']}

# 3. GRAPH CONSTRUCTION
workflow = StateGraph(AgentState)

workflow.add_node("writer", sql_writer)
workflow.add_node("executor", db_executor)
workflow.add_node("presenter", presenter)

workflow.set_entry_point("writer")
workflow.add_edge("writer", "executor")

def decide_next_step(state: AgentState):
    if state["error"] and state["attempts"] < 5: # It has 5 tries to fix itself
        return "writer"
    return "presenter"

workflow.add_conditional_edges("executor", decide_next_step)
workflow.add_edge("presenter", END)

app = workflow.compile()

# 4. RUN
if __name__ == "__main__":
    print("\n--- SELF-HEALING BIKE AGENT ---")
    while True:
        user_q = input("\nAsk a question (or 'exit'): ")
        if user_q.lower() == 'exit': break
        
        inputs = {"question": user_q, "attempts": 0, "error": "", "sql": "", "results": ""}
        final_state = app.invoke(inputs)
        print(f"\nFINAL RESULT:\n{final_state['results']}")