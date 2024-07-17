from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .utils import get_schemas
from .forms import SchemaForm

@login_required
def dashboard(request):
    schemas = get_schemas()
    return render(request, 'schema/dashboard.html', context={'schemas':schemas})

def add_schema(request):
    form = SchemaForm()
    if request.method == "POST":
        form = SchemaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('schema_dashboard')
    return render(request, 'schema/add_schema.html', context={'form':form})