# std
from typing import Optional
# 3rd party
from fpdf import FPDF
# custom
from test_system.constants import DEFAULT_CERTIFICATE_FONTS, DEFAULT_CERTIFICATE_PDF_CONFIG


class PDF(FPDF):

    PDF_NEWLINE_LN = 20  # for newline after cells

    def __init__(self, margin_top: Optional[int] = 50):
        super().__init__()
        self.alias_nb_pages()  # to use {nb} as total number of pages
        self.add_page()
        self.set_font(*DEFAULT_CERTIFICATE_FONTS.BODY)
        self.cell(0, margin_top, ln=self.PDF_NEWLINE_LN)

    def add_default_cell(self, text: str = "") -> None:
        self.cell(0, 10, text, 0, self.PDF_NEWLINE_LN, DEFAULT_CERTIFICATE_PDF_CONFIG.BODY_TEXT_ALIGN)

    def get_pdf_bytes(self) -> bytes:
        pdf_str = self.output(dest='S')  # S to get result as string
        pdf_bytes = pdf_str.encode("latin1")
        return pdf_bytes

    def header(self):
        self.image(DEFAULT_CERTIFICATE_PDF_CONFIG.LOGO_PATH, 10, 10, 190)
        self.set_font(*DEFAULT_CERTIFICATE_FONTS.HEADER)  # Arial bold 15
        self.cell(0, 10,
                  DEFAULT_CERTIFICATE_PDF_CONFIG.TITLE,
                  DEFAULT_CERTIFICATE_PDF_CONFIG.HEADER_BORDER,
                  self.PDF_NEWLINE_LN, align='C')  # 20 for line break

    def footer(self):
        self.set_y(-15)  # Position at 1.5 cm from bottom
        self.set_font(*DEFAULT_CERTIFICATE_FONTS.FOOTER)  # Arial italic 8
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', align='C')
