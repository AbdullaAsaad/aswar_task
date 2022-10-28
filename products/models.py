from django.db import models
import uuid
# Create your models here.
class Product (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length = 100)
    description = models.TextField()
    image  = models.URLField(null=True , blank=True)
    expired = models.DateField(db_column='expired_at' , null=False , )
    created = models.DateTimeField(auto_now_add=True, null=False, db_column='created_at')
    updated = models.DateTimeField(auto_now=True, null=False, db_column='updated_at')
    
    def __str__(self):
        return self.name