from django.db import models


class Channel(models.Model):
    name = models.CharField(max_length=30)
    publicName = models.CharField(max_length=30)
    programId = models.IntegerField()

    def __str__(self):
        return self.name


class Word(models.Model):
    dateTime = models.DateTimeField()
    word = models.CharField(max_length=30)
    lemma = models.CharField(max_length=30)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    def __str__(self):
        return self.word + " - " + str(self.dateTime) + " - " + self.channel.name

    class Meta:
        indexes = [
            models.Index(fields=['word']),
            models.Index(fields=['lemma']),
            models.Index(fields=['dateTime']),
            models.Index(fields=['channel'])
        ]
