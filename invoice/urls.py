from django.urls import path
from . views import *


urlpatterns = [
    path("",createInvoice,name = "invoice"),
    path('login',loginrequest,name = 'login'),
    path('master',home,name= 'master'),
    path('updateMealDetails',updateMealDetails,name= "updateMealDetails"),
    path('addcmp',addCompany,name = 'addcmp'),
    path('editcmp',editcmp,name='editcmp'),
    path('delcmp',delCompany,name ='delcmp'),
    path('ls',listInvoices,name= "listInvoices"),
    path('logout',lgout,name = 'logout')
]
