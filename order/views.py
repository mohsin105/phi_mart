from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from order.models import Cart,CartItem,Order,OrderItem
from order.serializers import CartSerializer,CartItemSerializer,AddCartItemSerializer,UpdateCartItemSerializer,OrderSerializer,CreateOrderSerializer,UpdateOrderSerializer,EmptySerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.decorators import action
from order.services import OrderService
# Create your views here.

class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    # queryset=Cart.objects.all()
    serializer_class=CartSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Cart.objects.prefetch_related('items__product').filter(user=self.request.user)

class CartItemViewSet(ModelViewSet):
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
        return {'cart_id':self.kwargs['cart_pk']} #why the key is 'cart_id' and not 'cart_pk'?

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id=self.kwargs['cart_pk'])

class OrderViewSet(ModelViewSet):
    # queryset=Order.objects.all()
    # serializer_class=OrderSerializer
    # permission_classes=[IsAuthenticated]
    http_method_names=['get','post','delete','patch','head','options'] #destroy method hobe na?


    @action(detail=True,methods=['post']) #permission_classes=[IsAuthenticated]
    def cancel(self,request,pk=None):
        order=self.get_object()
        user=request.user
        OrderService.cancel_order(order=order,user=user)   #cancel_order to return kore. recieve korte hobe na? 
        return Response({'status':'Order Cancelled'})


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
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        return Order.objects.prefetch_related('items__product').filter(user=self.request.user)
    # select_related keno kaj korlo na?