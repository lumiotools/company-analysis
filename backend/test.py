# pip install -U llama-index llama-parse
# pip install llama-parse llama-index

import os
from llama_parse import LlamaParse
from dotenv import load_dotenv
load_dotenv()

# Initialize the LlamaParse client
parser = LlamaParse(
    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),  # Use os.getenv() not os.getenv[]
    result_type="markdown"  # Options: "markdown", "text", or "elements"
)

# Parse a PDF file
documents = parser.load_data("Alpine VC Overview.pdf")

# Access the extracted content
for doc in documents:
    print(doc.text)  # Print the extracted text content
    print(doc.metadata)  # Print metadata like page numbers