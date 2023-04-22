from django.shortcuts import render
from .models import *
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt


test_data = '{"gst":"false","gratuity":"false","2313":[{"mealDate":"2023-04-07","mealType":"1","adults":"2","children":"2","infants":"2","desc":"2313","billingCompany":"1"},{"mealDate":"2023-04-20","mealType":"","adults":"2","children":"2","infants":"2","desc":"2313","billingCompany":"1"}],"2313 ads":[{"mealDate":"2023-04-13","mealType":"","adults":"2","children":"2","infants":"2","desc":"2313 ads","billingCompany":"1"}]}'
# Create your views here.
def calc(data):

    def calcMeal(mealType, adults,children, infants):
        total = 0
        if mealType == "BreakFast":
            adBfPrice = Prices.objects.get(name = 'adults Breakfast')
            chBfPrice = Prices.objects.get(name = 'children Breakfast')
            inBfPrice = Prices.objects.get(name = 'infants Breakfast')
            total += adBfPrice.price * adults + chBfPrice.price * children + inBfPrice.price * infants
        elif mealType == "Lunch":
            adLuPrice = Prices.objects.get(name = 'adults Lunch')
            chLuPrice = Prices.objects.get(name = 'children Lunch')
            inLuPrice = Prices.objects.get(name = 'infants Lunch')
            total += adLuPrice.price * adults + chLuPrice.price * children + inLuPrice.price * infants
        else:
            adDiPrice = Prices.objects.get(name = 'adults Dinner')
            chDiPrice = Prices.objects.get(name = 'children Dinner')
            inDiPrice = Prices.objects.get(name = 'infants Dinner')
            total += adDiPrice.price * adults + chDiPrice.price * children + inDiPrice.price * infants
        return total

    totalAmount = 0
    for desc in data:
        if desc in ('gst','gratuity'):
            continue
        for meal in data[desc]:
            adultsC = int(meal['adults']) // 20
            if  adultsC > 0:
                meal['Complimentary'] = str(adultsC)
                meal['adults'] = str(int(meal['adults']) - adultsC)
            if meal['mealType'] == "1":
                totalAmount += calcMeal("BreakFast",int(meal['adults']),int(meal['children']),int(meal['infants']))
            elif meal['mealType'] == "2":
                totalAmount += calcMeal("Lunch",int(meal['adults']),int(meal['children']),int(meal['infants']))
            else:
                totalAmount += calcMeal("Dinner",int(meal['adults']),int(meal['children']),int(meal['infants']))
            meal['adults'] = int(meal['adults'])
            meal['children'] = int(meal['children'])
            meal['infants'] = int(meal['infants'])
    temp = totalAmount

    gst = 0
    gratuity = 0
    if data['gst'] == "true": gst = temp*18/100
    if data['gratuity'] == "true":
        gratuity = temp*10/100
    totalAmount += gst + gratuity
    
    chargesData = {'GST':gst,'Gratuity':gratuity,'Total Amount':totalAmount}
    del(data['gst'])
    del(data['gratuity'])
    return (chargesData,data)


def login(request):
    return render(request,'login.html')


@csrf_exempt
def createInvoice(request):
    request.user = User.objects.all()[0]
    user = request.user.id
    mainCompanies = MainCompany.objects.filter(user = user)
    if request.method == "GET":
        return render(request, 'createInvoice.html',{'companies':mainCompanies})
    else:
        data = json.loads(request.body)
        renderedData,data = calc(data)
        adBfPrice = Prices.objects.get(name = 'adults Breakfast')
        chBfPrice = Prices.objects.get(name = 'children Breakfast')
        inBfPrice = Prices.objects.get(name = 'infants Breakfast')
        adLuPrice = Prices.objects.get(name = 'adults Lunch')
        chLuPrice = Prices.objects.get(name = 'children Lunch')
        inLuPrice = Prices.objects.get(name = 'infants Lunch')
        adDiPrice = Prices.objects.get(name = 'adults Dinner')
        chDiPrice = Prices.objects.get(name = 'children Dinner')
        inDiPrice = Prices.objects.get(name = 'infants Dinner')

        adults = {}
        children = {}
        infants = {}
        adults['Breakfast'] = adBfPrice.price
        adults['Lunch'] = adLuPrice.price
        adults['Dinner'] = adDiPrice.price

        children['Breakfast'] = chBfPrice.price
        children['Lunch'] = chLuPrice.price
        children['Dinner'] = chDiPrice.price

        infants['Breakfast'] = inBfPrice.price
        infants['Lunch'] = inLuPrice.price
        infants['Dinner'] = inDiPrice.price
        cmpId = None
        for key in data:
            for meal in data[key]:
                cmpId = int(meal['billingCompany'])
                break
            break
        cmp = MainCompany.objects.get(id = cmpId)
        print(cmp.name)
        return render(request,"invoiceTemplate.html",{'data':data,'charges':renderedData,'adults':adults,'children':children,'infants':infants,'cmp':cmp})



def home(request):
    return render(request,'master.html')


def listInvoice(request):
    return render(request,"listInvoice.html")
    pass


def testInvoice(request):
    data = json.loads(test_data)
    renderedData,data = calc(data)
    adBfPrice = Prices.objects.get(name = 'adults Breakfast')
    chBfPrice = Prices.objects.get(name = 'children Breakfast')
    inBfPrice = Prices.objects.get(name = 'infants Breakfast')
    adLuPrice = Prices.objects.get(name = 'adults Lunch')
    chLuPrice = Prices.objects.get(name = 'children Lunch')
    inLuPrice = Prices.objects.get(name = 'infants Lunch')
    adDiPrice = Prices.objects.get(name = 'adults Dinner')
    chDiPrice = Prices.objects.get(name = 'children Dinner')
    inDiPrice = Prices.objects.get(name = 'infants Dinner')

    adults = {}
    children = {}
    infants = {}
    adults['Breakfast'] = adBfPrice.price
    adults['Lunch'] = adLuPrice.price
    adults['Dinner'] = adDiPrice.price

    children['Breakfast'] = chBfPrice.price
    children['Lunch'] = chLuPrice.price
    children['Dinner'] = chDiPrice.price

    infants['Breakfast'] = inBfPrice.price
    infants['Lunch'] = inLuPrice.price
    infants['Dinner'] = inDiPrice.price
    cmpId = None
    for key in data:
        for meal in data[key]:
            cmpId = int(meal['billingCompany'])
            break
        break
    cmp = MainCompany.objects.get(id = cmpId)
    print(cmp.name)
    return render(request,"invoiceTemplate.html",{'data':data,'charges':renderedData,'adults':adults,'children':children,'infants':infants,'cmp':cmp})

    
