import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import time
import chromadb
from chromadb.utils import embedding_functions
import uuid

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("Google API Key is missing. Please configure it in your .env file.")
    st.stop()

# Initialize Google Gemini AI
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

# Initialize ChromaDB client for feedback storage
chroma_client = chromadb.PersistentClient(path="./feedback_db")
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
feedback_collection = chroma_client.get_or_create_collection(
    name="query_feedback",
    embedding_function=embedding_function
)

def block_inappropriate_query(user_query):
    """Block queries with toxic or inappropriate content."""
    toxic_keywords = ["fuck", "sex", "sexual", "shit", "ass", "violence", "drugs", "hate", "political"]
    if any(word in user_query.lower() for word in toxic_keywords):
        return "I'm sorry, but I cannot process inappropriate or offensive queries."
    return None

# def block_irrelevant_query(user_query):
#     """Block queries that are irrelevant to manufacturing analytics."""
#     relevant_keywords = ["customer", "order", "product", "address", "id", "quantity", "delivery", "manufacturing", "inventory", "sales", "city", "plant"]
#     if not any(keyword in user_query.lower() for keyword in relevant_keywords):
#         return "This query appears irrelevant to manufacturing analytics. Please ask something related to manufacturing data."
#     return None

def check_sql_safety(user_query):
    """Block queries with potentially harmful SQL operations."""
    sql_blacklist = ["DROP", "DELETE", "ALTER", "UPDATE", "TRUNCATE"]
    if any(word in user_query.upper() for word in sql_blacklist):
        return "Your query involves restricted SQL operations and cannot be processed."
    return None

def get_schema(cursor, database):
    """Fetch enhanced schema information with primary keys"""
    try:
        schema_info = {"tables": {}, "relationships": [], "primary_keys": {}}
        
        cursor.execute(f"""
            SELECT table_name, column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = '{database}'
            ORDER BY table_name, ordinal_position
        """)
        
        for table, column, dtype, nullable, default in cursor.fetchall():
            if table not in schema_info["tables"]:
                schema_info["tables"][table] = []
            col_info = f"{column} ({dtype})"
            if nullable == 'NO':
                col_info += " NOT NULL"
            if default:
                col_info += f" DEFAULT {default}"
            schema_info["tables"][table].append(col_info)
        
        cursor.execute(f"""
            SELECT table_name, column_name
            FROM information_schema.key_column_usage
            WHERE table_schema = '{database}'
            AND constraint_name = 'PRIMARY'
        """)
        
        for table, column in cursor.fetchall():
            if table not in schema_info["primary_keys"]:
                schema_info["primary_keys"][table] = []
            schema_info["primary_keys"][table].append(column)
        
        cursor.execute(f"""
            SELECT TABLE_NAME, COLUMN_NAME, 
                   REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = '{database}'
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        
        for table, col, ref_table, ref_col in cursor.fetchall():
            schema_info["relationships"].append(f"{table}.{col} → {ref_table}.{ref_col}")
        
        schema_str = "Database Schema:\n"
        for table, columns in schema_info["tables"].items():
            schema_str += f"\nTable {table}:\n"
            if table in schema_info["primary_keys"]:
                schema_str += f"  Primary Keys: {', '.join(schema_info['primary_keys'][table])}\n"
            schema_str += "  Columns:\n  - " + "\n  - ".join(columns)
        
        schema_str += "\n\nRelationships:\n- " + "\n- ".join(schema_info["relationships"])
        return schema_str
        
    except mysql.connector.Error as err:
        st.error(f"Schema error: {err}")
        return None

def clean_sql(raw_sql):
    """Remove markdown and extra whitespace from SQL"""
    cleaned_sql = raw_sql.replace("sql", "").replace("", "").strip()
    # Remove any remaining leading/trailing backticks or newlines
    cleaned_sql = "\n".join(line.strip() for line in cleaned_sql.splitlines() if line.strip() and not line.strip().startswith(""))
    return cleaned_sql

def get_relevant_feedback(user_query):
    """Retrieve relevant positive feedback examples from ChromaDB using RAG"""
    try:
        results = feedback_collection.query(
            query_texts=[user_query],
            where={"feedback": "positive"},
            n_results=3
        )
        examples = []
        for i in range(len(results["ids"][0])):
            example = (
                f"Example {i+1}:\n"
                f"Query: {results['metadatas'][0][i]['user_query']}\n"
                f"SQL: {results['metadatas'][0][i]['generated_sql']}\n"
            )
            examples.append(example)
        return "\n".join(examples) if examples else "No relevant positive feedback examples found."
    except Exception as e:
        st.warning(f"Error retrieving feedback examples: {e}")
        return "No relevant positive feedback examples found."

def generate_sql(user_query, schema):
    """Generate SQL with RAG using relevant feedback examples"""
    feedback_examples = get_relevant_feedback(user_query)
    prompt_template = PromptTemplate(
        template="""
        As an expert SQL developer, convert this English query to MySQL syntax.
        
        Database Schema:
        {schema}
        
        Relevant Positive Feedback Examples:
        {feedback_examples}
        
        Critical Rules:
        1. Use exact column and table names as they appear in the schema
        2. Verify all relationships using foreign keys explicitly listed in the schema
        3. Use explicit JOIN syntax (INNER JOIN, LEFT JOIN) with correct column names
        4. Always quote string literals with single quotes
        5. Select specific columns instead of using *
        6. Include proper GROUP BY if using aggregates
        7. Use table aliases consistently (e.g., 'c' for customer, 'o' for orders)
        8. Validate date formats (use STR_TO_DATE if needed)
        9. Handle NULL values appropriately
        10. Leverage relevant feedback examples to ensure accuracy
        
        Query: "{user_query}"
        
        Return ONLY the raw SQL query without any markdown (e.g., no sql or ```).
        """,
        input_variables=["schema", "user_query", "feedback_examples"]
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run({"schema": schema, "user_query": user_query, "feedback_examples": feedback_examples})
    return clean_sql(response)

def correct_query(original_query, original_sql, schema):
    """Simplified Agentic AI to correct a query based on negative feedback using RAG"""
    feedback_examples = get_relevant_feedback(original_query)
    prompt_template = PromptTemplate(
        template="""
        As an expert SQL developer with agentic reasoning capabilities, the user provided the following query and SQL, but gave negative feedback indicating it was incorrect:
        
        Original Query: "{original_query}"
        Original SQL: "{original_sql}"
        
        Database Schema:
        {schema}
        
        Relevant Positive Feedback Examples:
        {feedback_examples}
        
        Analyze the original query and SQL, identify potential issues (e.g., incorrect table names, wrong column references, invalid joins, or misinterpretation of intent), and suggest a corrected English query and corresponding SQL. Ensure:
        - Exact column and table names match the schema (e.g., no prefixed columns like 'd.d_orderID' unless explicitly in schema)
        - Joins use correct foreign key relationships from the schema
        - The correction aligns with manufacturing analytics context (e.g., customers, orders, products)
        - Leverage positive feedback examples for improved accuracy
        
        Return the response EXACTLY in this format without any additional text or markdown:
        Corrected Query: <corrected English query>
        Corrected SQL: <corrected SQL>
        """,
        input_variables=["original_query", "original_sql", "schema", "feedback_examples"]
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run({
        "original_query": original_query,
        "original_sql": original_sql,
        "schema": schema,
        "feedback_examples": feedback_examples
    })
    
    # Debug: Show raw response if parsing fails
    st.write("Raw LLM Response (for debugging):")
    st.code(response)
    
    try:
        lines = response.strip().split("\n")
        corrected_query = None
        corrected_sql = None
        for line in lines:
            if line.startswith("Corrected Query:"):
                corrected_query = line.replace("Corrected Query:", "").strip()
            elif line.startswith("Corrected SQL:"):
                corrected_sql = line.replace("Corrected SQL:", "").strip()
        if corrected_query and corrected_sql:
            return corrected_query, clean_sql(corrected_sql)
        else:
            st.error("LLM failed to provide both corrected query and SQL.")
            return None, None
    except Exception as e:
        st.error(f"Error parsing corrected query: {e}")
        return None, None

def execute_query(db_config, query):
    """Execute query with proper resource handling"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(query)
        
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
        else:
            df = pd.DataFrame({"Message": ["Query executed successfully, but no data returned."]})
        
        conn.commit()
        return df
    except mysql.connector.Error as err:
        return pd.DataFrame({"Error": [f"Database error: {err.msg}"], "SQL": [query]})
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def store_feedback(user_query, generated_sql, feedback, execution_success=None, execution_time=None):
    """Store feedback in ChromaDB for continuous improvement"""
    try:
        doc_id = str(uuid.uuid4())
        metadata = {
            "user_query": user_query,
            "generated_sql": generated_sql,
            "feedback": feedback if feedback is not None else "None",
            "execution_success": str(execution_success) if execution_success is not None else "None",
            "execution_time": str(execution_time) if execution_time is not None else "None",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        feedback_collection.add(
            documents=[f"{user_query} -> {generated_sql}"],
            metadatas=[metadata],
            ids=[doc_id]
        )
        return True
    except Exception as e:
        st.error(f"Feedback storage error: {e}")
        return False

# Streamlit UI Configuration
st.set_page_config(page_title="Manufacturing Analytics", layout="wide", page_icon="🏭")

# Initialize session state
if 'schema' not in st.session_state:
    st.session_state.schema = None
if 'result' not in st.session_state:
    st.session_state.result = pd.DataFrame()
if 'generated_sql' not in st.session_state:
    st.session_state.generated_sql = ""
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'corrected_query' not in st.session_state:
    st.session_state.corrected_query = None
if 'execute_query' not in st.session_state:
    st.session_state.execute_query = False

# Database Connection
with st.sidebar.expander("🔧 Database Configuration", expanded=True):
    db_config = {
        "host": st.text_input("Host", "localhost"),
        "user": st.text_input("User", "root"),
        "password": st.text_input("Password", type="password"),
        "database": st.text_input("Database", "manufacturing")
    }
    
    if st.button("📥 Load Schema", use_container_width=True):
        with st.spinner("Analyzing database structure..."):
            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                schema = get_schema(cursor, db_config["database"])
                conn.close()
                st.session_state.schema = schema
                st.success("Schema loaded!")
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")

# Main Interface
st.title("📊 Manufacturing Analytics Dashboard")
st.write("Explore manufacturing data through natural language queries")

# Query Section
with st.expander("🔍 Start Your Analysis", expanded=True):
    user_input = st.text_area(
        "Enter your question:", 
        "Show customer IDs and addresses for customers who ordered product ID 50",
        height=100,
        label_visibility="collapsed",
        key="query_input"
    )
    
    # Execute on Enter key or button click
    if st.button("🚀 Execute Query", use_container_width=True) or st.session_state.execute_query:
        if not st.session_state.schema:
            st.error("Please load schema first!")
        else:
            with st.spinner("Processing..."):
                try:
                    inappropriate_result = block_inappropriate_query(user_input)
                    if inappropriate_result:
                        st.session_state.result = pd.DataFrame({"Message": [inappropriate_result]})
                        st.session_state.generated_sql = ""
                        st.session_state.corrected_query = None
                    else:
                        irrelevant_result = block_irrelevant_query(user_input)
                        if irrelevant_result:
                            st.session_state.result = pd.DataFrame({"Message": [irrelevant_result]})
                            st.session_state.generated_sql = ""
                            st.session_state.corrected_query = None
                        else:
                            sql_safety_result = check_sql_safety(user_input)
                            if sql_safety_result:
                                st.session_state.result = pd.DataFrame({"Message": [sql_safety_result]})
                                st.session_state.generated_sql = ""
                                st.session_state.corrected_query = None
                            else:
                                start_time = time.time()
                                generated_sql = generate_sql(user_input, st.session_state.schema)
                                st.session_state.generated_sql = generated_sql
                                result = execute_query(db_config, generated_sql)
                                execution_time = time.time() - start_time
                                st.session_state.result = result
                                st.session_state.feedback = None
                                st.session_state.corrected_query = None
                                
                                store_feedback(
                                    user_input,
                                    generated_sql,
                                    None,
                                    "Error" not in result.columns,
                                    execution_time
                                )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        st.session_state.execute_query = False

# Handle Enter key press
def on_enter():
    st.session_state.execute_query = True

st.text_input("Press Enter to Execute", key="enter_input", on_change=on_enter, label_visibility="collapsed")

# Results Display
if not st.session_state.result.empty:
    st.divider()
    
    if "Error" in st.session_state.result.columns:
        st.error(st.session_state.result["Error"][0])
        if "SQL" in st.session_state.result.columns:
            st.code(st.session_state.result["SQL"][0], language='sql')
    elif "Message" in st.session_state.result.columns and "Query executed successfully" not in st.session_state.result["Message"][0]:
        st.warning(st.session_state.result["Message"][0])
    else:
        df = st.session_state.result
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📄 Query Results")
            if df.empty or "Query executed successfully" in df.get("Message", [""])[0]:
                st.write("No data returned for this query.")
            else:
                st.dataframe(
                    df.style.highlight_null(props="color: red;"),
                    use_container_width=True,
                    height=400
                )
            
            if not df.empty and "Message" not in df.columns:
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Export CSV",
                    csv,
                    "query_results.csv",
                    use_container_width=True
                )
            
            # Always show feedback section for executed queries
            st.divider()
            st.subheader("💬 Provide Feedback")
            if st.session_state.feedback is None:
                st.write("Was this result helpful?")
                col_fb1, col_fb2 = st.columns(2)
                with col_fb1:
                    if st.button("👍 Yes"):
                        st.session_state.feedback = "positive"
                        store_feedback(
                            user_input if not st.session_state.corrected_query else st.session_state.corrected_query,
                            st.session_state.generated_sql,
                            "positive",
                            "Error" not in df.columns,
                            None
                        )
                        st.success("Thank you! Feedback recorded.")
                with col_fb2:
                    if st.button("👎 No"):
                        st.session_state.feedback = "negative"
                        store_feedback(
                            user_input if not st.session_state.corrected_query else st.session_state.corrected_query,
                            st.session_state.generated_sql,
                            "negative",
                            "Error" not in df.columns,
                            None
                        )
                        with st.spinner("Analyzing and correcting your query..."):
                            corrected_query, corrected_sql = correct_query(
                                user_input,
                                st.session_state.generated_sql,
                                st.session_state.schema
                            )
                            if corrected_query and corrected_sql:
                                st.session_state.corrected_query = corrected_query
                                st.session_state.generated_sql = corrected_sql
                                result = execute_query(db_config, corrected_sql)
                                st.session_state.result = result
                                st.session_state.feedback = None
                                store_feedback(
                                    corrected_query,
                                    corrected_sql,
                                    None,
                                    "Error" not in result.columns,
                                    None
                                )
                                st.info(f"Corrected Query: {corrected_query}")
                            else:
                                st.warning("Could not generate a corrected query. Please refine your input.")
            else:
                st.success("Thank you for your feedback! It's helping us improve.")
                if st.session_state.corrected_query:
                    st.info(f"Corrected Query: {st.session_state.corrected_query}")

        with col2:
            if not df.empty and "Message" not in df.columns:
                st.subheader("📈 Data Visualization")
                
                chart_type = st.selectbox(
                    "Select Visualization Type",
                    options=["Bar", "Line", "Pie", "Sunburst", "Scatter", "Histogram", "Data Summary"],
                    index=0
                )

                if chart_type == "Bar":
                    cols = st.columns(2)
                    with cols[0]:
                        x_col = st.selectbox("X-axis", df.columns, key="x_bar")
                    with cols[1]:
                        y_col = st.selectbox("Y-axis", df.columns, key="y_bar")
                    color_col = st.selectbox("Color (optional)", [None] + list(df.columns), key="c_bar")
                    
                    fig = px.bar(
                        df,
                        x=x_col,
                        y=y_col,
                        color=color_col,
                        title=f"{y_col} by {x_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Line":
                    cols = st.columns(2)
                    with cols[0]:
                        x_col = st.selectbox("X-axis", df.columns, key="x_line")
                    with cols[1]:
                        y_col = st.selectbox("Y-axis", df.columns, key="y_line")
                    color_col = st.selectbox("Color (optional)", [None] + list(df.columns), key="c_line")
                    
                    fig = px.line(
                        df,
                        x=x_col,
                        y=y_col,
                        color=color_col,
                        title=f"{y_col} Trend by {x_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Pie":
                    cols = st.columns(2)
                    with cols[0]:
                        names_col = st.selectbox("Categories", df.columns, key="pie_names")
                    with cols[1]:
                        values_col = st.selectbox("Values", df.columns, key="pie_values")
                    
                    fig = px.pie(
                        df,
                        names=names_col,
                        values=values_col,
                        title=f"{values_col} Distribution by {names_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Sunburst":
                    cols = st.columns([2,1])
                    with cols[0]:
                        path_cols = st.multiselect("Hierarchy Path", df.columns, key="sunburst_path")
                    with cols[1]:
                        value_col = st.selectbox("Values", df.columns, key="sunburst_val")
                    
                    if len(path_cols) >= 1:
                        fig = px.sunburst(
                            df,
                            path=path_cols,
                            values=value_col,
                            title="Hierarchical Distribution"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Select at least 1 column for hierarchy path")

                elif chart_type == "Scatter":
                    cols = st.columns(3)
                    with cols[0]:
                        x_col = st.selectbox("X-axis", df.columns, key="x_scatter")
                    with cols[1]:
                        y_col = st.selectbox("Y-axis", df.columns, key="y_scatter")
                    with cols[2]:
                        color_col = st.selectbox("Color", [None] + list(df.columns), key="c_scatter")
                    
                    fig = px.scatter(
                        df,
                        x=x_col,
                        y=y_col,
                        color=color_col,
                        title=f"{y_col} vs {x_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Histogram":
                    cols = st.columns(2)
                    with cols[0]:
                        num_col = st.selectbox("Numerical Column", df.select_dtypes(include='number').columns, key="hist_col")
                    with cols[1]:
                        color_col = st.selectbox("Color (optional)", [None] + list(df.columns), key="hist_color")
                    
                    fig = px.histogram(
                        df,
                        x=num_col,
                        color=color_col,
                        title=f"Distribution of {num_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                else:  # Data Summary
                    st.write("##### 📋 Summary Statistics")
                    st.table(df.describe(include='all'))
                    st.write("##### 🧮 Value Counts")
                    count_col = st.selectbox("Select column for value counts", df.columns)
                    st.table(df[count_col].value_counts().reset_index())

# Generated SQL Display
if st.session_state.generated_sql:
    st.divider()
    with st.expander("🔎 View Generated SQL", expanded=False):
        st.code(st.session_state.generated_sql, language='sql')

# Schema Viewer
if st.session_state.schema:
    st.divider()
    with st.expander("📚 Database Schema Overview", expanded=False):
        st.code(st.session_state.schema)