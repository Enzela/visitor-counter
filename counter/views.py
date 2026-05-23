from django.shortcuts import render
from .models import VisitorCount

def home(request):
    visitor, created = VisitorCount.objects.get_or_create(id=1)
    visitor.count += 1
    visitor.save()
    return render(request, 'counter/home.html', {'count': visitor.count})