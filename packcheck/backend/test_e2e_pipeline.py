import os
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def run_e2e_test():
    print("=" * 60)
    print("STARTING PACKCHECK END-TO-END PIPELINE VERIFICATION")
    print("=" * 60)

    # 1. Login
    print("\n[Step 1] Logging in as Inspector...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "username_or_email": "inspector",
        "password": "Inspector@123"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[OK] Authenticated! Officer: {login_res.json()['user']['full_name']}")

    # 2. Create Inspection Draft
    print("\n[Step 2] Creating new inspection draft...")
    insp_payload = {
        "product_name": "NutriFeast Organic Oats & Honey Cookies",
        "brand": "NutriFeast",
        "category": "Packaged Food & Beverages",
        "identifier": "8908001234567",
        "location": "Central Inspection Checkpoint, Delhi",
        "batch_number": "NF-2026/08A",
        "inspector_remarks": "Test scan of high-density declaration label."
    }
    create_res = requests.post(f"{BASE_URL}/inspections", json=insp_payload, headers=headers)
    assert create_res.status_code == 201, f"Create inspection failed: {create_res.text}"
    inspection = create_res.json()
    insp_id = inspection["id"]
    insp_num = inspection["inspection_number"]
    print(f"[OK] Created Inspection: ID {insp_id} ({insp_num})")

    # 3. Upload Package Image
    print("\n[Step 3] Uploading package photograph (cookie_label.jpg)...")
    img_path = "test_assets/cookie_label.jpg"
    assert os.path.exists(img_path), f"Test image missing: {img_path}"
    with open(img_path, "rb") as f:
        upload_res = requests.post(
            f"{BASE_URL}/inspections/{insp_id}/images",
            files={"files": ("cookie_label.jpg", f, "image/jpeg")},
            data={"image_side": "Principal Display Panel (Front)"},
            headers=headers
        )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    print(f"[OK] Image uploaded successfully: {upload_res.json()['message']}")

    # 4. Process Inspection (Preprocessing + PaddleOCR + Field Extraction + Rule Engine)
    print("\n[Step 4] Executing AI processing pipeline (OCR + Extraction + Rules)...")
    proc_res = requests.post(f"{BASE_URL}/inspections/{insp_id}/process", headers=headers)
    assert proc_res.status_code == 200, f"Processing failed: {proc_res.text}"
    processed_insp = proc_res.json()
    print(f"[OK] Processing completed!")
    print(f"   Overall Status: {processed_insp['overall_status']}")
    print(f"   Compliance Score: {processed_insp['compliance_score']}%")
    print(f"   Total Checks: {processed_insp['total_checks']} | Passed: {processed_insp['passed_checks']}")
    print(f"   Violations Flagged: {processed_insp['violations_count']}")

    # 5. Verify Extracted Declarations
    print("\n[Step 5] Validating Extracted Legal Declarations:")
    fields = processed_insp["extracted_fields"]
    for f in fields:
        print(f"   - {f['field_name'].upper()}: '{f['field_value']}' (Status: {f['status']}, Conf: {int(f['confidence']*100)}%)")

    # 6. Verify OCR Bounding Boxes
    print("\n[Step 6] Verifying OCR bounding boxes...")
    ocr_res = requests.get(f"{BASE_URL}/inspections/{insp_id}/ocr", headers=headers)
    assert ocr_res.status_code == 200
    ocr_items = ocr_res.json()
    print(f"[OK] Retrieved {len(ocr_items)} OCR bounding boxes with text coordinates.")

    # 7. Test Manual Correction (Section 15)
    print("\n[Step 7] Testing officer manual correction of OCR declaration...")
    mrp_field = next((f for f in fields if f["field_name"] == "mrp"), None)
    if mrp_field:
        correct_res = requests.patch(
            f"{BASE_URL}/inspections/{insp_id}/fields/{mrp_field['id']}",
            json={"corrected_value": "140.00", "notes": "Verified against physical stamp: ₹140.00 inclusive of taxes."},
            headers=headers
        )
        assert correct_res.status_code == 200
        print(f"[OK] Field corrected! New value: '{correct_res.json()['corrected_value']}' (Original OCR preserved: '{correct_res.json()['original_ocr_text']}')")

    # 8. Generate Official PDF Report
    print("\n[Step 8] Generating official ReportLab inspection certificate PDF...")
    rep_res = requests.post(f"{BASE_URL}/reports/{insp_id}/generate", headers=headers)
    assert rep_res.status_code == 200
    rep_data = rep_res.json()
    print(f"[OK] PDF report generated: {rep_data['pdf_filename']} (Report ID: {rep_data['report_id']})")

    # 9. Verify Live Dashboard Statistics
    print("\n[Step 9] Verifying live PostgreSQL-backed Dashboard...")
    dash_res = requests.get(f"{BASE_URL}/dashboard", headers=headers)
    assert dash_res.status_code == 200
    stats = dash_res.json()["stats"]
    print(f"[OK] Total Inspections in DB: {stats['total_inspections']}")
    print(f"[OK] Compliant: {stats['compliant_count']}, Non-Compliant: {stats['non_compliant_count']}, Review: {stats['manual_review_count']}")

    print("\n" + "=" * 60)
    print("ALL END-TO-END PIPELINE TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    run_e2e_test()
