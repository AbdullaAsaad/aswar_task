from django.contrib import admin
from django.urls import path
from account.controller import account_router
from products.api_controllers.products import products_router
from ninja import NinjaAPI

api = NinjaAPI()

api.add_router('account/', account_router)
api.add_router('products/',  products_router)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
