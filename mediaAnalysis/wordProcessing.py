#!/usr/bin/python3

import datetime

from django.utils.timezone import make_aware

from core.models import Word


def addResultToDB(result, dateTime, channel, nlp):
    words = result["result"]

    dbWords = []
    for w in words:
        wStr = w["word"]
        try:
            doc = nlp(wStr)
            lemma = doc[-1].lemma_
        except:
            lemma = ""
        dbWord = Word(dateTime = make_aware(dateTime + datetime.timedelta(seconds = w["start_frame"])),
            word = wStr,
            lemma = lemma,
            channel = channel)
        dbWords.append(dbWord)

    Word.objects.bulk_create(dbWords)
    pprint("%d words added for %s" % (len(dbWords), channel.publicName))

