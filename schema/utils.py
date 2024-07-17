from .models import Schema

def get_schemas():
    return Schema.objects.all()

def get_schema(id):
    return Schema.objects.get(id=id)