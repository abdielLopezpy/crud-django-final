from django.db import models
from django.db.models import Sum, Avg, Count
from decimal import Decimal

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    def get_productos_count(self):
        return self.producto_set.count()
    
    def get_ventas_totales(self):
        return sum(producto.get_ventas_totales() for producto in self.producto_set.all())

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2, help_text="Costo por unidad")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    minimo_stock = models.IntegerField(default=5, help_text="Cantidad mínima antes de reordenar")
    
    def __str__(self):
        return self.nombre
    
    def get_margen_ganancia(self):
        return ((self.precio - self.costo) / self.costo) * 100
    
    def get_ventas_totales(self):
        return self.detalleventa_set.aggregate(total=Sum('subtotal'))['total'] or 0
    
    def get_cantidad_vendida(self):
        return self.detalleventa_set.aggregate(total=Sum('cantidad'))['total'] or 0
    
    def necesita_reorden(self):
        return self.cantidad <= self.minimo_stock

class Venta(models.Model):
    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    
    fecha_venta = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Venta #{self.id} - {self.fecha_venta.strftime('%Y-%m-%d %H:%M')}"
    
    def get_ganancia_neta(self):
        costo_total = sum(detalle.producto.costo * detalle.cantidad for detalle in self.detalleventa_set.all())
        return self.total - costo_total - self.descuento
    
    @staticmethod
    def get_ventas_por_periodo(inicio, fin):
        return Venta.objects.filter(fecha_venta__range=(inicio, fin)).aggregate(
            total_ventas=Sum('total'),
            promedio_venta=Avg('total'),
            num_ventas=Count('id')
        )

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        # Actualizar stock
        self.producto.cantidad -= self.cantidad
        self.producto.save()
    
    def get_margen_ganancia(self):
        return ((self.precio_unitario - self.producto.costo) / self.producto.costo) * 100
    
    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

class Notificacion(models.Model):
    TIPOS = [
        ('stock_bajo', 'Stock Bajo'),
        ('venta', 'Nueva Venta'),
        ('alerta', 'Alerta General'),
    ]
    
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo

    @staticmethod
    def crear_notificacion_stock_bajo(producto):
        Notificacion.objects.create(
            titulo=f'Stock bajo en {producto.nombre}',
            mensaje=f'El producto {producto.nombre} tiene un stock de {producto.cantidad} unidades, por debajo del mínimo requerido ({producto.minimo_stock}).',
            tipo='stock_bajo'
        )
