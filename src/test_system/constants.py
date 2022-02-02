# std
import logging
from os import environ


# routes


API_PREFIX = "/api"
DEFAULT_INDEX_FILE = "/index.html"


# flask


STATIC_URL_PATH = ""
STATIC_FOLDER = "../../static"  # relative path from directory of app.py to static dir (personality_test_system/static)

LOG_LEVEL = logging.INFO

PORT = 5000


# database


APP_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': environ["DATABASE_URL"],
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ECHO': False  # if true, all statements will be logged - maybe useful for debugging
}


# certificate pdf


class DefaultCertificateFonts:
    HEADER = ('Arial', 'B', 15)
    BODY = ('Times', '', 12)
    FOOTER = ('Arial', 'I', 8)


class DefaultCertificatePdfConfig:
    LOGO_PATH = "../static/certificate_background.png"  # path relative to run.py
    TITLE = "Persöhnlichkeitstest Zertifikat"
    HEADER_BORDER = 1
    BODY_TEXT_ALIGN = "C"


DEFAULT_CERTIFICATE_FONTS = DefaultCertificateFonts
DEFAULT_CERTIFICATE_PDF_CONFIG = DefaultCertificatePdfConfig
