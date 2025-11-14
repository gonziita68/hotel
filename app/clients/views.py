from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .models import Client

# Vistas existentes
# Create your views here.

@login_required
@require_http_methods(["GET"])
def clients_api(request):
    """API: Listado simple de clientes para el selector del dashboard"""
    qs = Client.objects.all().order_by('first_name', 'last_name')
    search = request.GET.get('search')
    if search:
        qs = qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search) | Q(dni__icontains=search))
    data = [
        {
            'id': c.id,
            'full_name': getattr(c, 'full_name', f"{c.first_name} {c.last_name}").strip(),
            'email': c.email,
            'dni': c.dni or ''
        }
        for c in qs
    ]
    return JsonResponse(data, safe=False)

# Endpoint unificado si se desea expandir a POST en futuro
@login_required
@csrf_exempt
@require_http_methods(["GET"])
def clients_api_collection(request):
    return clients_api(request)
