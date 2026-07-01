import pdfplumber


def pdf_to_text(pdf_path: str) -> str:
    """
    Extract text from all pages of a PDF.
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    return text.strip()
