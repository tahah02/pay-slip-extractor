import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8005/api"
DATASET_DIR = Path("dataset")

def test_payslip(pdf_file):
    print(f"\n{'='*60}")
    print(f"Testing: {pdf_file.name}")
    print(f"{'='*60}")
    
    with open(pdf_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code != 200:
        print(f"[X] Upload failed: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    upload_id = data.get('upload_id')
    print(f"[OK] Upload successful")
    print(f"     Upload ID: {upload_id}")
    print(f"     Status: {data.get('status')}")
    
    print(f"\n[...] Waiting for processing...")
    time.sleep(5)
    
    result_response = requests.get(f"{BASE_URL}/result/{upload_id}")
    
    if result_response.status_code == 202:
        print(f"[...] Still processing... (202)")
        time.sleep(5)
        result_response = requests.get(f"{BASE_URL}/result/{upload_id}")
    
    if result_response.status_code != 200:
        print(f"[X] Result fetch failed: {result_response.status_code}")
        print(result_response.text)
        return
    
    result = result_response.json()
    
    print(f"\n[OK] Processing complete!")
    print(f"     Total documents: {result.get('total_documents')}")
    
    for doc in result.get('documents', []):
        extracted = doc.get('extracted_data', {})
        confidence = doc.get('confidence_score', 0)
        
        print(f"\n     Document #{doc.get('document_number')}:")
        print(f"     - Name: {extracted.get('name', 'N/A')}")
        print(f"     - ID: {extracted.get('id_number', 'N/A')}")
        print(f"     - Gross: {extracted.get('gross_income', 'N/A')}")
        print(f"     - Net: {extracted.get('net_income', 'N/A')}")
        print(f"     - Deduction: {extracted.get('total_deduction', 'N/A')}")
        print(f"     - Month/Year: {extracted.get('month_year', 'N/A')}")
        print(f"     - Confidence: {confidence*100:.1f}%")
        
        errors = doc.get('validation_errors', [])
        if errors:
            print(f"     [!] Validation errors:")
            for error in errors:
                print(f"         - {error}")

def main():
    print("\n" + "="*60)
    print("PAYSLIP EXTRACTION TEST - DATASET")
    print("="*60)
    
    pdf_files = sorted(DATASET_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print("[X] No PDF files found in dataset folder")
        return
    
    print(f"\n[*] Found {len(pdf_files)} PDF files:")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"    {i}. {pdf.name}")
    
    for pdf_file in pdf_files:
        try:
            test_payslip(pdf_file)
        except Exception as e:
            print(f"[X] Error: {str(e)}")
    
    print(f"\n{'='*60}")
    print("[OK] TEST COMPLETE")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
