# std
import logging
from os import environ
from os.path import join as path_join, realpath, dirname


FILE_DIR = dirname(realpath(__file__))


# routes


API_PREFIX = "/api"
DEFAULT_INDEX_FILE = "/index.html"  # relative to static directory (personality_test_system/static)

PRE_COLLECT_TESTS_SURVEY_KEYWORD = "tests"
EXPIRES_SURVEY_KEYWORD = "expires"


# flask


STATIC_URL_PATH = ""
STATIC_FOLDER = "../../static"  # relative path from app.py to static directory (personality_test_system/static)

LOG_LEVEL = logging.INFO

PORT = 5000


# database


if environ["DATABASE_URL"].startswith("postgres://"):
    environ["DATABASE_URL"] = environ["DATABASE_URL"].replace("postgres://", "postgresql://", 1)

APP_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': environ["DATABASE_URL"],
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ECHO': False  # if true, all statements will be logged - maybe useful for debugging
}

PRE_COLLECT_TESTS_KEY = "PRE_COLLECT_TESTS"

MAX_HASH_GENERATION_TRY_COUNT = 1000

TOKEN_PERIOD_OF_VALIDITY_IN_DAYS = 14


# certificate pdf


class DefaultCertificateFonts:
    HEADER = ('Arial', 'B', 15)
    BODY = ('Times', '', 12)
    FOOTER = ('Arial', 'I', 8)


class DefaultCertificatePdfConfig:
    LOGO_PATH = path_join(FILE_DIR, "../../static/img/certificate_background.png")  # relative to this file
    TITLE = "Persöhnlichkeitstest Zertifikat"
    HEADER_BORDER = 1
    BODY_TEXT_ALIGN = "C"


DEFAULT_CERTIFICATE_FONTS = DefaultCertificateFonts
DEFAULT_CERTIFICATE_PDF_CONFIG = DefaultCertificatePdfConfig

CERTIFICATE_MIMETYPE = "application/pdf"
