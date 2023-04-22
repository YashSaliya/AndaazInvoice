from django.urls import path
from . views import *


urlpatterns = [
    path("",createInvoice,name = "invoice"),
    path('listInvoice',listInvoice,name = 'listInvoices'),
    path('testInvoiceTemplate',testInvoice,name='test1'),
    path('login',login,name = 'login'),
    path('master',home,name= 'master'),
]
