import streamlit as st
import json
from openai import OpenAI

# OpenAI client using OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",  
)

# Title and Description
st.title("📁 JSON Chatbot")
st.write("Upload a JSON file and ask questions about it!")

# Upload JSON file
uploaded_file = st.file_uploader("Upload JSON", type=["json"])

@st.cache_data(show_spinner=False)
def parse_json_file(file):
    try:
        # Try loading as a full JSON object (array or dict)
        return json.load(file)
    except json.JSONDecodeError:
        # Reset file pointer and try line-by-line parsing (NDJSON fallback)
        file.seek(0)
        lines = file.read().decode('utf-8').splitlines()
        return [json.loads(line) for line in lines if line.strip()]

# Store JSON in session
if uploaded_file:
    try:
        json_data = parse_json_file(uploaded_file)
        st.session_state.json_data = json_data
        st.success("✅ JSON file loaded successfully!")
        st.json(json_data if isinstance(json_data, dict) else json_data[:5])  # Preview first 5 if array
    except Exception as e:
        st.error(f"❌ Failed to load JSON: {e}")

# Input question
question = st.text_input("Ask a question about your JSON data:")

# Ask AI
if st.button("Ask") and question:
    if "json_data" not in st.session_state:
        st.warning("Please upload a JSON file first.")
    else:
        try:
            # Summarize large JSON to avoid overload
            raw = json.dumps(st.session_state.json_data[:50] if isinstance(st.session_state.json_data, list) else st.session_state.json_data)
            chunked = raw[:5000]  # Truncate if needed

            messages = [
                {
                    "role": "system",
                    "content": "You are a JSON expert. The user will give you a JSON dataset and ask questions about its content."
                },
                {
                    "role": "user",
                    "content": f"Here is the JSON: {chunked}"
                },
                {
                    "role": "user",
                    "content": question
                }
            ]

            response = client.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324:free",
                messages=messages,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "Streamlit JSON Chatbot"
                }
            )

            answer = response.choices[0].message.content
            st.markdown("### 🧠 Answer:")
            st.markdown(answer)

        except Exception as e:
            st.error(f"Error: {e}")
