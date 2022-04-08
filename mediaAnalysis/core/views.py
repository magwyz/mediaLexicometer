import datetime
import io
import base64
import time

from django.shortcuts import render
from django.utils.timezone import make_aware
from django import forms
from django.db.models import Subquery, Count, OuterRef, F
from django.db.models.functions import TruncDate
from django.db.models.fields import DateField
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import MaxNLocator
import spacy

from core.models import Word

nlp = spacy.load("fr_core_news_sm-3.1.0")


class QueryForm(forms.Form):
    q = forms.CharField(label="Requête", max_length=200)
    dmin = forms.DateTimeField(label="À partir de", initial = make_aware(datetime.datetime(2021, 9, 23, 0, 0)))
    dmax = forms.DateTimeField(label="Jusqu'à")


@csrf_exempt
def query(request):
    form = QueryForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data["q"]
        dateMin = form.cleaned_data["dmin"]
        dateMax = form.cleaned_data["dmax"]
        action = request.GET.get('action')
        page = request.GET.get('page')
        if action == "count":
            imgData, lemmas, queryTime = lemmaDayGraph(query, dateMin, dateMax)
            return render(
                request, 'core/query.html',
                {
                    'form': form,
                    'imgData' : imgData,
                    'lemmas' : lemmas,
                    'queryTime' : float(queryTime)
                }
            )
        else:
            page = 1 if page is None else int(page)
            lemmas, occurences, queryTime = getLemmaContext(query, dateMin, dateMax, page)
            return render(
                request, 'core/query.html',
                {
                    'form': form,
                    'lemmas' : lemmas,
                    'queryTime' : float(queryTime),
                    'occurences' : occurences
                }
            )
    else:
        form = QueryForm(initial={'dmax': make_aware(datetime.datetime.now())})

    return render(request, 'core/query.html', {'form': form})



def lemmaDayGraph(query, dateMin, dateMax):
    start = time.time()
    res, lemmas = countLemma(query, dateMin, dateMax)
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
    totals = {}
    for channelName, channelData in channelRes.items():

        extandedChannelData = {dateMin + datetime.timedelta(days = x) : 0 for x in range((dateMax - dateMin).days)}
        total = 0
        for d, c in channelData.items():
            extandedChannelData[d] = c
            total += c
        totals[channelName] = total

        plotData = list(extandedChannelData.values())
        plotLabels = list(
            map(
                lambda x : x.strftime('%d/%m/%y'),
                extandedChannelData.keys()
            )
        )

        f = len(plotLabels) // 30
        if f >= 1:
            for i in range(len(plotLabels)):
                if i % (f + 1) > 0:
                    plotLabels[i] = ""

        fig = plt.figure()
        plt.bar(range(len(plotData)), plotData, width=1)

        plt.xlabel('Dates')
        plt.xticks(list(range(len(plotLabels))), plotLabels, rotation='vertical')
        plt.ylim((0, countMax))
        ax = fig.axes[0]
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.suptitle(channelName, fontsize="large")
        plt.text(0.95, 0.95, "Total: %d" % total,
            horizontalalignment='right', verticalalignment='center',
            transform = ax.transAxes,
            fontsize="large",
            fontweight = "bold")

        # Tweak spacing to prevent clipping of tick-labels
        fig.tight_layout(rect=[0.07, 0, 1, 1])
        fig.set_size_inches(3.6, 5)
        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        plt.close(fig)

        buf.seek(0)

        imgData.append(base64.b64encode(buf.read()).decode('ascii'))

    # Pie chart
    fig = plt.figure()
    fig.tight_layout()
    fig.set_size_inches(4, 5)
    title = ""
    for lemma in lemmas:
        title += lemma + " "
    title = title[:-1]
    plt.suptitle(title)
    plt.title("Total : " + str(sum(totals.values())),
        fontweight = "bold", fontsize="large")
    plt.pie(totals.values(), labels=totals.keys())
    imgData = [saveFigureImg(fig)] + imgData

    end = time.time()
    queryTime = end - start

    return imgData, lemmas, queryTime


def saveFigureImg(fig):
    canvas = FigureCanvasAgg(fig)
    buf = io.BytesIO()
    canvas.print_png(buf)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('ascii')


def getLemma(query, dateMin, dateMax):
    words = query.split()
    lemmas = [nlp(word)[-1].lemma_ for word in words]

    for i, w in enumerate(lemmas):
        if i == 0:
            q = Word.objects.filter(
                dateTime__range=(dateMin, dateMax), lemma = w
            ).annotate(dateTime0 = F("dateTime"),
                        channel0 = F("channel"),
                        channel0Name = F("channel__name")
            ).annotate(date0=TruncDate('dateTime'))
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

    return lemmas, q


def countLemma(query, dateMin, dateMax):
    lemmas, q = getLemma(query, dateMin, dateMax)
    q = q.values("date0", "channel0Name").annotate(count=Count('lemma'))

    return list(q), lemmas


def getLemmaContext(query, dateMin, dateMax, page):
    start = time.time()
    lemmas, q = getLemma(query, dateMin, dateMax)

    paginator = Paginator(q, 25)
    occurences = paginator.get_page(page)

    for res in occurences:
        context = ""
        q2 = Word.objects.filter(dateTime__range=(
            res.dateTime - datetime.timedelta(seconds=15),
            res.dateTime + datetime.timedelta(seconds=15)), channel = res.channel)
        for res2 in q2:
            context += res2.word + " "
        res.context = context

    end = time.time()
    queryTime = end - start

    return lemmas, occurences, queryTime
