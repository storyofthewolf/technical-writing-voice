#!/usr/bin/env python

"""
Universal LLM Token Counter

Description:
    This script calculates the exact number of LLM tokens in a given file, 
    providing a highly precise count rather than a rough word-to-token estimate. 
    It supports direct ingestion of PDFs, Markdown, and plain text files. By 
    default, it uses the 'cl100k_base' encoding, which is the standard tokenizer 
    for modern models (e.g., GPT-4, Claude 3).

Dependencies:
    pip install tiktoken pymupdf

Usage:
    Make executable: chmod +x count_tokens.py
    
    Basic:
        ./count_tokens.py document.txt
        ./count_tokens.py research_paper.pdf
        ./count_tokens.py documentation.md
        
    Specify Tokenizer Encoding (Optional):
        ./count_tokens.py document.txt --model p50k_base
"""

import argparse
import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    pass

try:
    import tiktoken
except ImportError:
    print("Error: 'tiktoken' is required. Install via: pip install tiktoken")
    sys.exit(1)

def extract_text_from_pdf(pdf_path):
    if 'fitz' not in sys.modules:
        print("Error: PyMuPDF (fitz) is required for PDF parsing. Install via: pip install pymupdf")
        sys.exit(1)
        
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def main():
    parser = argparse.ArgumentParser(description="Count exact LLM tokens in a PDF, TXT, or MD file.")
    parser.add_argument("input_file", help="Path to the input file (.pdf, .txt, .md).")
    
    # cl100k_base is the standard encoding for modern models (GPT-4, Claude 3, etc.)
    parser.add_argument("--model", default="cl100k_base", help="Encoding model (default: cl100k_base).")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    ext = input_path.suffix.lower()
    
    try:
        if ext == '.pdf':
            text = extract_text_from_pdf(input_path)
        elif ext in ['.txt', '.md']:
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            print(f"Error: Unsupported file type '{ext}'. Please provide a .pdf, .txt, or .md file.")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to read file: {e}")
        sys.exit(1)

    try:
        encoding = tiktoken.get_encoding(args.model)
        # disallowed_special=() allows the tokenizer to process text containing <|endoftext|> without throwing an error
        num_tokens = len(encoding.encode(text, disallowed_special=()))
        print(f"File: {input_path.name}")
        print(f"Exact Tokens ({args.model}): {num_tokens:,}")
    except Exception as e:
        print(f"Token counting failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
