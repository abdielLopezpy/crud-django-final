from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from .models import Categoria, Producto, Venta, DetalleVenta, Notificacion
from .forms import CategoriaForm, ProductoForm, VentaForm, DetalleVentaForm, ReporteFechasForm

def get_base_context(request):
    """Contexto base para todas las vistas que incluye los items del menú"""
    return {
        'menu_items': [
            {
                'url': reverse('inventario:index'),
                'text': 'Dashboard',
                'icon': '''<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>'''
            },
            # Agrega más items según necesites
        ]
    }

def index(request):
    context = get_base_context(request)
    context.update({
        'total_categorias': Categoria.objects.count(),
        'total_productos': Producto.objects.count(),
        'total_ventas': Venta.objects.count(),
        'productos_bajos': Producto.objects.filter(cantidad__lte=models.F('minimo_stock')).count(),
    })
    return render(request, 'inventario/index.html', context)

# Vistas para Categorías
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'inventario/categoria/lista.html', {'categorias': categorias})

def nueva_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('inventario:lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'inventario/categoria/form.html', {'form': form, 'accion': 'Nueva'})

def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('inventario:lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'inventario/categoria/form.html', {'form': form, 'accion': 'Editar'})

def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente.')
        return redirect('inventario:lista_categorias')
    return render(request, 'inventario/categoria/confirmar_eliminar.html', {'categoria': categoria})

# Vistas para Productos
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'inventario/producto/lista.html', {'productos': productos})

def nuevo_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('inventario:lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario/producto/form.html', {'form': form, 'accion': 'Nuevo'})

def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('inventario:lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/producto/form.html', {'form': form, 'accion': 'Editar'})

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('inventario:lista_productos')
    return render(request, 'inventario/producto/confirmar_eliminar.html', {'producto': producto})

# Vistas de Ventas
def lista_ventas(request):
    ventas = Venta.objects.all().order_by('-fecha_venta')
    return render(request, 'inventario/venta/lista.html', {'ventas': ventas})

def nueva_venta(request):
    if request.method == 'POST':
        venta_form = VentaForm(request.POST)
        detalle_form = DetalleVentaForm(request.POST)
        if venta_form.is_valid() and detalle_form.is_valid():
            venta = venta_form.save(commit=False)
            detalle = detalle_form.save(commit=False)
            
            # Calcular total
            producto = detalle.producto
            detalle.precio_unitario = producto.precio
            detalle.subtotal = detalle.cantidad * detalle.precio_unitario
            
            if detalle.cantidad > producto.cantidad:
                messages.error(request, 'No hay suficiente stock disponible.')
                return redirect('inventario:nueva_venta')
            
            venta.total = detalle.subtotal - venta.descuento + venta.impuesto
            venta.save()
            detalle.venta = venta
            detalle.save()
            
            messages.success(request, 'Venta realizada exitosamente.')
            return redirect('inventario:lista_ventas')
    else:
        venta_form = VentaForm()
        detalle_form = DetalleVentaForm()
    
    return render(request, 'inventario/venta/form.html', {
        'venta_form': venta_form,
        'detalle_form': detalle_form,
    })

def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    detalles = venta.detalleventa_set.all()
    return render(request, 'inventario/venta/detalle.html', {
        'venta': venta,
        'detalles': detalles,
    })

def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        # Restaurar stock
        for detalle in venta.detalleventa_set.all():
            producto = detalle.producto
            producto.cantidad += detalle.cantidad
            producto.save()
        
        venta.delete()
        messages.success(request, 'Venta eliminada exitosamente.')
        return redirect('inventario:lista_ventas')
    return render(request, 'inventario/venta/confirmar_eliminar.html', {'venta': venta})

# Vistas de Reportes
def reportes(request):
    return render(request, 'inventario/reportes/index.html')

def ventas_por_periodo(request):
    if request.method == 'POST':
        form = ReporteFechasForm(request.POST)
        if form.is_valid():
            inicio = form.cleaned_data['fecha_inicio']
            fin = form.cleaned_data['fecha_fin']
            ventas = Venta.get_ventas_por_periodo(inicio, fin)
            return render(request, 'inventario/reportes/ventas_periodo.html', {
                'form': form,
                'ventas': ventas,
                'inicio': inicio,
                'fin': fin,
            })
    else:
        form = ReporteFechasForm()
    return render(request, 'inventario/reportes/ventas_periodo.html', {'form': form})

def productos_bajo_stock(request):
    productos = Producto.objects.filter(cantidad__lte=models.F('minimo_stock'))
    return render(request, 'inventario/reportes/bajo_stock.html', {'productos': productos})

def ventas_por_categoria(request):
    categorias = Categoria.objects.annotate(
        total_ventas=Sum('producto__detalleventa__subtotal'),
        cantidad_vendida=Sum('producto__detalleventa__cantidad')
    )
    return render(request, 'inventario/reportes/ventas_categoria.html', {'categorias': categorias})

def mejores_productos(request):
    productos = Producto.objects.annotate(
        total_vendido=Sum('detalleventa__cantidad'),
        total_ingresos=Sum('detalleventa__subtotal')
    ).order_by('-total_vendido')[:10]
    return render(request, 'inventario/reportes/mejores_productos.html', {'productos': productos})

# APIs para datos en tiempo real
def ventas_diarias_api(request):
    hoy = timezone.now().date()
    ventas = Venta.objects.filter(
        fecha_venta__date=hoy
    ).values('fecha_venta__hour').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('fecha_venta__hour')
    return JsonResponse(list(ventas), safe=False)

def stock_actual_api(request):
    productos = Producto.objects.filter(
        cantidad__lte=models.F('minimo_stock')
    ).values('nombre', 'cantidad', 'minimo_stock')
    return JsonResponse(list(productos), safe=False)

def obtener_notificaciones(request):
    notificaciones = Notificacion.objects.filter(leida=False)[:5]
    data = [{
        'id': n.id,
        'titulo': n.titulo,
        'mensaje': n.mensaje,
        'tipo': n.tipo,
        'fecha': n.fecha.strftime('%Y-%m-%d %H:%M'),
        'tiempo_relativo': tiempo_relativo(n.fecha)
    } for n in notificaciones]
    return JsonResponse({'notificaciones': data, 'count': notificaciones.count()})

def marcar_notificacion_leida(request, notificacion_id):
    if request.method == 'POST':
        notificacion = get_object_or_404(Notificacion, id=notificacion_id)
        notificacion.leida = True
        notificacion.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def tiempo_relativo(fecha):
    """Calcula el tiempo relativo para una fecha"""
    ahora = timezone.now()
    diff = ahora - fecha
    
    if diff.days == 0:
        if diff.seconds < 60:
            return 'Hace un momento'
        if diff.seconds < 3600:
            minutos = diff.seconds // 60
            return f'Hace {minutos} {"minuto" if minutos == 1 else "minutos"}'
        horas = diff.seconds // 3600
        return f'Hace {horas} {"hora" if horas == 1 else "horas"}'
    if diff.days == 1:
        return 'Ayer'
    if diff.days < 7:
        return f'Hace {diff.days} días'
    return fecha.strftime('%d/%m/%Y')
