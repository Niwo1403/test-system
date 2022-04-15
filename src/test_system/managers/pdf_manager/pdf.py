# std
from typing import Optional, Dict
from tempfile import NamedTemporaryFile
from binascii import a2b_base64
from os import unlink as delete_file
# 3rd party
from fpdf import FPDF
from yaml import safe_dump
# custom
from test_system.constants import DEFAULT_PDF_FONTS, DEFAULT_PDF_CONFIG, DATA_URL_START, BASE64_SEPARATOR


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

    def add_formatted_json(self, data: Dict) -> None:
        """
        Formats the data in YAML style and adds it to the PDF.
        """
        formatted_answers = safe_dump(data, allow_unicode=True, sort_keys=False,
                                      indent=DEFAULT_PDF_CONFIG.YAML_INDENT).strip()
        formatted_answer_lines = formatted_answers.split("\n")
        for answer_line in formatted_answer_lines:
            self._add_indented_default_cell(answer_line)

    def add_titled_data_urls(self, titled_data_urls: Dict[str, str]) -> None:
        """
        Adds the titled_data_urls to the PDF.
        The titled_data_urls should be a dictionary with the image titles as key and the data-URIs as value.
        """
        for title, data_url in titled_data_urls.items():
            image_type, img_str = data_url[len(DATA_URL_START):].split(BASE64_SEPARATOR, maxsplit=1)
            img_bytes = a2b_base64(img_str)
            self.add_image(img_bytes, image_type=image_type, title=title)

    def add_image(self, image_bytes: bytes, image_type: str, title: Optional[str] = None) -> None:
        """
        Adds an image to the pdf, which is given as image_bytes.
        To identify the image encoding, set the matching image_type.
        If a title is given, it will be displayed above the image.
        """
        with NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(image_bytes)
            tmp_file.seek(0)
            if title is not None:
                self._add_indented_default_cell(f"{title}:")
            self.set_x(DEFAULT_PDF_CONFIG.YAML_LEFT_MARGIN)
            self.image(tmp_file.name, type=image_type)
            tmp_file.close()
            delete_file(tmp_file.name)

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

    def _add_indented_default_cell(self, text: str) -> None:
        self.set_x(DEFAULT_PDF_CONFIG.YAML_LEFT_MARGIN)
        self.add_default_cell(text, text_align=DEFAULT_PDF_CONFIG.YAML_TEXT_ALIGN)
