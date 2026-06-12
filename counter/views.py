from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import VisitorLog

def home(request):
    return render(request, 'counter/home.html')

# API 1 - Get total count
def api_total(request):
    count = VisitorLog.objects.count()
    return JsonResponse({'total_visitors': count})

# API 2 - Log visitor
def api_log_visitor(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '0.0.0.0'))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    VisitorLog.objects.create(ip_address=ip)
    count = VisitorLog.objects.count()
    return JsonResponse({'message': 'Visitor logged', 'total_visitors': count})

# API 3 - Get recent visitors
def api_recent(request):
    visitors = list(
        VisitorLog.objects.order_by('-timestamp')[:10].values('ip_address', 'timestamp')
    )
    return JsonResponse({'recent_visitors': visitors})

# API 4 - Get all visitors
def api_all(request):
    visitors = list(
        VisitorLog.objects.order_by('-timestamp').values('ip_address', 'timestamp')
    )
    return JsonResponse({'total': len(visitors), 'visitors': visitors})

# API 5 - AI Analysis data
@csrf_exempt
def api_ai_analyze(request):
    visitors = list(
        VisitorLog.objects.order_by('-timestamp').values('ip_address', 'timestamp')
    )
    visitor_data = []
    for v in visitors:
        visitor_data.append({
            'ip': v['ip_address'],
            'time': v['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if v['timestamp'] else ''
        })
    return JsonResponse({
        'visitor_data': visitor_data,
        'total': len(visitor_data)
    })