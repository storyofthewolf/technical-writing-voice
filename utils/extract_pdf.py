#!/usr/bin/env python

"""
PDF Academic Text Extractor and Cleaner

Description:
    This script extracts text from academic PDFs while preserving the correct 
    reading order (crucial for multi-column layouts). It then applies a 
    heuristic-based cleaning algorithm to strip non-semantic "noise" such as 
    running headers/footers, figure/table captions, reference lists, DOIs, 
    and stray page numbers. The resulting text is optimized for Large Language 
    Model (LLM) ingestion and style analysis.

Dependencies:
    pip install pymupdf

Usage:
    Make executable: chmod +x extract_pdf.py
    
    Basic:
        ./extract_pdf.py input_paper.pdf
        (Outputs to 'cleaned_input_paper.txt' in the same directory)
        
    Custom Output:
        ./extract_pdf.py input_paper.pdf -o my_custom_name.txt
"""

import fitz
import re
import sys
import argparse
from collections import Counter
from pathlib import Path

def clean_academic_text_generalized(text):
    # 1. Truncate trailing non-authorial sections
    split_pattern = r'(?i)\n(?:Acknowledgments|References|Literature Cited)\s*\n'
    text = re.split(split_pattern, text, maxsplit=1)[0]
    
    lines = text.split('\n')
    cleaned_lines = []
    
    # 2. Frequency Analysis for Headers and Footers
    line_counts = Counter([line.strip() for line in lines if len(line.strip()) > 5])
    boilerplate_lines = {line for line, count in line_counts.items() if count >= 3}

    in_figure_caption = False

    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            in_figure_caption = False
            continue

        if stripped in boilerplate_lines:
            continue
            
        if re.match(r"^(?:Figure|Fig\.|Table)\s*\d+[\.:]", stripped, re.IGNORECASE):
            in_figure_caption = True
            continue
            
        if in_figure_caption:
            continue

        if stripped.isdigit():
            continue
        if re.search(r'(?:©|Copyright\s+\d{4})', stripped, re.IGNORECASE):
            continue
        if re.search(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', stripped, re.IGNORECASE):
            continue
        if re.match(r'^(?:Received|Accepted|Published|Revised)\s', stripped, re.IGNORECASE):
            continue

        line_clean = re.sub(r'\\s*', '', stripped)
        
        if len(line_clean.split()) < 3 and not re.search(r'[.!?]$', line_clean):
            continue

        if line_clean:
            cleaned_lines.append(line_clean)

    return "\n".join(cleaned_lines)

def main():
    parser = argparse.ArgumentParser(description="Extract and clean text from a single academic PDF.")
    parser.add_argument("input_pdf", help="Path to the input PDF file.")
    parser.add_argument("-o", "--output", help="Path to the output text file (optional).")
    args = parser.parse_args()

    input_path = Path(args.input_pdf)
    if not input_path.exists() or input_path.suffix.lower() != '.pdf':
        print(f"Error: Invalid PDF file path: {input_path}")
        sys.exit(1)

    # Default output name if none provided
    output_path = args.output if args.output else f"cleaned_{input_path.stem}.txt"

    try:
        doc = fitz.open(input_path)
        full_text = []
        
        for page in doc:
            blocks = page.get_text("blocks")
            for b in blocks:
                full_text.append(b[4])
                
        raw_text = "\n".join(full_text)
        clean_text = clean_academic_text_generalized(raw_text)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(clean_text)
            
        print(f"Successfully saved to: {output_path}")
        
    except Exception as e:
        print(f"Extraction failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
