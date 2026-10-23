import os
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_full_packcheck_suite():
    print("=" * 70)
    print("PACKCHECK COMPREHENSIVE ENDPOINT & COMPLIANCE VALIDATION SUITE")
    print("=" * 70)

    # 1. Health check
    print("\n[1] Testing /api/health...")
    h_res = requests.get(f"{BASE_URL}/health")
    assert h_res.status_code == 200, f"Health check failed: {h_res.text}"
    print(f"    [PASS] Health Status: {h_res.json()}")

    # 2. Login as Inspector
    print("\n[2] Testing Authentication /api/auth/login...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "username_or_email": "inspector",
        "password": "Inspector@123"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"    [PASS] Authenticated user: {login_res.json()['user']['full_name']}")

    # 3. List Rules
    print("\n[3] Testing Rules Registry /api/rules...")
    rules_res = requests.get(f"{BASE_URL}/rules", headers=headers)
    assert rules_res.status_code == 200
    rules = rules_res.json()
    print(f"    [PASS] Loaded {len(rules)} Legal Metrology compliance rules")

    # 4. Create new Inspection
    print("\n[4] Creating new inspection draft...")
    create_res = requests.post(f"{BASE_URL}/inspections", json={
        "product_name": "NutriFeast Organic Oats & Honey Cookies",
        "brand": "NutriFeast",
        "category": "Packaged Food & Beverages",
        "identifier": "8908001234567",
        "location": "Regional Quality Inspection Center, Mumbai",
        "batch_number": "NF-2026/08B",
        "inspector_remarks": "Official regulatory scan."
    }, headers=headers)
    assert create_res.status_code == 201
    insp = create_res.json()
    insp_id = insp["id"]
    print(f"    [PASS] Created Inspection ID: {insp_id}, Number: {insp['inspection_number']}")

    # 5. Upload Image
    print("\n[5] Uploading package image...")
    img_path = "test_assets/cookie_label.jpg"
    with open(img_path, "rb") as f:
        up_res = requests.post(
            f"{BASE_URL}/inspections/{insp_id}/images",
            files={"files": ("cookie_label.jpg", f, "image/jpeg")},
            data={"image_side": "Principal Display Panel (Front)"},
            headers=headers
        )
    assert up_res.status_code == 200
    print(f"    [PASS] Uploaded image successfully")

    # 6. Process Pipeline (OCR -> Extraction -> Compliance)
    print("\n[6] Running full AI OCR & Compliance pipeline...")
    proc_res = requests.post(f"{BASE_URL}/inspections/{insp_id}/process", headers=headers)
    assert proc_res.status_code == 200
    proc_data = proc_res.json()
    print(f"    [PASS] Pipeline completed:")
    print(f"           Score: {proc_data['compliance_score']}%")
    print(f"           Status: {proc_data['overall_status']}")
    print(f"           Checks Passed: {proc_data['passed_checks']}/{proc_data['total_checks']}")

    # 7. Check Extracted Declarations
    print("\n[7] Verifying extracted legal declarations...")
    fields = proc_data["extracted_fields"]
    assert len(fields) >= 6, "Expected at least 6 extracted declarations"
    for f in fields:
        print(f"    - {f['field_name']}: '{f['field_value']}' ({f['status']})")

    # 8. Check OCR Bounding Boxes
    print("\n[8] Verifying bounding boxes /api/inspections/{id}/ocr...")
    ocr_res = requests.get(f"{BASE_URL}/inspections/{insp_id}/ocr", headers=headers)
    assert ocr_res.status_code == 200
    ocr_boxes = ocr_res.json()
    assert len(ocr_boxes) > 0
    print(f"    [PASS] Retrieved {len(ocr_boxes)} OCR text segments with bounding boxes")

    # 9. Officer Manual Correction
    print("\n[9] Testing officer manual correction...")
    mrp_field = next((f for f in fields if f["field_name"] == "mrp"), None)
    if mrp_field:
        corr_res = requests.patch(
            f"{BASE_URL}/inspections/{insp_id}/fields/{mrp_field['id']}",
            json={"corrected_value": "140.00", "notes": "Verified by Senior Inspector Rajesh Kumar."},
            headers=headers
        )
        assert corr_res.status_code == 200
        print(f"    [PASS] Field corrected successfully: {corr_res.json()['corrected_value']}")

    # 10. Officer Final Decision
    print("\n[10] Testing officer final decision /api/inspections/{id}/decision...")
    dec_res = requests.post(
        f"{BASE_URL}/inspections/{insp_id}/decision",
        json={"status": "COMPLIANT", "notes": "Full compliance verified under Rule 6(1) of LMPC Rules 2011."},
        headers=headers
    )
    assert dec_res.status_code == 200
    print(f"    [PASS] Officer decision recorded: {dec_res.json()['overall_status']}")

    # 11. PDF Report Generation
    print("\n[11] Testing PDF generation /api/reports/{id}/generate...")
    pdf_res = requests.post(f"{BASE_URL}/reports/{insp_id}/generate", headers=headers)
    assert pdf_res.status_code == 200
    pdf_info = pdf_res.json()
    print(f"    [PASS] PDF Report generated: {pdf_info['pdf_filename']} (ID: {pdf_info['report_id']})")

    # 12. PDF Download
    print("\n[12] Testing PDF download...")
    dl_res = requests.get(f"{BASE_URL}/reports/{pdf_info['report_id']}/download", headers=headers)
    assert dl_res.status_code == 200
    assert len(dl_res.content) > 1000
    print(f"    [PASS] Downloaded PDF successfully ({len(dl_res.content)} bytes)")

    # 13. Products Repository & History
    print("\n[13] Testing Product Catalog /api/products...")
    prod_res = requests.get(f"{BASE_URL}/products", headers=headers)
    assert prod_res.status_code == 200
    prods = prod_res.json()
    print(f"    [PASS] Found {len(prods)} registered products")
    if prods:
        p_id = prods[0]["id"]
        hist_res = requests.get(f"{BASE_URL}/products/{p_id}/history", headers=headers)
        assert hist_res.status_code == 200
        print(f"    [PASS] Retrieved inspection history for product '{prods[0]['name']}' ({len(hist_res.json()['inspections'])} records)")

    # 14. Dashboard Analytics
    print("\n[14] Testing Enforcement Dashboard /api/dashboard...")
    dash_res = requests.get(f"{BASE_URL}/dashboard", headers=headers)
    assert dash_res.status_code == 200
    stats = dash_res.json()["stats"]
    print(f"    [PASS] Dashboard live stats:")
    print(f"           Total: {stats['total_inspections']}")
    print(f"           Compliant: {stats['compliant_count']}")
    print(f"           Non-Compliant: {stats['non_compliant_count']}")
    print(f"           Manual Review: {stats['manual_review_count']}")

    print("\n" + "=" * 70)
    print("ALL 14 SUITE TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    test_full_packcheck_suite()
