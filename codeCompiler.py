
from config import llm  # Assumes llm is a LangChain LLM instance like ChatOpenAI or Gemini
import re

LANGUAGE_PROMPTS = {
    "cpp": "You are a smart C++ compiler assistant.",
    "python": "You are a smart Python interpreter assistant.",
    "java": "You are a smart Java compiler assistant."
}

def compile_code(code: str, lang: str) -> dict:
    # Handle empty code input
    if not code or code.isspace():
        return {
            'result': 'Failure',
            'message': 'No code provided. Please submit a valid code snippet.',
            'corrected_code': None
        }

    language_prompt = LANGUAGE_PROMPTS.get(lang, "You are a smart code assistant.")
    prompt = f"""
{language_prompt}
Given the following {lang} code, perform the following tasks:
[IMPORTANT] Never Auto Correct OR Change the given code.
[IMPORTANT] You are a {lang} compiler, give response exactly like how compilers works after compiling the code.
1. Try to compile the code and tell if it compiles or not.
2. If the code is already correct, simply confirm successful compilation.

Code:
```{lang}
{code}
```

Respond strictly exactly like a compiler:

[Result]: Compilation Success or Failure  
[Message]: You are a {lang} compiler, give response exactly like how compilers works after compiling the code.Incase of no error give the correct and exact output of the code without any extra text.
[CorrectedCode]: (if needed, provide corrected {lang} code in triple backticks, otherwise write "N/A")
"""

    response = llm.invoke(prompt).content

    # Extract result
    result_match = re.search(r'\[Result\]:\s*(.*)', response)
    result = result_match.group(1).strip() if result_match else "Unknown"

    # Extract message
    # Extract message
    message_match = re.search(r'\[Message\]:\s*(.*?)(?=\[CorrectedCode\]:)', response, re.DOTALL)
    message = message_match.group(1).strip() if message_match else "No message provided."

    # Extract corrected code if available
    corrected_code_match = re.search(r'```' + lang + r'(.*?)```', response, re.DOTALL)
    corrected_code = corrected_code_match.group(1).strip() if corrected_code_match else None

    return {
        'result': result,
        'message': message,
        'corrected_code': corrected_code
    }
