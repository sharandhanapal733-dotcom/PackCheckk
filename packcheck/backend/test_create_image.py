import os
from PIL import Image, ImageDraw, ImageFont

def generate_test_label():
    os.makedirs('test_assets', exist_ok=True)
    img = Image.new('RGB', (1000, 750), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Border
    d.rectangle([(20, 20), (980, 730)], outline=(30, 41, 59), width=3)
    d.rectangle([(25, 25), (975, 725)], fill=(248, 250, 252))

    # Header brand
    d.rectangle([(40, 40), (960, 110)], fill=(30, 58, 138))
    d.text((60, 55), "NUTRIFEAST® ORGANIC COOKIES", fill=(255, 255, 255))
    d.text((60, 85), "GENERIC NAME: OATS & HONEY BISCUITS", fill=(219, 234, 254))

    # Mandatory declarations box
    d.rectangle([(40, 130), (960, 710)], fill=(255, 255, 255), outline=(203, 213, 225), width=2)

    lines = [
        "MANDATORY DECLARATIONS UNDER LEGAL METROLOGY (PC) RULES, 2011",
        "",
        "NET QUANTITY: 400 g",
        "MAXIMUM RETAIL PRICE (MRP): Rs. 140.00 (Inclusive of all taxes)",
        "DATE OF MANUFACTURE (MFD): 08/2026",
        "BEST BEFORE 9 MONTHS FROM DATE OF PACKAGING",
        "BATCH NO: NF-2026/08A",
        "",
        "MANUFACTURED & PACKED BY:",
        "NutriFeast Foods India Pvt Ltd, Plot No 42, Okhla Industrial Area Phase-III,",
        "New Delhi - 110020, India",
        "",
        "CONSUMER CARE DETAILS:",
        "In case of consumer complaints, contact Consumer Care Cell:",
        "Toll-Free Helpline: 1800-112-9988 | Email: care@nutrifeast.in",
        "Address: Same as manufacturer",
        "",
        "COUNTRY OF ORIGIN: INDIA",
    ]

    y = 150
    for line in lines:
        if "MANDATORY" in line:
            d.text((60, y), line, fill=(30, 41, 59))
            y += 28
        elif "NET QUANTITY" in line or "MRP" in line or "DATE" in line:
            d.text((60, y), line, fill=(15, 23, 42))
            y += 32
        else:
            d.text((60, y), line, fill=(51, 65, 85))
            y += 26

    out_path = 'test_assets/cookie_label.jpg'
    img.save(out_path, quality=95)
    print(f"Generated {out_path} successfully!")

if __name__ == '__main__':
    generate_test_label()
