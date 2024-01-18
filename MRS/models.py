from django.db import models

class Medicine(models.Model):
    brand_name = models.CharField(max_length=50)
    generic_name = models.CharField(max_length=75)
    diseases_cured = models.CharField(max_length=325)

    def __str__(self):
        return self.brand_name + ': ' + self.generic_name