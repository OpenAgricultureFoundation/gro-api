from django.db import models
from schemata import all_schemata

all_models = {}
for name, schema in all_schemata:
    models = []
    for model in schema:
        pass
