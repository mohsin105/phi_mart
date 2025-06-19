from rest_framework.views import APIView
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from product.models import Product,Category,Review,ProductIamge
from product.serializers import ProductSerializer,CategorySerializer,ReviewSerializer,ProductImageSerializer
from django.db.models import Count
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from product.filters import ProductFilter
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination
from product.paginations import DefaultPagination
from rest_framework.permissions import IsAdminUser,AllowAny,DjangoModelPermissions,DjangoModelPermissionsOrAnonReadOnly
from api.permissions import IsAdminOrReadOnly,FullDjangoModelPermission
from product.permissions import IsReviewAuthorOrReadOnly
from drf_yasg.utils import swagger_auto_schema

# Create your views here.

# id and pk niye confusion lagse. 

# @api_view(['GET','POST'])
# def view_products(request):
#     if request.method=='GET':
#         products=Product.objects.select_related('category').all()
#         serializer=ProductSerializer(products,many=True) #,context={'request':request}
#         return Response(serializer.data)
#     if request.method=='POST':
#         serializer=ProductSerializer(data=request.data) #deserializing here
#         serializer.is_valid(raise_exception=True) #when true, the lines below wont run. just throw an error then n there
#         serializer.save() #a create() method is called within the ModelSerializer, which receives serializer.validated_data and then saves it. 
#         return Response(serializer.data,status=status.HTTP_201_CREATED)
#         """
#         Long cut: 
#         if serializer.is_valid():
#             print(serializer.validated_data) #form.cleaned_data counterpart of django-form
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
        
#         else:
#             return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST) #this status is shown when field valudation fails
#         """
        


#CBV of view_products
"""
class ViewProducts(APIView):
    def get(self,request):
        products=Product.objects.select_related('category').all()
        serializer=ProductSerializer(products,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer=ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)      

"""

#using generic APIView for product list [view_products]

class ProductView(ListCreateAPIView):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer

    """use this functions to change data dynamically and 
    based on conditions logically"""
    # def get_queryset(self):
    #     return Product.objects.select_related('category').all()
    # def get_serializer_class(self):
    #     return ProductSerializer
    """to add hyperlinked related field"""
    # def get_serializer_context(self):
    #     return {'request':self.request}

class ProductViewSet(ModelViewSet):
    """Product add, delete, update, read operations.
    - Any user can see products
    - Only authenticated users can select product to cart
    - Only admin can add , update ,delete a product from the website. 
    """
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    # filterset_fields=['category_id'] #basic manual filtering
    filterset_class=ProductFilter #using django-filters package after customizing
    search_fields=['name','description','category__name']
    ordering_fields=['price']
    # pagination_class=PageNumberPagination
    pagination_class=DefaultPagination
    # permission_classes=[IsAdminUser]
    permission_classes=[IsAdminOrReadOnly]
    # permission_classes=[DjangoModelPermissions]
    # permission_classes=[DjangoModelPermissionsOrAnonReadOnly]
    # permission_classes=[FullDjangoModelPermission]

    """customizing permission using a method
    
    def get_permissions(self):
        if self.request.method=='GET':
            return [AllowAny()]
        return [IsAdminUser()]
    """


    """for basic filtering 
    
    def get_queryset(self):
        queryset=Product.objects.all()
        category_id=self.request.query_params.get('category_id')

        if category_id is not None: #why not NULL
            queryset=Product.objects.filter(category_id=category_id)
        return queryset
    """
    
    def list(self, request, *args, **kwargs):
        """-Any user can see the list of products"""
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Create a single product',
	operation_description='This feature allows a product object to be created only by Admin',
	request_body=ProductSerializer,
	responses={
		201:ProductSerializer,
		401:'Bad Request'
	    }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    

    @swagger_auto_schema(
	operation_summary='Get a single product',
	operation_description='This feature allows a product object to be read by any user',
	responses={
		200:ProductSerializer,
		401:'Bad Request'
	    }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Update a single product',
	operation_description='This feature allows a product object to be updated only by Admin',
	request_body=ProductSerializer,
	responses={
		200:ProductSerializer,
		401:'Bad Request'
	    }
    )
    def update(self, request, *args, **kwargs):
        """Update a product"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
	operation_summary='Delete a single product',
	operation_description='This feature allows a product object to be deleted only by Admin',
	request_body=ProductSerializer,
	responses={
		204:ProductSerializer,
		401:'Bad Request'
	    }
    )
    def destroy(self, request, *args, **kwargs):
        product=self.get_object()
        if product.stock>20:
            return Response({'message':'product with stock more than 20 can not be deleted'})
        self.perform_destroy(product)
        return Response(status=status.HTTP_204_NO_CONTENT) # return self.super() dile hobe na?

# @api_view(['GET','PUT','DELETE'])
# def view_specific_product(request,pk):
#     product=get_object_or_404(Product,pk=pk)
#     if request.method=='GET':
#         # product=Product.objects.all().first()
#         # product_dict={'id':product.id,'name':product.name,'price':product.price}
#         serializer=ProductSerializer(product)
#         return Response(serializer.data)
#         #DRF by default renders all number/integer as string. 
        
#     if request.method=='PUT':
#         serializer=ProductSerializer(product,data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     if request.method=='DELETE':
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    
#         """optional procedure on delete: show deleted data
#         copy_of_product=product
#         product.delete()
#         serializer=ProductSerializer(copy_of_product)
#         return Response(serializer.data,status=status.HTTP_204_NO_CONTENT)

#         """

#CBV of view_specific_product
"""
class ViewSpecificProduct(APIView):
    def get(self,request,pk):
        product=get_object_or_404(Product,pk=pk)
        serializer=ProductSerializer(product)
        return Response(serializer.data)
    
    def put(self,request,pk):
        product=get_object_or_404(Product,pk=pk)
        serializer=ProductSerializer(product,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self,reqeust,pk):
        product=get_object_or_404(Product,pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

"""

# generic view for viewSpecificProduct

class ProductDetails(RetrieveUpdateDestroyAPIView):
    queryset=Product.objects.all() #no single object query here. must be entire query set. 
    serializer_class=ProductSerializer
    # lookup_field='id' #to modify the search-field

    """modifying a generic view method
    def delete(self,request,pk):
        product=get_object_or_404(Product,pk=pk)
        if product.stock>20:
            return Response({'message':'product with stock more than 20 can not be deleted'})
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    """
    


#apply deserializing on view_categories
# @api_view()
# def view_categories(request):
#     categories=Category.objects.annotate(product_count=Count('products')).all()
#     serializer=CategorySerializer(categories,many=True)
#     return Response(serializer.data)
#     # return Response({"message":"Category list"})

class ViewCategories(APIView):
    def get(self,request):
        categories=Category.objects.annotate(product_count=Count('products')).all()
        serializer=CategorySerializer(categories,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer=CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)


# using generic view to show category list
class CategoryView(ListCreateAPIView):
    queryset=Category.objects.annotate(product_count=Count('products')).all()
    serializer_class=CategorySerializer


class CategoryViewSet(ModelViewSet):
    """Category read, create, update and delete operations
    - Normal user can only read and see the categories. 
    - Admin can create , update and delete categories"""
    permission_classes=[IsAdminOrReadOnly]
    queryset=Category.objects.annotate(product_count=Count('products')).all()
    serializer_class=CategorySerializer

    @swagger_auto_schema(
	operation_summary='Get the list of categories',
	operation_description='This feature allows the cateogry list to be read by any user',
	responses={
		200:CategorySerializer,
		401:'Bad Request'
	    }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Get a single category with its details',
	operation_description='This feature allows a category details to be read by any user',
	responses={
		200:CategorySerializer,
		401:'Bad Request'
	    }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Create a single Category',
	operation_description='This feature allows a Category object to be created only by Admin',
	request_body=CategorySerializer,
	responses={
		201:CategorySerializer,
		401:'Bad Request'
	    }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Update a single Category',
	operation_description='This feature allows a Category object to be updated only by Admin',
	request_body=CategorySerializer,
	responses={
		200:CategorySerializer,
		401:'Bad Request'
	    }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Delete a single product',
	operation_description='This feature allows a product object to be deleted only by Admin',
	request_body=ProductSerializer,
	responses={
		204:ProductSerializer,
		401:'Bad Request'
	    }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

# @api_view()
# def view_specific_category(request,pk):
#     category=get_object_or_404(Category,pk=pk)
#     serializer=CategorySerializer(category)
#     return Response(serializer.data)

"""Class based APIView of view_specific_cateogry
class ViewSpecificCategory(APIView):

    def get(self,request,pk):
        # category=get_object_or_404(Category,pk=pk)
        # we can place queryset instead of direct model name inside get_object_or_404
        category=get_object_or_404(
            Category.objects.annotate(product_count=Count('products')).all(),
                                   pk=pk
                                   )
        serializer=CategorySerializer(category)
        return Response(serializer.data)
    
    def put(self,request,pk):
        category=get_object_or_404(
            Category.objects.annotate(product_count=Count('products')).all(),
            pk=pk
            )
        serializer=CategorySerializer(category,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self,request,pk):
        category=get_object_or_404(
            Category.objects.annotate(product_count=Count('products')).all(),
            pk=pk
        )
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
"""

# using generic view for view_specific_category
"""
class CategoryDetails(RetrieveUpdateDestroyAPIView):

    queryset=Category.objects.annotate(product_count=Count('products')).all()
    serializer_class=CategorySerializer
"""

class ReviewViewSet(ModelViewSet):
    """Review read, create, update and delete operations
    - Normal user can only read and see the reviews
    - Authenticate user can create a review.
    - Authenticated user can also update and delete his own reviews 
    - Admin can create , update and delete any reviews"""
     
    # queryset=Review.objects.all()
    serializer_class=ReviewSerializer
    permission_classes=[IsReviewAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self,serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if getattr(self,'swagger_fake_view',False):
            return Review.objects.none()

        return Review.objects.filter(product_id=self.kwargs.get('product_pk'))
    
    # to send context data to serializer
    def get_serializer_context(self):
        return {'product_id':self.kwargs.get('product_pk')} #in ViewSet,instance data is stored in self.kwargs dictionary. 
        # warning=> kwargs key product_id kaj kore na. 
    
    @swagger_auto_schema(
	operation_summary='Get the list of reviews of a product',
	operation_description='This feature allows all reviews of a product to be read by any user',
	responses={
		200:ReviewSerializer,
		401:'Bad Request'
	    }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Get a single review',
	operation_description='This feature allows a review object to be read by any user',
	responses={
		200:ReviewSerializer,
		401:'Bad Request'
	    }
    )    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    

    @swagger_auto_schema(
	operation_summary='Create a single Review',
	operation_description='This feature allows a product object to be created by an authenticated user',
	request_body=ReviewSerializer,
	responses={
		201:ReviewSerializer,
		401:'Bad Request'
	    }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    

    @swagger_auto_schema(
	operation_summary='Update a single review',
	operation_description='This feature allows a review object to be updated only by Admin and the review author',
	request_body=ReviewSerializer,
	responses={
		200:ReviewSerializer,
		401:'Bad Request'
	    }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
	operation_summary='Delete a single review',
	operation_description='This feature allows a review object to be deleted only by Admin and the review author',
	request_body=ReviewSerializer,
	responses={
		204:ReviewSerializer,
		401:'Bad Request'
	    }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class ProductImageViewSet(ModelViewSet):
    serializer_class=ProductImageSerializer
    permission_classes=[IsAdminOrReadOnly]

    def get_queryset(self):
        return ProductIamge.objects.filter(product_id=self.kwargs.get('product_pk'))
    
    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs.get('product_pk'))