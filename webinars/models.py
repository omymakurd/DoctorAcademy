from django.db import models

class Webinar(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField()
    image = models.ImageField(upload_to='webinars/', null=True, blank=True)
    link = models.URLField()

    def __str__(self):
        return self.title
