from django.shortcuts import render
from django.http import HttpResponse
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil
import json
# Create your views here.

def index(request):
    allprods=[]
    catprods=Product.objects.values('Category')
    cats={item['Category'] for item in catprods}
    for cat in cats:
        prod=Product.objects.filter(Category=cat)
        n=len(prod)
        nSlides=(n//4) + ceil((n/4)-(n//4))
        allprods.append([prod,range(1,nSlides),nSlides])
    params={'allprods':allprods}
    return render(request,"shop/index.html",params)


def About(request):
    return render(request,'shop/about.html')


def contact(request):
    x=False
    if request.method=="POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        contact=Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        x=True
        
    return render(request,'shop/contact.html',{'thank':x})
    


def Tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/track.html')


def Search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('Category', 'id', 'Sub_category')
    cats = {item['Category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(Category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.Product_name.lower() or query in item.Category.lower() or query in item.Sub_category.lower():
        return True
    else:
        return False


def ProductView(request, myid):
    product=Product.objects.filter(id=myid)
    return render(request,"shop/product.html",{'product':product[0]})


def Checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson')
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        email = request.POST.get('email')
        address = request.POST.get('address1') + " " + request.POST.get('address2', '')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        if amount != '0':
            order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
            order.save()
            update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
            update.save()
            thank = True
            id = order.order_id
            return render(request, 'shop/checkout.html',context={'thank':thank,'id':id})
        else:
            return render(request, 'shop/checkout.html',context={'msg':'Your cart is empty, please add some items to your cart before checking out!'})


    return render(request, 'shop/checkout.html')
