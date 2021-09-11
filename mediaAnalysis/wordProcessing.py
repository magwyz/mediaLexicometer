#!/usr/bin/python3

import datetime

from django.utils.timezone import make_aware

from core.models import Word


def addResultToDB(result, dateTime, channel):
    print("addResultToDB")
    words = result["result"]

    dbWords = []
    for w in words:
        dbWord = Word(dateTime = make_aware(dateTime + datetime.timedelta(0, w["start"])),
            word = w["word"],
            lemme = w["word"],
            channel = channel)
        dbWords.append(dbWord)

    Word.objects.bulk_create(dbWords)

