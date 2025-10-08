import uvicorn
from main_fastapi import app

def main():
    
    print("Starting EU Regulatory Document Processor FastAPI application...")
    uvicorn.run(app, host="0.0.0.0", port=8010)

if __name__ == "__main__":
    main()