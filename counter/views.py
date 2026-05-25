from django.shortcuts import render
from .models import VisitorLog

def home(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '0.0.0.0'))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    
    VisitorLog.objects.create(ip_address=ip)
    count = VisitorLog.objects.count()
    
    return render(request, 'counter/home.html', {'count': count})