from django.db import models
import uuid

class BaseModel(models.Model):
    id = models.UUIDField(editable=False, unique=True, default=uuid.uuid4, primary_key=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
