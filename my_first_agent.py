import sqlite3
import anthropic
import os

# 1. SETUP - Pulls key safely from your terminal environment
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
DB_PATH = "Bikes.db"

def get_sql_from_ai(question):
    """Asks Claude to write the SQL for us based on the DB schema."""
    prompt = f"""
    You are a SQLite expert. Given the following schema, write ONLY the SQL query to answer the question.
    Do not explain the code. Do not use markdown backticks.
    
    Schema:
    - products (product_id, product_name, brand_id, category_id, model_year, list_price)
    - categories (category_id, category_name)
    - stocks (store_id, product_id, quantity)
    - stores (store_id, store_name)
    - order_items (order_id, item_id, product_id, quantity, list_price, discount)
    - orders (order_id, customer_id, order_status, order_date, required_date, shipped_date, store_id, staff_id)
    - customers (customer_id, first_name, last_name, phone, email, street, city, state, zip_code)
    - staffs (staff_id, first_name, last_name, email, phone, active, store_id, manager_id)
    - brands (brand_id, brand_name)

    Question: {question}
    SQL Query:"""
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def run_query(sql):
    """Executes the SQL and returns results."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        # Get column names for better readability
        columns = [description[0] for description in cursor.description]
        conn.close()
        return columns, results
    except Exception as e:
        return None, f"Error: {e}"

# 2. INTERACTIVE TERMINAL LOOP
print("\n" + "="*40)
print("--- BIKE DATABASE ASSISTANT READY ---")
print("="*40)
print("Type 'exit' to quit.")

while True:
    user_question = input("\nAsk a question: ")
    
    if user_question.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break
    
    if not user_question.strip():
        continue

    print("Thinking...")
    sql = get_sql_from_ai(user_question)
    
    # Clean SQL just in case Claude adds backticks
    sql = sql.replace("```sql", "").replace("```", "").strip()
    
    print(f"\n[SQL GENERATED]: {sql}")
    
    cols, data = run_query(sql)
    
    print("\n[RESULT]:")
    if cols is None:
        print(data) # This prints the error message
    elif not data:
        print("No records found in the database for this query.")
    else:
        # Print column headers
        print(" | ".join(cols))
        print("-" * 50)
        for row in data:
            print(row)