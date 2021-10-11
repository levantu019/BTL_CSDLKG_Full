from django.shortcuts import render
from .searchWay import run
import json
from django.http import JsonResponse


def index(request):
    return render(request, 'index.html')


def search(request, start_end):
    start_end = json.loads(start_end)
    start = [start_end[0]['start_X'], start_end[1]['start_Y']]
    end = [start_end[2]['end_X'], start_end[3]['end_Y']]

    result = run(start, end)
    return JsonResponse({'res': json.dumps(result)}, status=200)