import os
from datetime import datetime, timedelta
from app.database import engine, Base, SessionLocal
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.rule import ComplianceRule, RuleType, RuleSeverity
from app.models.inspection import (
    Inspection,
    InspectionImage,
    OCRResult,
    ExtractedField,
    ComplianceResult,
    Violation,
    InspectionStatus,
    CheckStatus,
    FieldStatus,
)
from app.models.report import InspectionReport
from app.utils.security import get_password_hash

def init_db():
    print("Creating all tables in PostgreSQL packcheck database...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

    db = SessionLocal()
    try:
        # 1. Seed Users
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                email="admin@packcheck.gov.in",
                username="admin",
                full_name="Dr. V. Sharma (Controller of Legal Metrology)",
                hashed_password=get_password_hash("Admin@123"),
                role=UserRole.ADMIN,
                badge_number="CLM-DL-001",
                department="Legal Metrology Central Enforcement Cell"
            )
            db.add(admin)
            print("Seeded Admin: admin@packcheck.gov.in / Admin@123")

        inspector = db.query(User).filter(User.username == "inspector").first()
        if not inspector:
            inspector = User(
                email="inspector@packcheck.gov.in",
                username="inspector",
                full_name="Rajesh Kumar (Senior Enforcement Officer)",
                hashed_password=get_password_hash("Inspector@123"),
                role=UserRole.INSPECTOR,
                badge_number="INSP-LM-2045",
                department="Department of Consumer Affairs & Legal Metrology"
            )
            db.add(inspector)
            print("Seeded Inspector: inspector@packcheck.gov.in / Inspector@123")

        db.commit()

        # 2. Seed Default Legal Metrology (Packaged Commodities) Rules, 2011
        default_rules = [
            {
                "rule_id": "LMPC-R6-1A",
                "field": "manufacturer",
                "rule_type": RuleType.REQUIRED_FIELD,
                "description": "Name and complete address of the manufacturer, or where the manufacturer is not the packer, the name and address of the manufacturer and packer, or importer.",
                "severity": RuleSeverity.CRITICAL,
                "legal_reference": "Rule 6(1)(a) of Legal Metrology (Packaged Commodities) Rules, 2011",
                "enabled": True,
            },
            {
                "rule_id": "LMPC-R6-1A-ADDR",
                "field": "manufacturer",
                "rule_type": RuleType.PATTERN_VALIDATION,
                "description": "Manufacturer declaration must contain postal pin code and complete premises address.",
                "severity": RuleSeverity.HIGH,
                "legal_reference": "Rule 6(1)(a) of Legal Metrology (Packaged Commodities) Rules, 2011",
                "enabled": True,
            },
            {
                "rule_id": "LMPC-R6-1B",
                "field": "commodity_name",
                "rule_type": RuleType.REQUIRED_FIELD,
                "description": "The common or generic names of the commodity contained in the package.",
                "severity": RuleSeverity.HIGH,
                "legal_reference": "Rule 6(1)(b) of Legal Metrology (Packaged Commodities) Rules, 2011",
                "enabled": True,
            },
            {
                "rule_id": "LMPC-R6-1C",
                "field": "net_quantity",
                "rule_type": RuleType.REQUIRED_FIELD,
                "description": "The net quantity, in terms of the standard unit of weight or measure, of the commodity contained in the package.",
                "severity": RuleSeverity.CRITICAL,
                "legal_reference": "Rule 6(1)(c) of Legal Metrology (Packaged Commodities) Rules, 2011",
                "enabled": True,
            },
            {
                "rule_id": "LMPC-R6-1C-UNIT",
                "field": "net_quantity",
                "rule_type": RuleType.NUMERIC_VALIDATION,
                "description": "Net quantity must be declared using Second Schedule standard units (g, kg, ml, L, N, U). Non-standard units are prohibited.",
                "severity": RuleSeverity.CRITICAL,
                "legal_reference": "Rule 6(1)(c) & Second Schedule, LMPC Rules 2011",
                "enabled": True,
            },
            {
                "rule_id": "LMPC-R6-1D",
                "field": "date",
                "rule_type": RuleType.DATE_VALIDATION,
                "description": "The month and the year in which the commodity is manufactured or pre-packed or imported.",
                "severity": RuleSeverity.CRITICAL,
                "legal_reference": "Rule 6(1)(d) of Legal Metrology (Packaged Commodities) Rules, 2011",
                "enabled": True,
            },
            {
                "rule_id": "LMPC-R6-1DA",
                "field": "mrp",
                "rule_type": RuleType.REQUIRED_FIELD,
                "description": "The retail sale price of the package in Indian currency with explicit statement 'Inclusive of all taxes' (MRP Rs. / ₹).",
                "severity": RuleSeverity.CRITICAL,
                "legal_reference": "Rule 6(1)(da) of Legal Metrology (Packaged Commodities) Rules, 2011",
                "enabled": True,
            },
            {
                "rule_id": "LMPC-R6-1DA-TAX",
                "field": "mrp",
                "rule_type": RuleType.NUMERIC_VALIDATION,
                "description": "MRP must be clearly specified with positive numerical value and indication of inclusive tax status.",
                "severity": RuleSeverity.HIGH,
                "legal_reference": "Rule 6(1)(da) of Legal Metrology (Packaged Commodities) Rules, 2011",
                "enabled": True,
            },
            {
                "rule_id": "LMPC-R6-1F",
                "field": "consumer_care",
                "rule_type": RuleType.REQUIRED_FIELD,
                "description": "Name, address, telephone number, and e-mail address of the person or office which can be contacted in case of consumer complaints.",
                "severity": RuleSeverity.HIGH,
                "legal_reference": "Rule 6(1)(f) of Legal Metrology (Packaged Commodities) Rules, 2011",
                "enabled": True,
            },
            {
                "rule_id": "LMPC-R6-10",
                "field": "country_of_origin",
                "rule_type": RuleType.REQUIRED_FIELD,
                "description": "Declaration of Country of Origin on imported or packaged commodity.",
                "severity": RuleSeverity.MEDIUM,
                "legal_reference": "Rule 6(10) of Legal Metrology (Packaged Commodities) Rules, 2011",
                "enabled": True,
            },
            {
                "rule_id": "LMPC-R7-FONT",
                "field": "mrp",
                "rule_type": RuleType.FONT_SIZE_REVIEW,
                "description": "Minimum height of numerals and letters based on package net quantity under Rule 7 Table.",
                "severity": RuleSeverity.MEDIUM,
                "legal_reference": "Rule 7 of Legal Metrology (Packaged Commodities) Rules, 2011",
                "enabled": True,
            },
        ]

        for r_spec in default_rules:
            existing_r = db.query(ComplianceRule).filter(ComplianceRule.rule_id == r_spec["rule_id"]).first()
            if not existing_r:
                rule = ComplianceRule(**r_spec)
                db.add(rule)

        db.commit()
        print("Seeded Legal Metrology 2011 rules successfully!")

        # 3. Seed initial demo inspections if table is empty (Section 30: labeled clearly)
        if db.query(Inspection).count() == 0:
            seed_initial_demo_inspections(db, inspector.id)

    finally:
        db.close()

def seed_initial_demo_inspections(db, inspector_id: int):
    """Creates initial verifiable inspection records in PostgreSQL for immediate dashboard analytics."""
    p1 = Product(
        name="Amul Butter Pasteurized (Demo Record)",
        brand="Amul",
        category="Dairy & Perishables",
        manufacturer="Gujarat Co-operative Milk Marketing Federation Ltd, Anand 388001",
        identifier="8901262010053",
    )
    p2 = Product(
        name="Sunfeast Dark Fantasy Choco Fills (Demo Record)",
        brand="Sunfeast",
        category="Biscuits & Confectionery",
        manufacturer="ITC Limited, 37 J.L. Nehru Road, Kolkata 700071",
        identifier="8901725132339",
    )
    p3 = Product(
        name="Imported Olive Oil Extra Virgin (Demo Record)",
        brand="Borges",
        category="Edible Oils",
        manufacturer="Borges Agricultural & Industrial Edible Oils, Spain",
        identifier="8410179012345",
    )
    db.add_all([p1, p2, p3])
    db.flush()

    # Inspection 1: Compliant
    insp1 = Inspection(
        inspection_number="PC-2026-0001",
        product_id=p1.id,
        inspector_id=inspector_id,
        inspection_date=datetime.utcnow() - timedelta(days=2),
        location="Central Retail Depot, Connaught Place, New Delhi",
        batch_number="B26-09A",
        inspector_remarks="All declarations printed clearly on Principal Display Panel. Standard font verified.",
        overall_status=InspectionStatus.COMPLIANT,
        compliance_score=100.0,
        total_checks=11,
        passed_checks=11,
        violations_count=0,
        manual_review_count=0
    )
    db.add(insp1)
    db.flush()

    # Fields for Insp 1
    fields1 = [
        ExtractedField(inspection_id=insp1.id, field_name="manufacturer", field_value="Gujarat Co-operative Milk Marketing Federation Ltd, Anand 388001, Gujarat", confidence=0.96, status=FieldStatus.DETECTED, original_ocr_text="Mfd by: Gujarat Co-operative Milk Marketing Federation Ltd, Anand 388001", bbox=[50, 100, 450, 160]),
        ExtractedField(inspection_id=insp1.id, field_name="net_quantity", field_value="500 g", unit="g", confidence=0.98, status=FieldStatus.DETECTED, original_ocr_text="Net Qty: 500 g", bbox=[50, 180, 250, 220]),
        ExtractedField(inspection_id=insp1.id, field_name="mrp", field_value="275.00", currency="INR", confidence=0.95, status=FieldStatus.DETECTED, original_ocr_text="MRP ₹275.00 (Incl. of all taxes)", bbox=[50, 230, 320, 270]),
        ExtractedField(inspection_id=insp1.id, field_name="date", field_value="08/2026", confidence=0.92, status=FieldStatus.DETECTED, original_ocr_text="PKD: 08/2026", bbox=[50, 280, 220, 310]),
        ExtractedField(inspection_id=insp1.id, field_name="consumer_care", field_value="Toll-Free: 1800-258-3333 | gcmmf@amul.coop", confidence=0.91, status=FieldStatus.DETECTED, original_ocr_text="Customer Care: 1800-258-3333, gcmmf@amul.coop", bbox=[50, 320, 480, 360]),
        ExtractedField(inspection_id=insp1.id, field_name="country_of_origin", field_value="India", confidence=0.97, status=FieldStatus.DETECTED, original_ocr_text="Made in India", bbox=[50, 370, 200, 400]),
        ExtractedField(inspection_id=insp1.id, field_name="commodity_name", field_value="Butter Pasteurized", confidence=0.94, status=FieldStatus.DETECTED, original_ocr_text="Generic Name: Butter", bbox=[50, 60, 260, 95]),
    ]
    db.add_all(fields1)

    # Inspection 2: Potential Non-Compliance
    insp2 = Inspection(
        inspection_number="PC-2026-0002",
        product_id=p2.id,
        inspector_id=inspector_id,
        inspection_date=datetime.utcnow() - timedelta(days=1),
        location="Supermart Sector 18, Noida",
        batch_number="DF-8812",
        inspector_remarks="Customer care helpline missing from outer wrapper. Non-standard unit format noted.",
        overall_status=InspectionStatus.POTENTIAL_NON_COMPLIANCE,
        compliance_score=63.6,
        total_checks=11,
        passed_checks=7,
        violations_count=2,
        manual_review_count=1
    )
    db.add(insp2)
    db.flush()

    # Fields for Insp 2
    fields2 = [
        ExtractedField(inspection_id=insp2.id, field_name="manufacturer", field_value="ITC Limited, 37 J.L. Nehru Road, Kolkata 700071", confidence=0.94, status=FieldStatus.DETECTED, original_ocr_text="Marketed by ITC Limited, Kolkata 700071", bbox=[60, 110, 460, 160]),
        ExtractedField(inspection_id=insp2.id, field_name="net_quantity", field_value="300 g", unit="g", confidence=0.95, status=FieldStatus.DETECTED, original_ocr_text="Net Wt: 300 g", bbox=[60, 180, 240, 215]),
        ExtractedField(inspection_id=insp2.id, field_name="mrp", field_value="90.00", currency="INR", confidence=0.92, status=FieldStatus.DETECTED, original_ocr_text="MRP: Rs. 90.00", bbox=[60, 225, 290, 260]),
        ExtractedField(inspection_id=insp2.id, field_name="date", field_value="09/2026", confidence=0.88, status=FieldStatus.DETECTED, original_ocr_text="MFD 09/2026", bbox=[60, 270, 210, 305]),
        ExtractedField(inspection_id=insp2.id, field_name="consumer_care", field_value="", confidence=0.0, status=FieldStatus.NOT_DETECTED, original_ocr_text=None, bbox=None),
        ExtractedField(inspection_id=insp2.id, field_name="country_of_origin", field_value="India", confidence=0.95, status=FieldStatus.DETECTED, original_ocr_text="Country of Origin: India", bbox=[60, 315, 240, 345]),
    ]
    db.add_all(fields2)

    # Violations for Insp 2
    viol1 = Violation(
        inspection_id=insp2.id,
        field_name="consumer_care",
        violation_type="MISSING_DECLARATION",
        severity="CRITICAL",
        description="Consumer care details (phone number, email, or contact address) could not be detected on package.",
        evidence_text="No text matching consumer care contact found on inspected surfaces.",
        legal_reference="Rule 6(1)(f) of Legal Metrology (Packaged Commodities) Rules, 2011",
        recommended_action="Conduct physical inspection of individual inner sachet or issue Notice under Rule 6(1)(f)."
    )
    viol2 = Violation(
        inspection_id=insp2.id,
        field_name="mrp",
        violation_type="INVALID_FORMAT",
        severity="HIGH",
        description="MRP declaration detected but explicit statement 'inclusive of all taxes' was not verified.",
        evidence_text="MRP: Rs. 90.00",
        legal_reference="Rule 6(1)(da) of Legal Metrology (Packaged Commodities) Rules, 2011",
        recommended_action="Verify if 'incl. of all taxes' is printed adjacent to retail sale price."
    )
    db.add_all([viol1, viol2])

    # Inspection 3: Manual Review Required
    insp3 = Inspection(
        inspection_number="PC-2026-0003",
        product_id=p3.id,
        inspector_id=inspector_id,
        inspection_date=datetime.utcnow() - timedelta(hours=5),
        location="Port Customs Warehouse, Nhava Sheva",
        batch_number="SP-77124",
        inspector_remarks="Imported batch label with low contrast overwrap. Importer address sticker partially obscured.",
        overall_status=InspectionStatus.MANUAL_REVIEW_REQUIRED,
        compliance_score=72.7,
        total_checks=11,
        passed_checks=8,
        violations_count=1,
        manual_review_count=2
    )
    db.add(insp3)
    db.flush()

    viol3 = Violation(
        inspection_id=insp3.id,
        field_name="date",
        violation_type="READABILITY_ISSUE",
        severity="MEDIUM",
        description="Date of import and packaging has low OCR clarity (58% confidence). Manual verification required.",
        evidence_text="EXP / PKD: 2026 / ??",
        legal_reference="Rule 6(1)(d) of Legal Metrology (Packaged Commodities) Rules, 2011",
        recommended_action="Manually examine laser-etched date code on bottle neck."
    )
    db.add(viol3)

    db.commit()
    print("Seeded initial demo inspection records for live analytics successfully!")

if __name__ == "__main__":
    init_db()
