from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
load_dotenv()


client = OpenAI(
    api_key = getenv("OPENAI_API_KEY")
).with_options(timeout=20,max_retries=0)
