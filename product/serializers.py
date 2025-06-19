from rest_framework import serializers
from decimal import Decimal
from product.models import Category,Product,Review,ProductIamge
#rest_framework.org -> api guide -> serializers -> serializer fields
# from django.conf import settings #user model does not work like that on serializer
from django.contrib.auth import get_user_model

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductIamge
        fields=['id','image']

class SimpleUserSerializer(serializers.ModelSerializer):
    name=serializers.SerializerMethodField(method_name='get_current_user_name')
    class Meta:
        model=get_user_model()
        fields=['id','name']
    
    def get_current_user_name(self,obj):
        return obj.get_full_name()

# Normal serializer
# class CategorySerializer(serializers.Serializer):
#     id=serializers.IntegerField()
#     name=serializers.CharField()
#     description=serializers.CharField()

# class ProductSerializer(serializers.Serializer):
#     id=serializers.IntegerField()
#     name=serializers.CharField()
#     unit_price=serializers.DecimalField(max_digits=10,decimal_places=2,source='price')

#     price_with_tax=serializers.SerializerMethodField(method_name='calculate_tax')

#     # category=serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
#     # category=serializers.StringRelatedField() #. __str__ must be declared in related model
#     # category=CategorySerializer()
#     category=serializers.HyperlinkedRelatedField(queryset=Category.objects.all(),view_name='view-specific-category')

    
#     def calculate_tax(self,product):
#         # return product.price*Decimal(1.1)
#         return round(product.price * Decimal(1.1),2)



# Model Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name','description','product_count']

    product_count=serializers.IntegerField(read_only=True) #value assigned in views.py
    # ekhane read_only=true ditei hobe. nahole post,update e ei field not found diye error dekhabe
    
    '''un-optimized approach 
    
    product_count=serializers.SerializerMethodField(method_name='get_product_count')

    def get_product_count(self,category):
        return Product.objects.filter(category=category).count()
    '''


class ProductSerializer(serializers.ModelSerializer):
    images=ProductImageSerializer(many=True,read_only=True)
    class Meta:
        model=Product
        fields=['id','name','description','price','stock','category','images','price_with_tax']

    # category=serializers.HyperlinkedRelatedField(queryset=Category.objects.all(),view_name='view-specific-category')
    price_with_tax=serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self,product):
        return round(product.price * Decimal(1.1),2)
    #field-level validation
    def validate_price(self,price):
        if price<0:
            raise serializers.ValidationError('Price Could Not be Negative')
        else: 
            return price
    """how .save() bts:
    
    def create(self, validated_data):
        product=Product(**validated_data) #creating product object with data from views.py  . not yet saved
        product.other='something'  #modifying the data before saving
        product.save()
        return product
    """
        

class ReviewSerializer(serializers.ModelSerializer):
    # user=serializers.CharField(read_only=True) #one process to make a serializer field hidden from user input form
    # user=SimpleUserSerializer()  #call kora lage
    user=serializers.SerializerMethodField(method_name='get_user')
    class Meta:
        model=Review
        fields=['id','user','product','comment','ratings']
        read_only_fields=['user','product']
        # hide jodi kortei hoy, tahole first e serializer e ei duita field include korlam keno?
    
    def get_user(self,obj):
        return SimpleUserSerializer(obj.user).data


    # modifying the create() to dynamically add product_id to the review in the backend without taking user input from frontend
    def create(self, validated_data):
        product_id=self.context['product_id'] #sent by get_context_data() from view
        review=Review.objects.create(product_id=product_id,**validated_data)
        return review

