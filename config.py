from langchain_google_genai import ChatGoogleGenerativeAI

# Configure Gemini Flash model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    convert_system_message_to_human=True
)