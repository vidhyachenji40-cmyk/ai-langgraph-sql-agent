import google.generativeai as genai
import os

# 1. Configuration
genai.configure(api_key="AIzaSyBNW0gWEbU077Qy1rO3iPA5d6Ez3eX_dow")

def generate_and_save_solutions():
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Path to your data
    file_path = os.path.join("Jenson USA", "Bikes - load data.sql")
    
    if not os.path.exists(file_path):
        return "❌ Error: Could not find the SQL data file."

    with open(file_path, 'r') as file:
        sql_content = file.read()

    prompt = f"""
    You are a Data Analyst at Jenson USA. Using this data: {sql_content[:4000]}
    
    Provide the SQL queries for all 12 Milestone tasks. 
    Format the output as a clean SQL file with comments like:
    -- Question 1: [Description]
    [SQL Code];
    """
    
    print("✨ Gemini is drafting your 12 SQL solutions...")
    response = model.generate_content(prompt)
    solutions_text = response.text
    
    # Remove any markdown formatting if the AI added it (like ```sql)
    clean_sql = solutions_text.replace("```sql", "").replace("```", "")

    # Save to a new file
    output_filename = "Jenson_Milestone_Solutions.sql"
    with open(output_filename, "w") as f:
        f.write(clean_sql)
    
    return f"✅ Success! Solutions saved to: {output_filename}"

# --- EXECUTION ---
try:
    status = generate_and_save_solutions()
    print(status)
except Exception as e:
    print(f"❌ Error: {e}")