#!/usr/bin/python3

from core.models import Channel


def getChannels(channelNames):
    ret = Channel.objects.filter(name__in=channelNames)
    return list(ret)
