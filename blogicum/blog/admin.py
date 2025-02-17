from . import models
from django.contrib import admin

admin.site.register(models.Post)
admin.site.register(models.Category)
admin.site.register(models.Location)
