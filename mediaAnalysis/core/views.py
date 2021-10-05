import datetime
import io
import base64

from django.shortcuts import render
from django.utils.timezone import make_aware
from django import forms
from django.db.models import Count

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

from core.models import Word


class QueryForm(forms.Form):
    query = forms.CharField(max_length=200)


def query(request):
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            imgData = lemmaDayGraph(form.cleaned_data["query"])
            print(len(imgData))
            return render(request, 'core/query.html', {'form': form, 'imgData' : imgData})
    else:
        form = QueryForm()

    return render(request, 'core/query.html', {'form': form})



def lemmaDayGraph(lemma):
    res = countLemma(lemma)
    channelRes = {}
    dateMin = datetime.date.max
    dateMax = datetime.date.min
    for r in res:
        channelName = r["channel__name"]
        date = r["date"]
        dateObj = datetime.date.fromisoformat(date)
        channelRes.setdefault(channelName, {})[dateObj] = r["count"]
        dateMin = dateObj if dateObj < dateMin else dateMin
        dateMax = dateObj if dateObj > dateMax else dateMax

    imgData = []
    for channelName, channelData in channelRes.items():

        extandedChannelData = {dateMin + datetime.timedelta(days = x) : 0 for x in range((dateMax - dateMin).days)}
        for d, c in channelData.items():
            extandedChannelData[d] = c

        plotData = list(extandedChannelData.values())
        plotLabels = list(extandedChannelData.keys())

        fig = plt.figure()
        plt.bar(range(len(plotData)), plotData)

        plt.xlabel('Dates')
        plt.xticks(list(range(len(plotLabels))), plotLabels)
        plt.title(channelName)

        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        plt.close(fig)

        buf.seek(0)

        imgData.append(base64.b64encode(buf.read()).decode('ascii'))

    return imgData



def countLemma(lemma):
    start_date = make_aware(datetime.datetime(2021, 9, 23, 0, 0))
    end_date = make_aware(datetime.datetime.now())
    q = Word.objects.filter(dateTime__range=(start_date, end_date), lemma=lemma) \
        .extra({'date' : "date(dateTime)"}) \
        .values('date', 'channel__name') \
        .annotate(count=Count('lemma'))

    return list(q)