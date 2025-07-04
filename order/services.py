from order.models import Cart,Order,OrderItem,CartItem
from django.db import transaction
from rest_framework.exceptions import PermissionDenied,ValidationError
class OrderService:
    @staticmethod
    def create_order(cart_id,user_id):
        with transaction.atomic():
            cart=Cart.objects.get(pk=cart_id)
            cart_items=cart.items.select_related('product').all()

            total_price=sum([item.product.price * item.quantity for item in cart_items])
            order=Order.objects.create(user_id=user_id,total_price=total_price)

            order_items=[
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                    total_price=item.quantity * item.product.price
                )
                for item in cart_items
                ]
            
            OrderItem.objects.bulk_create(order_items)

            cart.delete()
            return order
    
    @staticmethod
    def cancel_order(order,user):
        if user.is_staff:
            order.status=Order.CANCELED
            order.save()
            return order

        if order.user != user:
            raise PermissionDenied({'detail':'You can only cancel your own order'})

        if order.status == Order.DELIVERED:
            raise ValidationError({'detail':'You can not cancel an already delivered order'})

        order.status=Order.CANCELED
        order.save()
        return order