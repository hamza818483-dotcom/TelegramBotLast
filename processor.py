import os
import csv
from config import CSV_DIR, TEMP_DIR
import asyncio

# Dummy AI function (replace with OpenAI or local AI call)
async def ai_extract_mcqs(text, prompt=None):
    """
    Return list of dict MCQs in format:
    {"question": str, "options": [A,B,C,D], "answer": str}
    """
    # Example dummy MCQs
    return [
        {"question": "Sample Q1 from AI", "options": ["A1","B1","C1","D1"], "answer": "A1"},
        {"question": "Sample Q2 from AI", "options": ["A2","B2","C2","D2"], "answer": "B2"},
    ]

# ---------------- PDF Processing ----------------
async def process_pdf(pdf_path, args):
    """
    Mode1: /pdfm  -> extract AI MCQs from PDF pages
    Mode2: /qbm   -> ready-made MCQs from PDF
    """
    pages = "all"
    title = "Quiz"
    mode = "pdfm"
    
    for i, arg in enumerate(args):
        if arg == "-p":
            pages = args[i+1]
        elif arg == "-m":
            title = args[i+1]
        elif arg in ["pdfm", "qbm"]:
            mode = arg
    
    # Step 1: Extract text from PDF pages (pseudo)
    extracted_text = f"Text from {pdf_path} pages {pages}"
    
    # Step 2: Extract MCQs based on mode
    if mode == "pdfm":
        mcqs = await ai_extract_mcqs(extracted_text)
    else:  # qbm
        # Assume PDF already has MCQs, just read and format (pseudo)
        mcqs = [
            {"question":"Ready Q1","options":["A","B","C","D"],"answer":"A"},
            {"question":"Ready Q2","options":["A","B","C","D"],"answer":"C"},
        ]
    
    # Step 3: Save CSV
    os.makedirs(CSV_DIR, exist_ok=True)
    csv_file = os.path.join(CSV_DIR, os.path.basename(pdf_path).replace(".pdf", ".csv"))
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["questions","option1","option2","option3","option4","option5","answer","explanation","type","section"])
        for q in mcqs:
            writer.writerow([q["question"], *q["options"], "", q["answer"], "", "1", "1"])
    
    return csv_file

# ---------------- Image Processing ----------------
async def process_image(image_path, prompt):
    """
    Extract MCQs from image using AI + prompt
    """
    # Step1: OCR or AI read image (pseudo)
    image_text = f"Extracted text from {image_path}"
    
    # Step2: AI MCQ generation
    mcqs = await ai_extract_mcqs(image_text, prompt)
    
    # Step3: Save CSV
    os.makedirs(CSV_DIR, exist_ok=True)
    csv_file = os.path.join(CSV_DIR, os.path.basename(image_path).replace(".jpg", ".csv"))
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["questions","option1","option2","option3","option4","option5","answer","explanation","type","section"])
        for q in mcqs:
            writer.writerow([q["question"], *q["options"], "", q["answer"], "", "1", "1"])
    
    return csv_file
