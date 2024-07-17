from django.db import models

class Schema(models.Model):
    nom = models.CharField(max_length=254, verbose_name='Nom du schéma')