from rest_framework import serializers
from order.models import Cart,CartItem,Order,OrderItem
from product.serializers import ProductSerializer
from product.models import Product
from order.services import OrderService


class EmptySerializer(serializers.Serializer):
    pass 

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['id','name','price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id=serializers.IntegerField()
    class Meta:
        model=CartItem
        fields=['id','product_id','quantity'] #product_id directly pawa jay na. why?
    # overriding save method to customize creating new cartItem
    def save(self, **kwargs):
        cart_id=self.context['cart_id'] #recieved from cartItemViewSet context function as a context
        product_id=self.validated_data['product_id'] #recieved from serializer form. 
        quantity=self.validated_data['quantity']

        try:
            cart_item=CartItem.objects.get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity+=quantity
            self.instance=cart_item.save()
        except CartItem.DoesNotExist:
            self.instance=CartItem.objects.create(cart_id=cart_id,**self.validated_data)
        
        return self.instance
    # ekhane self.instance return holo keno? mane ki?
    
    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f'Product with id: {value} does not exist')
        return value


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartItem
        fields=['quantity']


class CartItemSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer()
    # product_price=serializers.SerializerMethodField(method_name='get_product_price')
    total_price=serializers.SerializerMethodField(method_name='get_total_price')
    
    class Meta:
        model=CartItem
        fields=['id','product','quantity','total_price']

    def get_total_price(self,cart_item:CartItem):
        return cart_item.quantity * cart_item.product.price
    
    # def get_product_price(self,cart_item): #cart_item kotha theke send hobe?
    #     return cart_item.product.price 
    #     #ekhane self.product.price kaj korbe na keno? 

class CartSerializer(serializers.ModelSerializer):
    items=CartItemSerializer(many=True,read_only=True) #read_only=true means only available for get method. 
    gross_total_price=serializers.SerializerMethodField(method_name='get_gross_total_price')
    class Meta:
        model=Cart
        fields=['id','user','items','gross_total_price']
        read_only_fields=['user']
    
    def get_gross_total_price(self,cart:Cart):
        return sum([item.product.price*item.quantity for item in cart.items.all()])

    # def get_gross_total_price(self,cart:Cart):
    #     item_list=cart['items']
    #     totalPrice=0
    #     for item in item_list:
    #         totalPrice+=item['total_price'] #item['total_price'] cannot be retrieved. not allowed . why?
    #     return totalPrice

class CreateOrderSerializer(serializers.Serializer):
    cart_id=serializers.UUIDField()

    def validate_cart_id(self,cart_id):
        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError('No Cart Found with this id')
        if not CartItem.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError('Cart is Empty')
        
        return cart_id
    
    def create(self, validated_data):
        cart_id=validated_data['cart_id']
        user_id=self.context['user_id']

        try:
            order=OrderService.create_order(cart_id=cart_id,user_id=user_id)
            return order
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        
    
    def to_representation(self, instance):
        return OrderSerializer(instance).data


class OrderItemSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer()
    class Meta:
        model=OrderItem
        fields=['id','product','quantity','price','total_price']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=['status']
    
    """After action implementation, updateing is done in ViewSet
    
    
    def update(self, instance, validated_data):
        user=self.context['user']
        new_status=validated_data['status']

        if new_status==Order.CANCELED:
            return OrderService.cancel_order(order=instance,user=user)
        
        # other status update request, check if admin
        if not user.is_staff:
            raise serializers.ValidationError({'detail':'You are not allowed to update this order'})
        
        # shortcut method
        return super().update(instance,validated_data)
        
        # Long Cut method 
        
        instance.status=new_status
        instance.save()
        return instance
        
    """


class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True)
    class Meta:
        model=Order
        fields=['id','user','status','total_price','created_at','items']