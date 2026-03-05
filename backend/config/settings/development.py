import os

from .base import *  # noqa: F403

MIDDLEWARE.append("api.middleware.RangesMiddleware")  # noqa: F405

# Avoid noisy staticfiles warning in development when frontend build artifacts
# are not present yet.
STATICFILES_DIRS = [static_dir for static_dir in STATICFILES_DIRS if os.path.isdir(static_dir)]  # noqa: F405
# LOGGING = {
#     'version': 1,
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         },
#     }
# }
