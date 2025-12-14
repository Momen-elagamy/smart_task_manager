from django.http import JsonResponse

def test_api(request):
    return JsonResponse({"status": "ok", "message": "API is working!"})

def search_api(request):
    q = request.GET.get('q', '').strip()
    # Placeholder: extend with real search across models
    results = []
    if q:
        results.append({"type": "placeholder", "query": q, "info": "Implement real search"})
    return JsonResponse({"query": q, "results": results}, status=200)

def recent_activity_api(request):
    # Placeholder recent events; integrate with audit trail later
    data = [
        {"id": 1, "event": "login", "detail": "User logged in", "ts": "2025-11-20T10:00:00Z"},
        {"id": 2, "event": "project_created", "detail": "Sample project", "ts": "2025-11-20T10:05:00Z"},
    ]
    return JsonResponse({"results": data}, status=200)
