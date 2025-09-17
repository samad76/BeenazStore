from django import forms
from orders.models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'payment_method', 'address_line_1', 'address_line_2', 'country', 'province', 'city', 'order_note']
        exclude = ['user', 'status', 'order_total', 'tax', 'ip', 'order_number']
        widgets = {
            'user': forms.HiddenInput(),
            'status': forms.HiddenInput(),
        }
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'payment_method': 'Payment Method',
            'address_line_1': 'Address Line 1',
            'address_line_2': 'Address Line 2',
            'country': 'Country',
            'province': 'Province/State',
            'city': 'City',
            'order_note': 'Order Note (Optional)',
        }
   