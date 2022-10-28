from sqlite3 import Date
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from pydantic import UUID4
from products.models import Product

products_router = Router(tags=['Products'])

class ProductOut(Schema):
    name:str
    description:str
    expired:Date
    image:str=None
    
    # Get all products
@products_router.get('/', response=list[ProductOut] , url_name='get_product' )
def list_products(request):
    products = Product.objects.all()
    return products

    # get single product
@products_router.get('/{id}', response={200: ProductOut})
def get_product(request, id: UUID4):
    try:
        product = Product.objects.get(id=id)
        return 200, product
    except Product.DoesNotExist:
        return 404, {'msg': 'There is no product with that id.'}
    
    # create new product 
    
@products_router.post("/")
def create_product(request, payload: ProductOut):
    product = Product.objects.create(**payload.dict())
    return 200,{"name": product.name}

    # edit the product 
    
@products_router.put("/{id}")
def update_product(request, id: UUID4, payload: ProductOut):
    product = get_object_or_404(Product, id=id)
    for attr, value in payload.dict().items():
        setattr(product, attr, value)
    product.save()
    return 200, {"updated": True}

    # delete the product 
    
@products_router.delete("/{id}")
def delete_product(request, id: UUID4):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return 200,{"deleted": True}