from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import VisitorLog
from collections import Counter
import json

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
    return JsonResponse({'visitor_data': visitor_data, 'total': len(visitor_data)})

# API 6 - AI Result using Python logic
@csrf_exempt
def api_ai_result(request):
    visitors = list(
        VisitorLog.objects.order_by('-timestamp').values('ip_address', 'timestamp')
    )

    if not visitors:
        return JsonResponse({
            'analysis': 'PEAK HOURS: No data yet\nBOT DETECTION: No data yet\nPATTERN SUMMARY: No visitors recorded yet.',
            'status': 'success'
        })

    # Peak Hours Analysis
    hours = [v['timestamp'].hour for v in visitors if v['timestamp']]
    hour_counts = Counter(hours)
    peak_hour = max(hour_counts, key=hour_counts.get)
    top_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    peak_analysis = f"Peak traffic at {peak_hour}:00 - {peak_hour+1}:00 with {hour_counts[peak_hour]} visits. "
    peak_analysis += f"Top hours: {', '.join([f'{h}:00 ({c} visits)' for h, c in top_hours])}"

    # Bot Detection
    ip_counts = Counter([v['ip_address'] for v in visitors])
    suspicious = [(ip, count) for ip, count in ip_counts.items() if count > 5]
    if suspicious:
        bot_analysis = f"Suspicious IPs detected: {', '.join([f'{ip} ({c} visits)' for ip, c in suspicious])}"
    else:
        bot_analysis = f"No suspicious activity detected. All {len(ip_counts)} unique IPs appear normal."

    # Pattern Summary
    total = len(visitors)
    unique_ips = len(ip_counts)
    summary = f"Site received {total} total visits from {unique_ips} unique visitors. "
    if total > 10:
        summary += "Traffic is growing steadily. "
    else:
        summary += "Site is in early stages with low traffic. "
    summary += f"Most active hour is {peak_hour}:00."

    analysis = f"PEAK HOURS: {peak_analysis}\nBOT DETECTION: {bot_analysis}\nPATTERN SUMMARY: {summary}"

    return JsonResponse({'analysis': analysis, 'status': 'success'})