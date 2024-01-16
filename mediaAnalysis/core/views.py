import datetime
import time

from django.shortcuts import render
from django.utils.timezone import make_aware
from django import forms
from django.db.models.fields import DateField
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from core.models import Channel, Word
from core.wordCount import lemmaDayGraph, lemmaHourGraph, getLemma


class QueryForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(QueryForm, self).__init__(*args, **kwargs)
        self.fields['channels'] = forms.MultipleChoiceField(
            choices=[(c.id, c.publicName) for c in Channel.objects.all()],
            label="Chaîne",
            widget=forms.widgets.SelectMultiple(attrs={'size': 10})
        )

    q = forms.CharField(label="Requête", max_length=200)
    dmin = forms.DateTimeField(label="À partir de", initial = make_aware(datetime.datetime(2023, 12, 3, 0, 0)))
    oneDay = forms.BooleanField(label="Une journée", required=False)
    dmax = forms.DateTimeField(label="Jusqu'à")


@csrf_exempt
def query(request):
    form = QueryForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data["q"]
        dateMin = form.cleaned_data["dmin"]
        oneDay = form.cleaned_data["oneDay"]
        dateMax = form.cleaned_data["dmax"]
        channels = form.cleaned_data["channels"]
        action = request.GET.get('action')
        page = request.GET.get('page')
        if action == "count":
            if oneDay:
                imgData, lemmas, queryTime = lemmaHourGraph(query, dateMin, dateMin + datetime.timedelta(days=1), channels)
            else:
                imgData, lemmas, queryTime = lemmaDayGraph(query, dateMin, dateMax, channels)
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
            lemmas, occurences, queryTime = getLemmaContext(query, dateMin, dateMax, channels, page)
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
        form = QueryForm(initial={
            'dmax': make_aware(datetime.datetime.now()),
            'channels': [c.id for c in Channel.objects.all()]
        })

    return render(request, 'core/query.html', {'form': form})


def getLemmaContext(query, dateMin, dateMax, channel, page):
    start = time.time()
    lemmas, q = getLemma(query, dateMin, dateMax, channel, False)

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
