# std
from typing import Optional, Dict
# 3rd party
from fpdf import FPDF
from yaml import safe_dump
# custom
from test_system.constants import DEFAULT_PDF_FONTS, DEFAULT_PDF_CONFIG


class PDF(FPDF):
    """
    Can be used to create PDFs, which should use the DEFAULT_PDF_FONTS & DEFAULT_PDF_CONFIG.
    So only the text of the body must be set, using the add_default_cell method to write lines.
    The PDF bytes can be obtained by calling the get_pdf_bytes method.
    """

    PDF_NEWLINE_LN = 20  # for newline after cells

    def __init__(self, margin_top: Optional[int] = 10):
        super().__init__()
        self.alias_nb_pages()  # to use {nb} as total number of pages
        self.add_page()
        self.set_font(*DEFAULT_PDF_FONTS.BODY)
        self.cell(0, margin_top, ln=self.PDF_NEWLINE_LN)

    def add_formatted_json(self, data: Dict):
        formatted_answers = safe_dump(data, allow_unicode=True, sort_keys=False,
                                      indent=DEFAULT_PDF_CONFIG.YAML_INDENT).strip()
        formatted_answer_lines = formatted_answers.split("\n")
        for answer_line in formatted_answer_lines:
            self.set_x(DEFAULT_PDF_CONFIG.YAML_LEFT_MARGIN)
            self.add_default_cell(answer_line, text_align=DEFAULT_PDF_CONFIG.YAML_TEXT_ALIGN)

    def add_default_cell(self, text: str = "", text_align: Optional[str] = None) -> None:
        """
        Adds the text as one line to the body of PDF.
        If no text is passed, an empty line will be added.
        """
        self.multi_cell(0, 10, text, 0, text_align or DEFAULT_PDF_CONFIG.DEFAULT_TEXT_ALIGN)

    def get_pdf_bytes(self) -> bytes:
        """
        Creates the actual PDF and returns the PDF bytes.
        """
        pdf_str = self.output(dest='S')  # S to get result as string
        pdf_bytes = pdf_str.encode("latin1")
        return pdf_bytes

    # Override
    def header(self):
        if DEFAULT_PDF_CONFIG.LOGO_PATH is not None:
            self.image(DEFAULT_PDF_CONFIG.LOGO_PATH, 180, 25, 20)
        self.set_font(*DEFAULT_PDF_FONTS.HEADER)  # Arial bold 15
        self.cell(0, 10,
                  DEFAULT_PDF_CONFIG.TITLE,
                  DEFAULT_PDF_CONFIG.HEADER_BORDER,
                  self.PDF_NEWLINE_LN, align='C')  # 20 for line break

    # Override
    def footer(self):
        self.set_y(-15)  # Position at 1.5 cm from bottom
        self.set_font(*DEFAULT_PDF_FONTS.FOOTER)  # Arial italic 8
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', align='C')
