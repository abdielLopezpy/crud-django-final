# Copyright 2025 Abdiel Lopez.
# SPDX-License-Identifier: BSL-1.0

from django import forms
from .models import Categoria, Producto, Venta, DetalleVenta

class FormStyleMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.EmailInput)):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                    'rows': '3'
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'
                })

class CategoriaForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class ProductoForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'cantidad', 'precio', 'costo', 'minimo_stock']
        widgets = {
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
            'costo': forms.NumberInput(attrs={'step': '0.01'}),
        }

class VentaForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['metodo_pago', 'descuento', 'impuesto']
        widgets = {
            'descuento': forms.NumberInput(attrs={'step': '0.01'}),
            'impuesto': forms.NumberInput(attrs={'step': '0.01'}),
        }

class DetalleVentaForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos con stock disponible
        self.fields['producto'].queryset = Producto.objects.filter(cantidad__gt=0)

class ReporteFechasForm(FormStyleMixin, forms.Form):
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

