#!/usr/bin/python3


import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mediaAnalysis.settings")

import django
django.setup()

from core.models import Word


if __name__ == "__main__":
    Word.objects.all().delete()
    print("Done")