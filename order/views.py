from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from order.models import Cart,CartItem,Order,OrderItem
from order.serializers import CartSerializer,CartItemSerializer,AddCartItemSerializer,UpdateCartItemSerializer,OrderSerializer,CreateOrderSerializer,UpdateOrderSerializer,EmptySerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.decorators import action
from order.services import OrderService
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

# Create your views here.

class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    """Cart read, create, update and delete operations
    - Only Authenticated user can only create a cart. 
    -Authenticated user can also  read and update or delete only his own cart
    -One authenticated user can have only 1 cart at a time. 
    - Admin can create ,read update and delete any cart """
    
    # queryset=Cart.objects.all()
    serializer_class=CartSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if getattr(self,'swagger_fake_view',False):
            return Cart.objects.none()
        
        return Cart.objects.prefetch_related('items__product').filter(user=self.request.user)
    
    @swagger_auto_schema(
	operation_summary='Get a single cart with its details',
	operation_description='This feature allows a cart details to be read by only by its owner',
	responses={
		200:CartSerializer,
		401:'Bad Request'
	    }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class CartItemViewSet(ModelViewSet):
    """CartItem read, create, update and delete operations
    - Authenticated user can only read and see the cartitems of his own cart.
    - And add, update, delete item from his own cart 
    - Admin can create , update and delete any cart and cartItem"""
    http_method_names=['get','post','patch','delete']
    # queryset=CartItem.objects.all()
    # serializer_class=CartItemSerializer

    def get_serializer_class(self):
        if self.request.method=='POST':
            return AddCartItemSerializer
        elif self.request.method=='PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs.get('cart_pk')} #why the key is 'cart_id' and not 'cart_pk'?

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id=self.kwargs.get('cart_pk'))
    
    @swagger_auto_schema(
	operation_summary='Get the list of  cart items of the cart',
	operation_description='This feature allows all cart item object to be read by the owner of the cart',
	responses={
		200:CartItemSerializer,
		401:'Bad Request'
	    }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Get a single cart item of the cart',
	operation_description='This feature allows a single cart item object to be read by the owner of the cart',
	responses={
		200:CartItemSerializer,
		401:'Bad Request'
	    }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Create a single cartitem to the cart',
	operation_description='This feature allows a cartitem object to be created only by Admin and the owner of the cart',
	request_body=AddCartItemSerializer,
	responses={
		201:CartItemSerializer,
		401:'Bad Request'
	    }
    )
    def create(self, request, *args, **kwargs):
        existing_cart=Cart.objects.filter(user=request.user).first()

        if existing_cart:
            serializer=self.get_serializer(existing_cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Update the quantity of a single cartitem to the cart',
	operation_description='This feature allows to the update the quantity of a cartitem object  only by Admin and the owner of the cart',
	request_body=UpdateCartItemSerializer,
	responses={
		201:CartItemSerializer,
		401:'Bad Request'
	    }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    

class OrderViewSet(ModelViewSet):
    """Order read, create, update and delete operations
    - Only Authenticated user who has a non-empty cart can only create an order. 
    -Authenticated user can also  read  or delete only his own order.
    - The only update option is updating status, exclusive for Admin. 
    -One authenticated user can cancel the order unless it is already delivered. 
    - Admin can create ,read update and delete any order """
    # queryset=Order.objects.all()
    # serializer_class=OrderSerializer
    # permission_classes=[IsAuthenticated]
    http_method_names=['get','post','delete','patch','head','options'] #destroy method hobe na?

    @swagger_auto_schema(
	operation_summary='Update the status of the order to cancel',
	operation_description='This feature allows the status of a order object to be updated as Cancelled only by Admin and the owner of the order, if the order is not already Delivered',
	request_body=EmptySerializer,
	responses={
		200:OrderSerializer,
		401:'Bad Request'
	    }
    )   
    @action(detail=True,methods=['post']) #permission_classes=[IsAuthenticated]
    def cancel(self,request,pk=None):
        order=self.get_object()
        user=request.user
        OrderService.cancel_order(order=order,user=user)   #cancel_order to return kore. recieve korte hobe na? 
        return Response({'status':'Order Cancelled'})

    @swagger_auto_schema(
	operation_summary='Update the status of the order',
	operation_description='This feature allows the status of a order object to be updated only by Admin',
	request_body=UpdateOrderSerializer,
	responses={
		200:OrderSerializer,
		401:'Bad Request'
	    }
    )   
    @action(detail=True,methods=['patch']) #,permission_classes=[IsAdminUser]
    def update_status(self,request,pk=None):
        order=self.get_object()
        serializer=UpdateOrderSerializer(order,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status':f'Order status updated to {request.data['status']}'})

    def get_permissions(self):
        # if self.request.method in 'DELETE':
        #     return [IsAdminUser()] #call korte hobe
        if self.action in ['update_status','destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        context=super().get_serializer_context()
        if getattr(self,'swagger_fake_view',False):
            return context
        return {'user_id':self.request.user.id,'user':self.request.user}

    def get_serializer_class(self):
        if self.action=='cancel': #cancel in also a post method, so to distinguish from POST, we used action instead of method
            return EmptySerializer
        if self.action=='create': #self.request.method=='POST'
            return CreateOrderSerializer
        elif self.action=='update_status': #elif self.request.method=='PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        if getattr(self,'swagger_fake_view',False):
            return Cart.objects.none()

        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        return Order.objects.prefetch_related('items__product').filter(user=self.request.user)
    # select_related keno kaj korlo na?
    
    @swagger_auto_schema(
	operation_summary='Get list of all orders',
	operation_description='This feature allows list of all order object to be read only by the admin',
	responses={
		200:OrderSerializer,
		401:'Bad Request'
	    }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Get a single order object',
	operation_description='This feature allows a single order object to be read by the owner of the order and the admin',
	responses={
		200:OrderSerializer,
		401:'Bad Request'
	    }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Create a single order',
	operation_description='This feature allows a order object to be created only by Admin and the owner of an existing cart',
	request_body=CreateOrderSerializer,
	responses={
		201:OrderSerializer,
		401:'Bad Request'
	    }
    )    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Delete a single order object',
	operation_description='This feature allows a order object to be deleted only by Admin',
	request_body=OrderSerializer,
	responses={
		204:OrderSerializer,
		401:'Bad Request'
	    }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    