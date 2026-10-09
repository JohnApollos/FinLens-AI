import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

OUTPUT_DIR = "backend/data/test_documents"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_pdf(filename, title, subtitle, period, currency, scale_note, income_rows, balance_rows, notes_text):
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#1e293b"))
    sub_style = ParagraphStyle("H2", fontName="Helvetica", fontSize=12, leading=16, textColor=colors.HexColor("#64748b"))
    section_style = ParagraphStyle("Sec", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=colors.HexColor("#0f172a"), spaceBefore=12, spaceAfter=6)
    cell_bold = ParagraphStyle("CB", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#1e293b"))
    cell_regular = ParagraphStyle("CR", fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#334155"))
    cell_right = ParagraphStyle("CRight", fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#334155"), alignment=2)
    cell_right_bold = ParagraphStyle("CRightB", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#0f172a"), alignment=2)
    body_style = ParagraphStyle("Body", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#475569"))
    
    story = []
    
    # Header Banner
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(subtitle, sub_style))
    story.append(Paragraph(f"<b>Reporting Period:</b> {period} | <b>Functional Currency:</b> {currency} ({scale_note})", body_style))
    story.append(Spacer(1, 15))
    
    # 1. Income Statement Table
    story.append(Paragraph("Consolidated Statement of Profit or Loss", section_style))
    
    is_table_data = [[
        Paragraph("<b>Financial Line Item</b>", cell_bold),
        Paragraph(f"<b>{period} ({currency})</b>", cell_right_bold)
    ]]
    for item, val in income_rows:
        is_table_data.append([
            Paragraph(item, cell_bold if "Total" in item or "Net" in item or "Profit" in item else cell_regular),
            Paragraph(val, cell_right_bold if "Total" in item or "Net" in item or "Profit" in item else cell_right)
        ])
        
    is_table = Table(is_table_data, colWidths=[4.2 * inch, 2.5 * inch])
    is_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("LINEBELOW", (0, -1), (-1, -1), 1.5, colors.HexColor("#0f172a"))
    ]))
    story.append(is_table)
    story.append(Spacer(1, 15))
    
    # 2. Balance Sheet Table
    story.append(Paragraph("Consolidated Statement of Financial Position", section_style))
    
    bs_table_data = [[
        Paragraph("<b>Financial Line Item</b>", cell_bold),
        Paragraph(f"<b>{period} ({currency})</b>", cell_right_bold)
    ]]
    for item, val in balance_rows:
        bs_table_data.append([
            Paragraph(item, cell_bold if "Total" in item or "Equity" in item else cell_regular),
            Paragraph(val, cell_right_bold if "Total" in item or "Equity" in item else cell_right)
        ])
        
    bs_table = Table(bs_table_data, colWidths=[4.2 * inch, 2.5 * inch])
    bs_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("LINEBELOW", (0, -1), (-1, -1), 1.5, colors.HexColor("#0f172a"))
    ]))
    story.append(bs_table)
    story.append(Spacer(1, 15))
    
    # 3. Notes & Regulatory Disclosures
    story.append(Paragraph("Selected Notes and Regulatory Disclosures", section_style))
    for note in notes_text:
        story.append(Paragraph(f"&bull; {note}", body_style))
        story.append(Spacer(1, 4))
        
    doc.build(story)
    print(f"Generated sample document: {filepath}")

def main():
    # 1. Equity Group Holdings Plc
    generate_pdf(
        filename="Equity_Group_Holdings_2023_Financial_Report.pdf",
        title="Equity Group Holdings Plc",
        subtitle="Annual Integrated Report & Consolidated Financial Statements",
        period="FY 2023",
        currency="KES",
        scale_note="in Millions",
        income_rows=[
            ("Interest income and dividend yields", "148,200.00"),
            ("Non-interest operating revenue & fees", "32,300.00"),
            ("Total Revenue", "180,500.00"),
            ("Total operating expenses & credit impairment", "118,500.00"),
            ("Income tax expense", "18,600.00"),
            ("Total Expenses", "137,100.00"),
            ("Profit for the year / Net Income", "43,400.00")
        ],
        balance_rows=[
            ("Cash and cash equivalents", "112,400.00"),
            ("Government investment securities & deposits", "379,900.00"),
            ("Loans and advances to customers (Net)", "887,200.00"),
            ("Other non-current assets & equipment", "441,900.00"),
            ("Total Assets", "1,821,400.00"),
            ("Customer deposits & current accounts", "1,310,200.00"),
            ("Borrowings and debt securities in issue", "145,200.00"),
            ("Other operating liabilities", "147,900.00"),
            ("Total Liabilities", "1,603,300.00"),
            ("Share capital & share premium", "29,700.00"),
            ("Retained earnings & statutory reserves", "188,400.00"),
            ("Total Shareholders' Equity", "218,100.00"),
            ("Total Liabilities and Equity", "1,821,400.00")
        ],
        notes_text=[
            "<b>Capital Adequacy:</b> The Group maintained a Core Capital to Risk-Weighted Assets ratio of 15.6% and a Total Capital Adequacy Ratio (CAR) of 18.1%, exceeding the CBK statutory minimum of 14.5%.",
            "<b>Liquidity Management:</b> Liquid assets (cash, balances with central banks, and government paper) totaled KES 492,300 Million against customer demand deposits.",
            "<b>Borrowings:</b> Senior and subordinated financial debt stood at KES 145,200 Million. Customer deposits are structural balance sheet funding rather than leverage debt."
        ]
    )
    
    # 2. East African Breweries Limited
    generate_pdf(
        filename="EABL_2023_Annual_Report.pdf",
        title="East African Breweries Limited (EABL)",
        subtitle="Annual Report and Audited Financial Statements",
        period="FY 2023",
        currency="KES",
        scale_note="in Millions",
        income_rows=[
            ("Gross revenue from contract with customers", "109,600.00"),
            ("Cost of sales (materials, production, excise)", "58,100.00"),
            ("Selling and distribution costs", "14,800.00"),
            ("Administrative expenses", "13,600.00"),
            ("Finance costs / Interest expense", "4,700.00"),
            ("Income tax expense", "6,100.00"),
            ("Total Expenses", "97,300.00"),
            ("Profit for the year / Net Income", "12,300.00")
        ],
        balance_rows=[
            ("Property, plant and equipment", "62,500.00"),
            ("Intangible assets & goodwill", "5,600.00"),
            ("Inventories / stock", "14,800.00"),
            ("Trade and other receivables", "11,300.00"),
            ("Cash and cash equivalents", "8,200.00"),
            ("Total Assets", "102,400.00"),
            ("Trade and other payables", "36,400.00"),
            ("Borrowings (current and non-current)", "42,100.00"),
            ("Total Liabilities", "78,500.00"),
            ("Share capital", "5,500.00"),
            ("Retained earnings", "18,400.00"),
            ("Total Shareholders' Equity", "23,900.00"),
            ("Total Liabilities and Equity", "102,400.00")
        ],
        notes_text=[
            "<b>Working Capital:</b> Current assets stood at KES 34,300 Million and current liabilities were KES 38,800 Million, representing working capital of KES -4,500 Million.",
            "<b>Solvency Profile:</b> Altman Z'-Score for private manufacturing positions the entity in the Safe Zone with healthy asset coverage and strong operating margins.",
            "<b>Financial Borrowings:</b> Total bank borrowings and commercial paper totaled KES 42,100 Million."
        ]
    )
    
    # 3. Jubilee Holdings Limited
    generate_pdf(
        filename="Jubilee_Insurance_2023_Annual_Report.pdf",
        title="Jubilee Holdings Limited",
        subtitle="Audited Annual Report and Financial Statements (IFRS 17)",
        period="FY 2023",
        currency="KES",
        scale_note="in Millions",
        income_rows=[
            ("Insurance revenue", "22,780.00"),
            ("Insurance service expenses & claims", "14,210.00"),
            ("Net insurance finance expenses & operating costs", "4,150.00"),
            ("Total Expenses", "18,360.00"),
            ("Net profit for the year / Net Income", "4,420.00")
        ],
        balance_rows=[
            ("Cash and cash equivalents", "2,160.00"),
            ("Term deposits with financial institutions", "7,040.00"),
            ("Government investment securities (backing claims)", "122,300.00"),
            ("Investment property & other admitted assets", "60,200.00"),
            ("Total Assets", "191,700.00"),
            ("Insurance contract liabilities (policyholder reserves)", "129,400.00"),
            ("Other operating payables & provisions", "8,000.00"),
            ("Total Borrowings (commercial financial debt)", "0.00"),
            ("Total Liabilities", "137,400.00"),
            ("Share capital", "20,100.00"),
            ("Retained earnings & statutory reserves", "34,200.00"),
            ("Total Shareholders' Equity", "54,300.00"),
            ("Total Liabilities and Equity", "191,700.00")
        ],
        notes_text=[
            "<b>Solvency Ratio & Capital Adequacy:</b> The company maintained an IRA Risk-Based Capital (RBC) Solvency Ratio of 165.0%, comfortably above the statutory 100.0% threshold.",
            "<b>Zero Financial Debt:</b> Commercial interest-bearing borrowings stood at KES 0.00 in 2023. Total liabilities of KES 137,400 Million represent policyholder reserves matched by KES 131,500 Million in liquid assets and securities.",
            "<b>Asset Matching:</b> Insurance contract liabilities are backed 1:1 by liquid government bonds and bank deposits."
        ]
    )

if __name__ == "__main__":
    main()
