from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from typing import List
import uvicorn
import os
import fitz  
import docx
import google.generativeai as genai
import pandas as pd
from io import BytesIO
import ast

app = FastAPI(title="Resume Ranking API", description="API to rank resumes based on job descriptions")

os.environ["GEMINI_API_KEY"] = "AIzaSyAVGFYHqLKbdLhgQuYX91EFHqOY1ruRZTU"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text from PDF or DOCX file.
    """
    if file.filename.endswith(".pdf"):
        # Read PDF bytes and reset pointer
        file_bytes = file.file.read()
        file.file.seek(0)
        pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "\n".join(page.get_text() for page in pdf_doc)
    elif file.filename.endswith(".docx"):
        # Ensure pointer is at the beginning and wrap in BytesIO
        file.file.seek(0)
        doc = docx.Document(BytesIO(file.file.read()))
        text = "\n".join(para.text for para in doc.paragraphs)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF or DOCX.")
    return text

def extract_criteria(text: str) -> List[str]:
    """Use OpenAI to extract job ranking criteria."""
    prompt = f"""
    Extract key ranking criteria such as skills, certifications, experience, and qualifications from the following job description:
    return the criteria only as a list of strings separated by end-of-line characters.
    {text}
    """
    response = model.generate_content(prompt)
    return str(response.text).split("\n")

@app.post("/extract-criteria")
async def extract_criteria_endpoint(file: UploadFile = File(...)):
    text = extract_text_from_file(file)
    criteria = extract_criteria(text)
    criteria = [criterion for criterion in criteria if criterion!=""]
    return {"criteria": criteria}

def score_resume(text: str, criteria: List[str]) -> dict:
    """Score resume against the extracted job criteria."""
    scores = {criterion: 0 for criterion in criteria}
    for criterion in criteria:
        prompt = f""" 
            You are provided with two pieces of text: one is a resume, and the other is a set of evaluation criteria. 
            Your task is to evaluate the resume strictly based on the provided criteria. Please follow these instructions:
        Evaluation: 
            Assess how well the resume meets the evaluation criteria.
        Scoring:
            If the resume meets the criteria, return a numerical score between 1 and 5 (where 1 represents a very poor match and 5 represents an excellent match).
            If the resume does not meet the criteria, if the criteria are not applicable, or for any other reason that prevents a proper evaluation, return a score of 0.
        Output Format: 
            Provide only the final numerical score as your answer with no additional text or commentary.
        here is the resume {text} and here is the criteria {criterion}
                """
        response = model.generate_content(prompt)
        print(response.text)
        try :
            scores[criterion] = int(response.text)  # Assign full score if criterion exists
        except ValueError:
            scores[criterion] = 0
    total_score = sum(scores.values())
    return {**scores, "Total Score": total_score}

@app.post("/score-resumes")
async def score_resumes_endpoint(
    criteria: List[str] = Form(...),
    files: List[UploadFile] = File(...)
):
    criteria = criteria[0].split(",")
    results = []
    for file in files:
        text = extract_text_from_file(file)
        score = score_resume(text, criteria)
        results.append({"Candidate Name": file.filename, "scores" : score})
    df = pd.DataFrame(results)
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return {"filename": "resume_scores.xlsx", "results": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)