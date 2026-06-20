import os
import urllib.request

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