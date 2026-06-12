from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import VisitorLog
import json
import urllib.request

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

# API 6 - AI Result from Claude
@csrf_exempt
def api_ai_result(request):
    visitors = list(
        VisitorLog.objects.order_by('-timestamp').values('ip_address', 'timestamp')
    )
    visitor_data = []
    for v in visitors:
        visitor_data.append({
            'ip': v['ip_address'],
            'time': v['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if v['timestamp'] else ''
        })

    prompt = f"""Analyze this visitor data and provide exactly 3 sections:
PEAK HOURS: Which hours get the most traffic?
BOT DETECTION: Any suspicious IPs or bot-like behavior?
PATTERN SUMMARY: 2-3 sentence plain English summary.

Data ({len(visitor_data)} visitors):
{json.dumps(visitor_data, indent=2)}

Format exactly like:
PEAK HOURS: [analysis]
BOT DETECTION: [analysis]
PATTERN SUMMARY: [analysis]"""

    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            text = result['content'][0]['text']
            return JsonResponse({'analysis': text, 'status': 'success'})
    except Exception as e:
        return JsonResponse({'analysis': str(e), 'status': 'error'})