from django.test import TestCase
from .import models

# Create your tests here.
for unitName in ["g", "kg", "oz", "lbs", "ml", "liter", "cup", "loaf", "piece", "slice", "teasponn", "tablespoon", "pinch"]:
    unit = models.Unit(name=unitName);
    unit.save();