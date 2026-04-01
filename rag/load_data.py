import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.vector_store import get_vector_store

def clean_text(text):
    """Normalize whitespace: replace multiple newlines and spaces with single ones."""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def load_pdf(pdf_path, chunk_size=500, chunk_overlap=100):
    print(f"Extracting text from {pdf_path}...")
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        all_text = []
        total_pages = len(reader.pages)
        for i, page in enumerate(reader.pages):
            if i % 50 == 0:
                print(f"Processing page {i+1} of {total_pages}...")
            page_text = page.extract_text()
            if page_text:
                all_text.append(clean_text(page_text))
            else:
                print(f"Warning: no text on page {i+1}")

    full_text = "\n\n".join(all_text)      # separate pages by double newline

    print("Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_text(full_text)

    # Clean each chunk again (just in case)
    chunks = [clean_text(chunk) for chunk in chunks]

    print(f"Adding {len(chunks)} chunks to ChromaDB...")
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    print("Done!")

if __name__ == "__main__":
    # Use a default relative path, or ask user
    pdf_path = input("Enter path to your PDF file (or press Enter to use './C4.pdf'): ").strip()
    if not pdf_path:
        pdf_path = "C4.pdf"
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
    else:
        load_pdf(pdf_path)