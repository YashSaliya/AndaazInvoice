from django.shortcuts import render
from .models import *
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages 
from django.shortcuts import redirect
import firebase_admin
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from firebase_admin import storage
from xhtml2pdf import pisa
import datetime
from weasyprint import HTML, CSS
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.
import requests
from restInvoice.settings import *
#create credential instance
cred = firebase_admin.credentials.Certificate("andaazinvoice-firebase-adminsdk-10x6t-07a767ba18.json")
firebase_admin.initialize_app(cred)

test_data = '{"gst":"false","gratuity":"false","2313":[{"mealDate":"2023-04-07","mealType":"1","adults":"2","children":"2","infants":"2","desc":"2313","billingCompany":"7"},{"mealDate":"2023-04-20","mealType":"","adults":"2","children":"2","infants":"2","desc":"2313","billingCompany":"7"}],"2313 ads":[{"mealDate":"2023-04-13","mealType":"","adults":"2","children":"2","infants":"2","desc":"2313 ads","billingCompany":"7"}]}'

@login_required(login_url='/login')
def updateMealDetails(request):
    nameList =  {'b1':'children Breakfast','b2':'adults Breakfast','b3':'infants Breakfast'
                ,'l1':'children Lunch','l2':'adults Lunch','l3':'infants Lunch'
                ,'d1':'children Dinner','d2':'adults Dinner','d3':'infants Dinner'}
    if request.method == "GET":
        return render(request,'master.html')
    else:
        data = json.loads(request.body)
        data = data['changeRates']
        for desc in data:
            priceObject = Prices.objects.get(name = nameList[desc])
            priceObject.price = float(data[desc])
            priceObject.save()
    return HttpResponse("Success")

def storeToFirebase(result,context_dict):
    try:
        st = storage.bucket("andaazinvoice.appspot.com")
        blob = st.blob(f"{context_dict['cmp'].name} {context_dict['date']}--{context_dict['invoiceNumber']}.pdf")
        blob.upload_from_string(result, content_type='application/pdf')
        blob.make_public()
        print(blob.public_url)
        return blob.public_url
    #catch connection exception
    except:
        return storeToFirebase(result,context_dict)

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    result = HTML(string= html).write_pdf()
    return result
    # return storeToFirebase(result,context_dict)
    # try:
    #     st = storage.bucket("andaazinvoice.appspot.com")
    #     blob = st.blob(f"{context_dict['cmp'].name} {context_dict['date']}--{context_dict['invoiceNumber']}.pdf")
    #     blob.upload_from_string(result, content_type='application/pdf')
    #     blob.make_public()
    #     print(blob.public_url)
    #     return blob.public_url
    # except:
    #     return render_to_pdf(template_src,context_dict)


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

    gst = temp * (int(data['gst'])) / 100
    gratuity = temp * (int(data['gratuity'])) / 100
    totalAmount += gst + gratuity
    
    chargesData = {'GST':gst,'Gratuity':gratuity,'Total Amount':totalAmount}
    del(data['gst'])
    del(data['gratuity'])
    return (chargesData,data)


@login_required(login_url='/login')
@csrf_exempt
def createInvoice(request):
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
        invoice = Invoice()
        invoice.amount = renderedData['Total Amount']
        invoice.invoiceDate = datetime.datetime.now()
        invoice.userId = User.objects.all()[0]
        invoice.mainCompany = cmp
        invoice.save()
        invoiceNumber = invoice.invoiceNumber + 100
        date = invoice.invoiceDate.strftime("%b %d %Y")
        contextDict = {'data':data,'charges':renderedData,'adults':adults,'children':children,'infants':infants,'cmp':cmp,'date':date,'invoiceNumber':invoiceNumber}
        renderedResponse = render_to_pdf('invoiceTemplate.html',context_dict=contextDict)
        invoice.invoiceLink = storeToFirebase(renderedResponse,contextDict)
        invoice.invoiceDueDate = invoice.invoiceDate + datetime.timedelta(days=30)
        invoice.save()
        return HttpResponse("success")

def loginrequest(request):
    if request.method == "POST":
        username = request.POST['username'].strip()
        password = request.POST['password'].strip()
        user = authenticate(request,username = username,password = password)
        if user:
            login(request,user)
            return redirect(home)
        else:
            messages.error(request,"Invalid Credentials")
            return redirect('login')
    return render(request,'login.html')

@login_required(login_url='/login')
def lgout(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/login')
def home(request):
    companies = MainCompany.objects.filter(user = request.user.id)
    adBfPrice = Prices.objects.get(name = 'adults Breakfast')
    chBfPrice = Prices.objects.get(name = 'children Breakfast')
    inBfPrice = Prices.objects.get(name = 'infants Breakfast')
    adLuPrice = Prices.objects.get(name = 'adults Lunch')
    chLuPrice = Prices.objects.get(name = 'children Lunch')
    inLuPrice = Prices.objects.get(name = 'infants Lunch')
    adDiPrice = Prices.objects.get(name = 'adults Dinner')
    chDiPrice = Prices.objects.get(name = 'children Dinner')
    inDiPrice = Prices.objects.get(name = 'infants Dinner')
    #create a dictionary with above values
    context = {'adBf':adBfPrice.price,'chBf':chBfPrice.price,'inBf':inBfPrice.price,
                'adLu':adLuPrice.price,'chLu':chLuPrice.price,'inLu':inLuPrice.price,
                'adDi':adDiPrice.price,'chDi':chDiPrice.price,'inDi':inDiPrice.price,
                'companies':companies}
    return render(request,'master.html',context)


def cmpDetails(request,cmpId):
    cmp = MainCompany.objects.get(id = cmpId)
    return JsonResponse(
            {
            'id':cmp.id,
            'name':cmp.name,
            'address1':cmp.address1,
            'address2':cmp.address2,
            'email':cmp.email,
            }
    )

def listInvoices(request):
    invoices = Invoice.objects.filter(userId = User.objects.all()[0])
    return render(request,'listInvoice.html',context = {"invoices":invoices})



@login_required(login_url='/login')
def editcmp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        cmp = MainCompany.objects.get(id = int(data['id']))
        cmp.name = data['name']
        cmp.address1 = data['address1']
        cmp.address2 = data['address2']
        cmp.email = data['email']
        cmp.save()
        response = {'success':"Company updated Successfully !"}
        return JsonResponse(response)
    return redirect(home)

@login_required(login_url='/login')
def delCompany(request):
    if request.method == "POST":
        id = json.loads(request.body)['id']
        id = int(id)
        cmp = MainCompany.objects.get(id = id)
        cmp.delete()
        messages.info("Company has been deleted")
        response = {'success':"Record is removed! "}
        return JsonResponse(response)

@login_required(login_url='/login')
def addCompany(request):
    if request.method == "POST":
        data = json.loads(request.body)
        cmp = MainCompany()
        cmp.name = data['name']
        cmp.address1 = data['address1']
        cmp.address2 = data['address2']
        cmp.email = data['email']
        cmp.user = request.user
        cmp.save()
        response = {'success':"Company added Successfully !"}
        return JsonResponse(response)
    else:
        return redirect(home)



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
    date = datetime.datetime.now()
    date = date.strftime("%b %d %Y")
    invoiceNumber = 101
    contextDict = {'data':data,'charges':renderedData,'adults':adults,'children':children,'infants':infants,'cmp':cmp,'date':date,'invoiceNumber':invoiceNumber}
    renderedResponse = render_to_pdf('invoiceTemplate.html',contextDict)
    return HttpResponse(renderedResponse,content_type='application/pdf')



@login_required(login_url='/login')
def sendMail(request):
    from django.core.mail import send_mail,EmailMessage
    # send_mail("Subject",'message','yashsaliya2002@gmail.com',['yashsaliya2002@gmail.com'],fail_silently=False)
    if request.method == "POST":
        data = json.loads(request.body)
        id = int(data['id'])
        subject = data['subject']
        body = data['body']
        invoice = Invoice.objects.get(invoiceNumber = id)
        urlInvoice = invoice.invoiceLink
        # fetch pdf from url and prepare an email message and attach the file fetched to the mail
        response = requests.get(urlInvoice,stream = True)
        # prepare emailmessage
        # get host name from settings 
        host = EMAIL_HOST_USER
        # get maincompany from invoice 
        maincompany =  invoice.mainCompany.email
        message = EmailMessage(subject,body,host,[maincompany])
        message.attach("invoice.pdf",response.content)
        message.send(fail_silently=False)
        invoice.mailSent = True
        invoice.save()
        
    return HttpResponse("Hello")

@login_required(login_url='/login')
def changePaidDate(request):
    if request.method == "POST":
        data = json.loads(request.body)
        invoice = Invoice.objects.get(invoiceNumber = int(data['id']))
        invoice.invoicePaidDate = datetime.datetime.strptime(data['paidDate'],"%d-%m-%Y")
        invoice.status = True
        invoice.save()
        return JsonResponse({'success':"Date updated Successfully !"})