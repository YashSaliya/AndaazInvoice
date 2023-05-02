from django.db import models

# Add on default User Model
from django.contrib.auth.models import User

# Create your models here.
class MainCompany(models.Model):
    name = models.CharField(max_length=120)
    address1 = models.CharField(max_length = 500)
    address2 = models.CharField(max_length = 500,default= "")
    phone = models.CharField(max_length = 20,blank = True)
    email = models.EmailField(max_length = 254)
    website = models.CharField(max_length = 100,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.name 

class SisterCompanies(models.Model):
    main_company = models.ForeignKey(MainCompany, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    address = models.CharField(max_length = 500)
    phone = models.CharField(max_length = 20,blank = True)
    email = models.EmailField(max_length = 254)
    website = models.CharField(max_length = 100,blank=True)

    def __str__(self):
        return self.name

class Invoice(models.Model):
    invoiceNumber = models.AutoField(primary_key= True)
    invoiceDate = models.DateField()
    status = models.BooleanField(default =  False)
    amount = models.DecimalField(max_digits=10, decimal_places=4)
    userId = models.ForeignKey(User,on_delete=models.CASCADE)
    mainCompany = models.ForeignKey(MainCompany, on_delete=models.CASCADE)
    invoiceLink = models.CharField(max_length=2000,blank = True)


class Prices(models.Model):
    name = models.CharField(unique= True, primary_key= True, max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=4)
    userId = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} : ${self.price}'

