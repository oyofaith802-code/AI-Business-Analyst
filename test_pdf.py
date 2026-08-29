from pdf_report import create_pdf_report

report = """
AI BUSINESS REPORT

Revenue increased by 15%.

Top region:
Lagos

Recommendation:

Increase marketing in Lagos.
"""

file = create_pdf_report(report)

print(file)