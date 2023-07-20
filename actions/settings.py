"""
Django settings for actions project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

from environs import Env


env = Env()
env.read_env()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django_extensions",
    "django_vite",
    "actions.apps.ActionsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "actions.middleware.XSSFilteringMiddleware",
]

ROOT_URLCONF = "actions.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "actions.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {"default": env.dj_db_url("DATABASE_URL", "sqlite:///db.sqlite3")}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "assets", "dist"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

DJANGO_VITE_ASSETS_PATH = "/static/"
DJANGO_VITE_DEV_MODE = env.bool("DJANGO_VITE_DEV_MODE", default=False)
DJANGO_VITE_DEV_SERVER_PORT = 5173
DJANGO_VITE_MANIFEST_PATH = os.path.join(BASE_DIR, "staticfiles", "manifest.json")

# Insert Whitenoise Middleware.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# CSP
# https://django-csp.readthedocs.io/en/latest/configuration.html
CSP_REPORT_ONLY = DEBUG
CSP_DEFAULT_SRC = ["'none'"]
CSP_CONNECT_SRC = ["https://plausible.io"]
CSP_FONT_SRC = ["'self'"]
CSP_IMG_SRC = ["'self'", "https://user-images.githubusercontent.com"]
CSP_MANIFEST_SRC = ["'self'"]
CSP_SCRIPT_SRC = CSP_SCRIPT_SRC_ELEM = ["'self'", "https://plausible.io"]
CSP_STYLE_SRC = CSP_STYLE_SRC_ELEM = ["'self'"]

# which directives to set a nonce for
CSP_INCLUDE_NONCE_IN = ["script-src", "script-src-elem"]

# configure django-csp to work with Vite when using it in dev mode
if DJANGO_VITE_DEV_MODE:  # pragma: no cover
    CSP_CONNECT_SRC = ["ws://localhost:5173/static/", "https://plausible.io"]
    CSP_FONT_SRC = ["'self'", "data:"]
    CSP_SCRIPT_SRC = CSP_SCRIPT_SRC_ELEM = [
        "'self'",
        "https://plausible.io",
        "http://localhost:5173",
    ]
    CSP_STYLE_SRC = CSP_STYLE_SRC_ELEM = [
        "'self'",
        "'unsafe-inline'",
    ]

# Permissions Policy
# https://github.com/adamchainz/django-permissions-policy/blob/main/README.rst
PERMISSIONS_POLICY = {
    "interest-cohort": [],
}


ALLOWED_ORGS = ["opensafely-actions"]
