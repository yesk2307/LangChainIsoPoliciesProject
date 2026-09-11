import os
import warnings
from dotenv import load_dotenv

# Suppress version / urllib3 warnings
warnings.filterwarnings("ignore")

from langchain_google_genai import ChatGoogleGenerativeAI

# Load API key from .env file
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is not set. Please set it in your .env file.")

# Initialize Gemini Chat Model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=api_key,
)

# Invoke the model
response = llm.invoke("Explain LangChain in simple words")
print(response.content)
