from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import VisitorLog
import json
import os
import urllib.request

def home(request):
    return render(request, 'counter/home.html')

def api_total(request):
    count = VisitorLog.objects.count()
    return JsonResponse({'total_visitors': count})

def api_log_visitor(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '0.0.0.0'))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    VisitorLog.objects.create(ip_address=ip)
    count = VisitorLog.objects.count()
    return JsonResponse({'message': 'Visitor logged', 'total_visitors': count})

def api_recent(request):
    visitors = list(
        VisitorLog.objects.order_by('-timestamp')[:10].values('ip_address', 'timestamp')
    )
    return JsonResponse({'recent_visitors': visitors})

def api_all(request):
    visitors = list(
        VisitorLog.objects.order_by('-timestamp').values('ip_address', 'timestamp')
    )
    return JsonResponse({'total': len(visitors), 'visitors': visitors})

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
    return JsonResponse({'visitor_data': visitor_data, 'total': len(visitor_data)})

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

    api_key = os.environ.get('GROQ_API_KEY', '')

    payload = json.dumps({
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}]
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.groq.com/openai/v1/chat/completions',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            text = result['choices'][0]['message']['content']
            return JsonResponse({'analysis': text, 'status': 'success'})
    except Exception as e:
        return JsonResponse({'analysis': str(e), 'status': 'error'})