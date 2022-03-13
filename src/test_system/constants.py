# std
import logging
from os import environ
from os.path import join as path_join, realpath, dirname


FILE_DIR = dirname(realpath(__file__))
""" Directory of this file. """


# routes


API_PREFIX = "/api"
""" A prefix which stand before all flask REST routes. """
DEFAULT_INDEX_FILE = "/index.html"  # relative to static directory (personality_test_system/static)
""" Requests to domain root, get redirected to this file. """

PRE_COLLECT_TESTS_SURVEY_KEYWORD = "tests"
EXPIRES_SURVEY_KEYWORD = "expires"


# flask


STATIC_URL_PATH = ""
""" Prefix for REST routes with static content. """
STATIC_FOLDER = "../../static"  # relative path from app.py to static directory (personality_test_system/static)
""" Relative path to root of static files. """

LOG_LEVEL = logging.INFO

PORT = 5000
""" Local running port. """


# database


# ensure consistent DATABASE_URL format:
if environ["DATABASE_URL"].startswith("postgres://"):
    environ["DATABASE_URL"] = environ["DATABASE_URL"].replace("postgres://", "postgresql://", 1)

APP_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': environ["DATABASE_URL"],
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ECHO': False  # if true, all statements will be logged - maybe useful for debugging
}
""" Config of flask app regarding flask-sqlalchemy. """

PRE_COLLECT_TESTS_KEY = "PRE_COLLECT_TESTS"

MAX_HASH_GENERATION_TRY_COUNT = 1000
""" Max tries of hash generations, when an unknown token should be created. """

TOKEN_PERIOD_OF_VALIDITY_IN_DAYS = 21
""" How many days a token is valid, that can expire. """


# certificate pdf


class DefaultCertificateFonts:
    """
    Contains tuples with font config in format (font family, font style, font size).
    """

    HEADER = ('Arial', 'B', 15)
    """ Font config of title. """
    BODY = ('Times', '', 12)
    """ Font config of content. """
    FOOTER = ('Arial', 'I', 8)
    """ Font config of footer information like page number. """


class DefaultCertificatePdfConfig:
    """
    General configs for generating certificates.
    """

    LOGO_PATH = path_join(FILE_DIR, "../../static/img/certificate_background.png")  # relative to this file
    """ Relative path to location of background image of certificate. """
    TITLE = "Persöhnlichkeitstest Zertifikat"
    """ The title on top of the certificate. """
    HEADER_BORDER = True
    """ Whether the title should be surrounded with a border. """
    BODY_TEXT_ALIGN = "C"
    """ Where to align the text in the body (C - center, R - right, L - left). """


DEFAULT_CERTIFICATE_FONTS = DefaultCertificateFonts
DEFAULT_CERTIFICATE_PDF_CONFIG = DefaultCertificatePdfConfig

CERTIFICATE_MIMETYPE = "application/pdf"
""" Must be a valid MIME type - will be included in response header of certificates. """
