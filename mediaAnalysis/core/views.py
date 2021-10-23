import datetime
import io
import base64

from django.shortcuts import render
from django.utils.timezone import make_aware
from django import forms
from django.db.models import Subquery, Count, OuterRef, F
from django.db.models.functions import Cast
from django.db.models.fields import DateField

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import MaxNLocator

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



def lemmaDayGraph(query):
    res = countLemma(query)
    channelRes = {}
    dateMin = datetime.date.max
    dateMax = datetime.date.min
    countMax = 0
    for r in res:
        channelName = r["channel0Name"]
        date = r["date0"]
        count = r["count"]
        dateObj = datetime.date.fromisoformat(date) if isinstance(date, str) else date
        channelRes.setdefault(channelName, {})[dateObj] = count
        dateMin = dateObj if dateObj < dateMin else dateMin
        dateMax = dateObj if dateObj > dateMax else dateMax
        countMax = max(countMax, count)
    channelRes = dict(sorted(channelRes.items(), key=lambda item: item[0])) # sort the result dic by channel names

    imgData = []
    for channelName, channelData in channelRes.items():

        extandedChannelData = {dateMin + datetime.timedelta(days = x) : 0 for x in range((dateMax - dateMin).days)}
        total = 0
        for d, c in channelData.items():
            extandedChannelData[d] = c
            total += c

        plotData = list(extandedChannelData.values())
        plotLabels = list(extandedChannelData.keys())

        fig = plt.figure()
        plt.bar(range(len(plotData)), plotData)

        plt.xlabel('Dates')
        plt.xticks(list(range(len(plotLabels))), plotLabels, rotation='vertical')
        plt.ylim((0, countMax))
        ax = fig.axes[0]
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.title(channelName)
        plt.text(0.95, 0.95, "Total: %d" % total,
            horizontalalignment='right', verticalalignment='center',
            transform = ax.transAxes,
            fontweight = "bold")

        # Tweak spacing to prevent clipping of tick-labels
        plt.subplots_adjust(bottom=0.2)

        fig.tight_layout()
        fig.set_size_inches(4.5, 5)
        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        plt.close(fig)

        buf.seek(0)

        imgData.append(base64.b64encode(buf.read()).decode('ascii'))

    return imgData



def countLemma(query):
    start_date = make_aware(datetime.datetime(2021, 9, 23, 0, 0))
    end_date = make_aware(datetime.datetime.now())

    words = query.split()

    for i, w in enumerate(words):
        if i == 0:
            q = Word.objects.filter(
                dateTime__range=(start_date, end_date), lemma = w
            ).annotate(dateTime0 = F("dateTime"),
                        channel0 = F("channel"),
                        channel0Name = F("channel__name")
            ).annotate(date0=Cast('dateTime', DateField()))
        else:
            sq = Subquery(Word.objects.filter(
                dateTime__gt = OuterRef("dateTime0"),
                channel = OuterRef("channel0")
            ).order_by('dateTime').values('lemma')[i - 1 : i])
            q = q.annotate(
                **{"w_{}".format(i) : sq}
            ).filter(
                **{"w_{}".format(i) : w}
            )

    q = q.values("date0", "channel0Name").annotate(count=Count('lemma'))

    return list(q)