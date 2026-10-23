import re
from typing import List, Dict, Any, Optional

class FieldExtractor:
    """
    Structured extraction layer for Legal Metrology (Packaged Commodities) declarations.
    Parses OCR text blocks and links extracted entities to bounding box evidence.
    """

    @classmethod
    def extract_all(cls, ocr_results: List[Dict[str, Any]], image_id: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        full_text_lines = [r["text"] for r in ocr_results]

        extracted = {
            "manufacturer": cls.extract_manufacturer(ocr_results, full_text_lines, image_id),
            "net_quantity": cls.extract_net_quantity(ocr_results, full_text_lines, image_id),
            "mrp": cls.extract_mrp(ocr_results, full_text_lines, image_id),
            "date": cls.extract_date(ocr_results, full_text_lines, image_id),
            "consumer_care": cls.extract_consumer_care(ocr_results, full_text_lines, image_id),
            "country_of_origin": cls.extract_country_of_origin(ocr_results, full_text_lines, image_id),
            "commodity_name": cls.extract_commodity_name(ocr_results, full_text_lines, image_id),
        }
        return extracted

    @classmethod
    def extract_mrp(cls, ocr_results: List[Dict[str, Any]], lines: List[str], image_id: Optional[int]) -> Dict[str, Any]:
        """
        Detects Maximum Retail Price declarations:
        e.g., 'MRP ₹50.00', 'MAXIMUM RETAIL PRICE (MRP): Rs. 140.00 (Inclusive of all taxes)', 'MRP: 25.00'
        """
        # 1. Any line containing MRP / Retail Price keywords
        mrp_kw = re.compile(r'(?i)\b(?:M\.?\s*R\.?\s*P\.?|MAX(?:IMUM)?\s*RETAIL\s*PRICE|RETAIL\s*PRICE)\b')
        price_num = re.compile(r'(?:[₹\u20B9]|Rs\.?|INR)?\s*([0-9]+(?:[\.,][0-9]{1,2})?)', re.IGNORECASE)

        for i, item in enumerate(ocr_results):
            raw = item["text"]
            if mrp_kw.search(raw):
                # Search for currency or numbers in this line
                has_tax_mention = bool(re.search(r'(?i)incl|tax', raw))
                # Look for number after the keyword
                match = re.search(r'(?:[₹\u20B9]|Rs\.?|INR|\:|\s)\s*([0-9]+(?:\.[0-9]{1,2}))', raw, re.IGNORECASE)
                if not match:
                    # Match any positive float or integer
                    match = re.search(r'\b([0-9]+(?:\.[0-9]{1,2})?)\b', raw)

                if match:
                    try:
                        val = float(match.group(1))
                        if val > 0:
                            if not has_tax_mention and i + 1 < len(ocr_results):
                                has_tax_mention = bool(re.search(r'(?i)incl.*tax', ocr_results[i+1]["text"]))

                            return {
                                "field_name": "mrp",
                                "value": f"₹{val:.2f}",
                                "numeric_value": val,
                                "currency": "INR",
                                "status": "DETECTED",
                                "confidence": item["confidence"],
                                "original_ocr_text": raw,
                                "inclusive_of_taxes": has_tax_mention,
                                "bbox": item["box"],
                                "image_id": image_id
                            }
                    except ValueError:
                        pass

                # Check if price is in the immediately following line
                if i + 1 < len(ocr_results):
                    next_item = ocr_results[i + 1]
                    next_match = re.search(r'(?:[₹\u20B9]|Rs\.?|INR)?\s*([0-9]+(?:\.[0-9]{1,2})?)', next_item["text"], re.IGNORECASE)
                    if next_match:
                        try:
                            val = float(next_match.group(1))
                            if val > 0:
                                return {
                                    "field_name": "mrp",
                                    "value": f"₹{val:.2f}",
                                    "numeric_value": val,
                                    "currency": "INR",
                                    "status": "DETECTED",
                                    "confidence": min(item["confidence"], next_item["confidence"]),
                                    "original_ocr_text": f"{raw} {next_item['text']}",
                                    "inclusive_of_taxes": bool(re.search(r'(?i)incl|tax', f"{raw} {next_item['text']}")),
                                    "bbox": next_item["box"],
                                    "image_id": image_id
                                }
                        except ValueError:
                            pass

        return {
            "field_name": "mrp",
            "value": None,
            "status": "NOT_DETECTED",
            "confidence": 0.0,
            "original_ocr_text": None,
            "bbox": None,
            "image_id": image_id
        }

    @classmethod
    def extract_net_quantity(cls, ocr_results: List[Dict[str, Any]], lines: List[str], image_id: Optional[int]) -> Dict[str, Any]:
        """
        Detects Net Quantity declarations:
        e.g., 'NETQUANTITY: 400 g', '500 g', '1 kg', 'Net Wt. 250ml', 'Net Quantity: 1 L', '2 N', '10 Units'
        """
        qty_pattern = re.compile(
            r'(?:(?:NET\s*(?:QTY|QUANTITY|WT|WEIGHT)?|QUANTITY|QTY|CONTENT(?:S)?)\s*[:\-\.]?\s*)?([0-9]+(?:\.[0-9]+)?)\s*(kg|g|gm|gms|grams?|ml|l|ltr|litres?|liter|mg|n|u|units?|pcs?|pieces?)\b',
            re.IGNORECASE
        )

        for item in ocr_results:
            raw = item["text"]
            m = qty_pattern.search(raw)
            if m:
                val = m.group(1)
                unit_raw = m.group(2).lower()
                unit_map = {
                    'g': 'g', 'gm': 'g', 'gms': 'g', 'gram': 'g', 'grams': 'g',
                    'kg': 'kg', 'kilogram': 'kg', 'kilograms': 'kg',
                    'ml': 'ml', 'milli-liter': 'ml',
                    'l': 'L', 'ltr': 'L', 'liter': 'L', 'litres': 'L',
                    'mg': 'mg',
                    'n': 'N', 'u': 'U', 'unit': 'U', 'units': 'U', 'pc': 'N', 'pcs': 'N', 'piece': 'N'
                }
                std_unit = unit_map.get(unit_raw, unit_raw.upper())
                return {
                    "field_name": "net_quantity",
                    "value": f"{val} {std_unit}",
                    "numeric_value": float(val),
                    "unit": std_unit,
                    "status": "DETECTED",
                    "confidence": item["confidence"],
                    "original_ocr_text": raw,
                    "bbox": item["box"],
                    "image_id": image_id
                }

        return {
            "field_name": "net_quantity",
            "value": None,
            "status": "NOT_DETECTED",
            "confidence": 0.0,
            "original_ocr_text": None,
            "bbox": None,
            "image_id": image_id
        }

    @classmethod
    def extract_manufacturer(cls, ocr_results: List[Dict[str, Any]], lines: List[str], image_id: Optional[int]) -> Dict[str, Any]:
        """
        Detects Manufacturer / Packer / Importer entity and address.
        Filters out manufacturing date lines.
        """
        mfg_header = re.compile(
            r'(?i)\b(?:MANUFAC\s*TURED|PACKED|PKD|PRODUCED|IMPORTED|MARKETED)\s*(?:&|AND)?\s*(?:PACKED|MFD|MARKETED)?\s*(?:BY|AT)?\s*[:\-\.]?'
        )

        for i, item in enumerate(ocr_results):
            raw = item["text"]
            # Exclude date lines
            if re.search(r'(?i)\b(?:DATE|MFD|EXP|BEST\s*BEFORE)\b', raw):
                continue

            if mfg_header.search(raw):
                collected = [raw]
                best_conf = item["confidence"]
                box = item["box"]

                j = i + 1
                while j < len(ocr_results) and j <= i + 3:
                    nxt = ocr_results[j]["text"]
                    if re.search(r'(?i)(?:CONSUMER|CUSTOMER|HELPLINE|FEEDBACK|COMPLAINT|MRP|NET\s*QTY|NET\s*QUANTITY|NETQUANTITY|DATE|BATCH|ORIGIN|COUNTRY)', nxt):
                        break
                    collected.append(nxt)
                    j += 1

                combined = " ".join(collected).strip()
                cleaned = mfg_header.sub('', combined).strip(' :-,')
                if not cleaned:
                    cleaned = combined

                return {
                    "field_name": "manufacturer",
                    "value": cleaned,
                    "status": "DETECTED",
                    "confidence": best_conf,
                    "original_ocr_text": combined,
                    "bbox": box,
                    "image_id": image_id
                }

        # Fallback: check for Pvt Ltd / Limited / Industries in lines
        for i, item in enumerate(ocr_results):
            raw = item["text"]
            if re.search(r'(?i)\b(?:Pvt\s*Ltd|Limited|Industries|Enterprises|Foods)\b', raw):
                collected = [raw]
                if i + 1 < len(ocr_results):
                    nxt = ocr_results[i + 1]["text"]
                    if not re.search(r'(?i)(?:CONSUMER|CUSTOMER|HELPLINE|FEEDBACK|COMPLAINT|MRP|NET|DATE|BATCH|ORIGIN|COUNTRY)', nxt):
                        collected.append(nxt)
                combined = " ".join(collected)
                return {
                    "field_name": "manufacturer",
                    "value": combined,
                    "status": "DETECTED",
                    "confidence": item["confidence"],
                    "original_ocr_text": combined,
                    "bbox": item["box"],
                    "image_id": image_id
                }

        return {
            "field_name": "manufacturer",
            "value": None,
            "status": "NOT_DETECTED",
            "confidence": 0.0,
            "original_ocr_text": None,
            "bbox": None,
            "image_id": image_id
        }

    @classmethod
    def extract_date(cls, ocr_results: List[Dict[str, Any]], lines: List[str], image_id: Optional[int]) -> Dict[str, Any]:
        """
        Detects Date of Manufacture / Packing / Use By:
        e.g., 'DATEOF MANUFAC TURE (MFD): 08/2026', 'PKD: 08/2026', '08/2026'
        """
        date_pattern = re.compile(
            r'(?:MFD|MFG|PKD|PACKED|MANUFAC\s*TURE|USE\s*BY|EXP(?:IRY)?|DATE)\s*(?:ON|OF\s*MFG|OF\s*PKD|OF\s*MANUFAC\s*TURE)?(?:\s*\([^\)]*\))?\s*[:\-\.]?\s*([0-9]{1,2}[\/\-\.][0-9]{2,4}|(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[a-z]*[\s\-\/\.][0-9]{2,4})',
            re.IGNORECASE
        )

        for item in ocr_results:
            raw = item["text"]
            m = date_pattern.search(raw)
            if m:
                detected_date = m.group(1)
                decl_type = "EXPIRY" if re.search(r'(?i)\b(EXP|USE\s*BY)\b', raw) else "MFD/PKD"
                return {
                    "field_name": "date",
                    "value": detected_date,
                    "date_type": decl_type,
                    "status": "DETECTED",
                    "confidence": item["confidence"],
                    "original_ocr_text": raw,
                    "bbox": item["box"],
                    "image_id": image_id
                }

        # Standalone date pattern fallback
        for item in ocr_results:
            raw = item["text"]
            if re.search(r'(?i)\b(DATE|MFD|PKD|PACK)\b', raw):
                m = re.search(r'\b([0-9]{1,2}[\/\-\.](?:20)?[0-9]{2})\b', raw)
                if m:
                    return {
                        "field_name": "date",
                        "value": m.group(1),
                        "date_type": "MFD/PKD",
                        "status": "DETECTED",
                        "confidence": item["confidence"],
                        "original_ocr_text": raw,
                        "bbox": item["box"],
                        "image_id": image_id
                    }

        return {
            "field_name": "date",
            "value": None,
            "status": "NOT_DETECTED",
            "confidence": 0.0,
            "original_ocr_text": None,
            "bbox": None,
            "image_id": image_id
        }

    @classmethod
    def extract_consumer_care(cls, ocr_results: List[Dict[str, Any]], lines: List[str], image_id: Optional[int]) -> Dict[str, Any]:
        """
        Detects Consumer Care contact details:
        e.g., 'Toll-Free Helpline: 1800-112-9988 | Email: care@nutrifeast.in'
        """
        cc_keywords = re.compile(
            r'(?i)(?:CONSUMER\s*CARE|CUSTOMER\s*CARE|HELPLINE|FEEDBACK|COMPLAINT|CONSUMERCAREDETAILS)'
        )
        phone_pattern = re.compile(r'(?:(?:1800|1860)[\s\-]?[0-9]{3}[\s\-]?[0-9]{3,4}|\+?91[\s\-]?[0-9]{10}|[0-9]{10,11})')
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+\s*@\s*[a-zA-Z0-9.-]+\s*\.?[a-zA-Z]{2,}')

        for i, item in enumerate(ocr_results):
            raw = item["text"]
            if cc_keywords.search(raw) or phone_pattern.search(raw):
                contacts = [raw]
                best_conf = item["confidence"]
                box = item["box"]

                j = i + 1
                while j < len(ocr_results) and j <= i + 3:
                    nxt = ocr_results[j]["text"]
                    if cc_keywords.search(nxt) or phone_pattern.search(nxt) or email_pattern.search(nxt) or "address" in nxt.lower():
                        contacts.append(nxt)
                    j += 1

                combined = " | ".join(contacts)
                emails = email_pattern.findall(combined)
                clean_email = None
                if emails:
                    e = emails[0].replace(" ", "")
                    if not re.search(r'\.[a-zA-Z]{2,}$', e):
                        e = re.sub(r'([a-zA-Z0-9]+)(in|com|org|co|gov|net)$', r'\1.\2', e)
                    clean_email = e

                phones = phone_pattern.findall(combined)
                clean_phone = phones[0].replace(" ", "-") if phones else None

                return {
                    "field_name": "consumer_care",
                    "value": combined,
                    "email": clean_email,
                    "phone": clean_phone,
                    "status": "DETECTED",
                    "confidence": best_conf,
                    "original_ocr_text": combined,
                    "bbox": box,
                    "image_id": image_id
                }

        return {
            "field_name": "consumer_care",
            "value": None,
            "status": "NOT_DETECTED",
            "confidence": 0.0,
            "original_ocr_text": None,
            "bbox": None,
            "image_id": image_id
        }

    @classmethod
    def extract_country_of_origin(cls, ocr_results: List[Dict[str, Any]], lines: List[str], image_id: Optional[int]) -> Dict[str, Any]:
        """
        Detects Country of Origin:
        Handles OCR variations like 'COUN TRY OF ORIGIN INDIA', 'Made in India', 'Country of Origin: India'
        """
        origin_pattern = re.compile(
            r'(?i)(?:COUN\s*TRY\s*OF\s*ORIGIN|MADE\s*IN|PRODUCT\s*OF)\s*[:\-\.]?\s*([a-zA-Z\s]+)'
        )

        for item in ocr_results:
            raw = item["text"]
            m = origin_pattern.search(raw)
            if m:
                origin = m.group(1).strip()
                return {
                    "field_name": "country_of_origin",
                    "value": origin or "India",
                    "status": "DETECTED",
                    "confidence": item["confidence"],
                    "original_ocr_text": raw,
                    "bbox": item["box"],
                    "image_id": image_id
                }

        # Fallback check
        for item in ocr_results:
            raw = item["text"].upper()
            if "ORIGIN" in raw and "INDIA" in raw:
                return {
                    "field_name": "country_of_origin",
                    "value": "India",
                    "status": "DETECTED",
                    "confidence": item["confidence"],
                    "original_ocr_text": item["text"],
                    "bbox": item["box"],
                    "image_id": image_id
                }
            if "MADE IN INDIA" in raw:
                return {
                    "field_name": "country_of_origin",
                    "value": "India",
                    "status": "DETECTED",
                    "confidence": item["confidence"],
                    "original_ocr_text": item["text"],
                    "bbox": item["box"],
                    "image_id": image_id
                }

        return {
            "field_name": "country_of_origin",
            "value": None,
            "status": "NOT_DETECTED",
            "confidence": 0.0,
            "original_ocr_text": None,
            "bbox": None,
            "image_id": image_id
        }

    @classmethod
    def extract_commodity_name(cls, ocr_results: List[Dict[str, Any]], lines: List[str], image_id: Optional[int]) -> Dict[str, Any]:
        """
        Detects Generic Name of Commodity:
        e.g., 'GENERIC NAME: OATS & HONEY BISCUITS'
        """
        name_pattern = re.compile(
            r'(?i)(?:GENERIC\s*NAME|COMMODITY|PRODUCT\s*NAME)\s*[:\-\.]?\s*([a-zA-Z0-9\s&]+)'
        )

        for item in ocr_results:
            raw = item["text"]
            m = name_pattern.search(raw)
            if m:
                val = m.group(1).strip()
                if len(val) > 2:
                    return {
                        "field_name": "commodity_name",
                        "value": val,
                        "status": "DETECTED",
                        "confidence": item["confidence"],
                        "original_ocr_text": raw,
                        "bbox": item["box"],
                        "image_id": image_id
                    }

        return {
            "field_name": "commodity_name",
            "value": None,
            "status": "NOT_DETECTED",
            "confidence": 0.0,
            "original_ocr_text": None,
            "bbox": None,
            "image_id": image_id
        }
