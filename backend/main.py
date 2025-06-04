import uvicorn
from fastapi import FastAPI, File , UploadFile,Form 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"message":"Hello, Welcome"}

@app.post("/uploadfile/")
async def upload_files(
    files: List[UploadFile]= File(...),
    additional_notes: str = Form(...),
    model_type :Literal["LSTM","Transformer"]= Form(...),
):
    """
    Accepts:
    - List of files
    - A string of additional notes
    - A model type selection (either "lstm" or "transformer")
    """
    
    # Print debug info
    print("Received files:", [file.filename for file in files])
    print("Notes:", additional_notes)
    print("Model type:", model_type)
    
    #dummy data return
    return{
        "status":"success",
        "merged_output": "This is a dummy merged result.",
        "files_received": [file.filename for file in files],
        "notes_received": additional_notes,
        "model_used": model_type
    }