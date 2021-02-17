from django.test import TestCase

# Create your tests here.
from datetime import date
x = 20210101
a = date(*[int(item) for item in x.split('-')])
print(a)
