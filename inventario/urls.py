# Copyright 2025 Abdiel Lopez.
# SPDX-License-Identifier: BSL-1.0

from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # URLs para Categorias
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/nueva/', views.nueva_categoria, name='nueva_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # URLs para Productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/nuevo/', views.nuevo_producto, name='nuevo_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    
    # Nuevas URLs para ventas
    path('ventas/', views.lista_ventas, name='lista_ventas'),
    path('ventas/nueva/', views.nueva_venta, name='nueva_venta'),
    path('ventas/<int:pk>/', views.detalle_venta, name='detalle_venta'),
    path('ventas/eliminar/<int:pk>/', views.eliminar_venta, name='eliminar_venta'),
    
    # URLs para análisis y reportes
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/ventas-por-periodo/', views.ventas_por_periodo, name='ventas_por_periodo'),
    path('reportes/productos-bajo-stock/', views.productos_bajo_stock, name='productos_bajo_stock'),
    path('reportes/ventas-por-categoria/', views.ventas_por_categoria, name='ventas_por_categoria'),
    path('reportes/mejores-productos/', views.mejores_productos, name='mejores_productos'),
    
    # APIs para datos en tiempo real (opcional, para gráficos)
    path('api/ventas-diarias/', views.ventas_diarias_api, name='ventas_diarias_api'),
    path('api/stock-actual/', views.stock_actual_api, name='stock_actual_api'),
    
    # URLs para notificaciones
    path('api/notificaciones/', views.obtener_notificaciones, name='obtener_notificaciones'),
    path('api/notificaciones/<int:notificacion_id>/marcar-leida/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    
    # URL para la página principal
    path('', views.index, name='index'),
]

