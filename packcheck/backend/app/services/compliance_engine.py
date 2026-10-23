import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.rule import ComplianceRule, RuleType, RuleSeverity
from app.models.inspection import (
    CheckStatus,
    InspectionStatus,
    ComplianceResult,
    Violation
)

# Standard units under Second Schedule of Legal Metrology (Packaged Commodities) Rules, 2011
VALID_WEIGHT_UNITS = {"g", "kg", "mg"}
VALID_VOLUME_UNITS = {"ml", "l", "L"}
VALID_LENGTH_UNITS = {"m", "cm", "mm"}
VALID_NUMBER_UNITS = {"N", "U"}
ALL_VALID_UNITS = VALID_WEIGHT_UNITS | VALID_VOLUME_UNITS | VALID_LENGTH_UNITS | VALID_NUMBER_UNITS

class ComplianceEngine:
    """
    Evaluates extracted fields against Legal Metrology (Packaged Commodities) Rules, 2011.
    Generates rule results, transparent compliance score, and flagged violations.
    """

    @classmethod
    def evaluate(
        cls,
        extracted_fields: Dict[str, Dict[str, Any]],
        rules: List[ComplianceRule],
        ocr_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Runs all active rules against the extracted declarations.
        Returns:
        {
            "overall_status": InspectionStatus,
            "compliance_score": float,
            "total_checks": int,
            "passed_checks": int,
            "violations_count": int,
            "manual_review_count": int,
            "results": List[Dict],
            "violations": List[Dict]
        }
        """
        results: List[Dict[str, Any]] = []
        violations: List[Dict[str, Any]] = []

        total_checks = 0
        passed_checks = 0
        manual_review_count = 0
        failed_count = 0

        # Map rules by field
        for rule in rules:
            if not rule.enabled:
                continue

            total_checks += 1
            field_key = rule.field
            field_data = extracted_fields.get(field_key, {})
            status = field_data.get("status", "NOT_DETECTED")
            val = field_data.get("value")
            conf = field_data.get("confidence", 0.0)
            orig_text = field_data.get("original_ocr_text", "")
            bbox = field_data.get("bbox")

            rule_res_status = CheckStatus.PASS
            severity_str = rule.severity.value if hasattr(rule.severity, "value") else str(rule.severity)
            message = ""
            violation_type = None
            rec_action = None

            # 1. REQUIRED FIELD CHECK
            if rule.rule_type == RuleType.REQUIRED_FIELD:
                if status == "NOT_DETECTED" or not val:
                    rule_res_status = CheckStatus.MANUAL_REVIEW
                    message = f"{rule.field.replace('_', ' ').title()} declaration was not detected in the provided images."
                    violation_type = "MISSING_DECLARATION"
                    rec_action = f"Inspect other sides of the package. If missing, this constitutes potential non-compliance under {rule.legal_reference}."
                elif conf < 0.60:
                    rule_res_status = CheckStatus.WARNING
                    message = f"{rule.field.replace('_', ' ').title()} was detected with low OCR confidence ({int(conf * 100)}%). Manual verification required."
                    violation_type = "LOW_OCR_CONFIDENCE"
                    rec_action = "Review package image to confirm text accuracy or manually correct the declaration."
                else:
                    rule_res_status = CheckStatus.PASS
                    message = f"Mandatory declaration '{rule.field.replace('_', ' ').title()}' successfully detected ({int(conf * 100)}% confidence)."

            # 2. NUMERIC & UNIT VALIDATION (Net Quantity & MRP)
            elif rule.rule_type == RuleType.NUMERIC_VALIDATION:
                if status != "NOT_DETECTED" and val:
                    if field_key == "net_quantity":
                        unit = field_data.get("unit")
                        if not unit or unit not in ALL_VALID_UNITS:
                            rule_res_status = CheckStatus.FAIL
                            message = f"Net quantity unit '{unit}' is not a recognized standard unit under the Second Schedule."
                            violation_type = "INVALID_FORMAT"
                            rec_action = f"Ensure net quantity is specified in legal units (g, kg, ml, L, N, U) as per {rule.legal_reference}."
                        else:
                            rule_res_status = CheckStatus.PASS
                            message = f"Valid standard metric/unit declaration detected: {val}."

                    elif field_key == "mrp":
                        num_val = field_data.get("numeric_value")
                        has_taxes = field_data.get("inclusive_of_taxes", False)
                        if num_val is None or num_val <= 0:
                            rule_res_status = CheckStatus.FAIL
                            message = "MRP declaration does not contain a valid positive retail price."
                            violation_type = "INVALID_FORMAT"
                            rec_action = f"Check package for legible price statement in accordance with {rule.legal_reference}."
                        elif not has_taxes:
                            rule_res_status = CheckStatus.WARNING
                            message = "MRP declaration detected but explicit statement 'inclusive of all taxes' requires manual review."
                            violation_type = "INVALID_FORMAT"
                            rec_action = "Verify if 'incl. of all taxes' or similar phrasing is legibly printed alongside MRP."
                        else:
                            rule_res_status = CheckStatus.PASS
                            message = f"Valid Retail Sale Price detected: ₹{num_val:.2f} (inclusive of all taxes)."
                else:
                    rule_res_status = CheckStatus.MANUAL_REVIEW
                    message = f"Cannot perform numeric validation: {field_key.replace('_', ' ').title()} not detected."

            # 3. DATE VALIDATION
            elif rule.rule_type == RuleType.DATE_VALIDATION:
                if status != "NOT_DETECTED" and val:
                    # Legal Metrology requires month and year of manufacture or packing
                    valid_date_format = bool(re.search(r'[0-9]{1,2}[\/\-\.][0-9]{2,4}|[A-Za-z]{3,}[\s\-\/\.][0-9]{2,4}', str(val)))
                    if valid_date_format:
                        rule_res_status = CheckStatus.PASS
                        message = f"Valid month/year date declaration detected: '{val}'."
                    else:
                        rule_res_status = CheckStatus.WARNING
                        message = f"Date declaration format '{val}' requires manual verification for Month & Year compliance."
                        violation_type = "INVALID_FORMAT"
                        rec_action = f"Verify month and year format as required by {rule.legal_reference}."
                else:
                    rule_res_status = CheckStatus.MANUAL_REVIEW
                    message = "Month and year of manufacture/packing not detected. Manual review required."
                    violation_type = "MISSING_DECLARATION"
                    rec_action = "Check physical package for embossed or ink-jet printed date."

            # 4. FONT SIZE & READABILITY REVIEW
            elif rule.rule_type == RuleType.FONT_SIZE_REVIEW or rule.rule_type == RuleType.TEXT_READABILITY:
                # Estimate text height in pixels from bounding box if present
                if bbox and len(bbox) == 4:
                    pixel_height = abs(bbox[3] - bbox[1])
                    if pixel_height < 12:
                        rule_res_status = CheckStatus.WARNING
                        message = f"Estimated text height is small ({pixel_height}px). Visual readability requires manual verification."
                        violation_type = "READABILITY_ISSUE"
                        rec_action = "Verify minimum character height in millimeters on physical package using calibrated optical scale."
                    else:
                        rule_res_status = CheckStatus.PASS
                        message = f"Declaration text is legible with sufficient pixel resolution ({pixel_height}px estimated height)."
                else:
                    rule_res_status = CheckStatus.MANUAL_REVIEW
                    message = "Image calibration not available. Physical font height must be verified manually."

            # 5. PATTERN & DETAILS VALIDATION (Consumer Care / Manufacturer Address)
            elif rule.rule_type == RuleType.PATTERN_VALIDATION:
                if status != "NOT_DETECTED" and val:
                    if field_key == "consumer_care":
                        has_phone = bool(field_data.get("phone"))
                        has_email = bool(field_data.get("email"))
                        if not has_phone and not has_email:
                            rule_res_status = CheckStatus.WARNING
                            message = "Consumer care detected, but specific phone number or email could not be extracted automatically."
                            violation_type = "INVALID_FORMAT"
                            rec_action = f"Confirm whether helpline number, email, or physical address is provided as required by {rule.legal_reference}."
                        else:
                            rule_res_status = CheckStatus.PASS
                            details = []
                            if has_phone: details.append(f"Phone: {field_data['phone']}")
                            if has_email: details.append(f"Email: {field_data['email']}")
                            message = f"Consumer Care details confirmed ({', '.join(details)})."

                    elif field_key == "manufacturer":
                        # Check if address contains postal code (6 digits for India) or location keywords
                        has_pincode = bool(re.search(r'\b[1-9][0-9]{5}\b', str(val)))
                        if len(str(val).split()) < 3:
                            rule_res_status = CheckStatus.WARNING
                            message = "Manufacturer name detected but address appears incomplete. Complete address required."
                            violation_type = "INVALID_FORMAT"
                            rec_action = f"Verify complete street/factory address and postal pin code per {rule.legal_reference}."
                        else:
                            rule_res_status = CheckStatus.PASS
                            message = f"Manufacturer/Packer entity and address identified ({str(val)[:60]}...)."
                else:
                    rule_res_status = CheckStatus.MANUAL_REVIEW
                    message = f"Mandatory {field_key.replace('_', ' ').title()} could not be verified."

            # Tabulate counts
            if rule_res_status == CheckStatus.PASS:
                passed_checks += 1
            elif rule_res_status in (CheckStatus.FAIL, CheckStatus.WARNING, CheckStatus.MANUAL_REVIEW):
                if rule_res_status == CheckStatus.FAIL:
                    failed_count += 1
                elif rule_res_status == CheckStatus.MANUAL_REVIEW:
                    manual_review_count += 1

                # Record violation / review item if not pass
                if violation_type:
                    violations.append({
                        "field_name": field_key,
                        "violation_type": violation_type,
                        "severity": severity_str,
                        "description": message,
                        "evidence_text": orig_text or "No text detected in OCR output",
                        "legal_reference": rule.legal_reference,
                        "recommended_action": rec_action or "Inspector manual inspection advised."
                    })

            results.append({
                "rule_id": rule.rule_id,
                "field_name": field_key,
                "status": rule_res_status,
                "severity": severity_str,
                "message": message,
                "legal_reference": rule.legal_reference,
                "evidence": {
                    "text": orig_text,
                    "confidence": conf,
                    "bbox": bbox
                }
            })

        # Calculate transparent compliance score
        applicable_checks = total_checks if total_checks > 0 else 1
        compliance_score = round((passed_checks / applicable_checks) * 100, 1)

        # Determine overall screening status
        if failed_count > 0:
            overall_status = InspectionStatus.POTENTIAL_NON_COMPLIANCE
        elif manual_review_count > 0 or len(violations) > 0:
            overall_status = InspectionStatus.MANUAL_REVIEW_REQUIRED
        else:
            overall_status = InspectionStatus.COMPLIANT

        return {
            "overall_status": overall_status,
            "compliance_score": compliance_score,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "violations_count": len(violations),
            "manual_review_count": manual_review_count,
            "results": results,
            "violations": violations
        }
