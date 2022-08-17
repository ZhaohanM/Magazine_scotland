from django.http.response import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from magportal.models import UserProfile, Magazine, Category
from magportal.forms import UserForm, MagazineForm, EditUserForm
from datetime import datetime, timedelta, date
from dateutil.relativedelta import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse 
from django.views.decorators.csrf import csrf_exempt 
from django.conf import settings 
import stripe
import json
from django.views.generic import TemplateView

# Create your views here.

def home(request):
    staff = False
    if request.user.is_staff:
        staff = True
    return render(request, 'magportal/home.html', {'staff':staff})

def landing(request):
    return render(request, 'magportal/landing.html')

def contact(request):
    return render(request, 'magportal/contact.html')

def browse_magazines(request):
    magazine_list = Magazine.objects.order_by('-Date')
    category_list = Category.objects.all()
    context_dict = {}
    context_dict['results'] = magazine_list
    context_dict['cats'] = category_list
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(UserAccount=request.user)
        except:
            return render(request, 'magportal/magazines.html', context=context_dict)
        membership = False
        date = datetime.now().date()
        date2 = profile.Membership
        if date2 > date:
            membership = True
        context_dict['membership'] = membership
        context_dict['favourites'] = profile.Favourites.all()
        response = render(request, 'magportal/magazines.html', context=context_dict)
        return response
    else:
        return render(request, 'magportal/magazines.html', context=context_dict)

def browse_category(request, category_Name_Slug):
    context_dict = {}
    try:
        cat = Category.objects.get(Slug = category_Name_Slug)
        magazine_list = cat.Mags.order_by('-Date')
        context_dict['results'] = magazine_list
        category_list = Category.objects.all()
        context_dict['cats'] = category_list
        context_dict['cat'] = cat
    except Category.DoesNotExist:
        return render(request, 'magportal/magazines.html')
    
    return render(request, 'magportal/magazines.html', context_dict)

def add_magazine(request):
    
    form = MagazineForm()
    if request.method == "POST":
        print(request.POST)
        form = MagazineForm(request.POST)
        if form.is_valid():
            magazine = form.save(commit=False)
            magazine.Date = timezone.now()
            if 'Image' in request.FILES:
                magazine.Image = request.FILES['Image']
            magazine.save()
            magazine.Categories.add(request.POST.get('Categories'))
            Cat = Category.objects.get(CategoryID=request.POST.get('Categories'))
            Cat.Mags.add(magazine)
            magazine.save()
            Cat.save()
            
            return HttpResponseRedirect('/')
        else:
            print(form.errors)
    
    return render(request, 'magportal/add_magazine.html', {'magazine_form':form})

def register(request):
    registered = False
    if request.method == 'POST':
            user_form = UserForm(request.POST)
            
            if user_form.is_valid():
                user = user_form.save()
                user.set_password(user.password)
                user.save()
                userprofile=UserProfile.objects.get_or_create(UserAccount=user,UserID=user.id)[0]
                userprofile.Membership = str(datetime.now().strftime("%Y-%m-%d"))
                userprofile.save()
                login(request, user)
                return redirect(reverse('magportal:home'))
            else:
                print(user_form.errors,)
                return render(request, 'magportal/register.html', context = {'user_form': user_form, 'registered' : registered, 'errors' : user_form.errors,})
        
    else: 
        user_form = UserForm()

        
    return render(request, 'magportal/register.html', context = {'user_form': user_form, 'registered' : registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('magportal:home'))
            else:
                return HttpResponse("Your Magportal account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'magportal/login.html')
@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('magportal:home')) 

def view_profile(request,username):
    try:
        profile = UserProfile.objects.get(Slug=username)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.get(UserAccount=request.user)
    context_dict = {}
    membership = False
    date = datetime.now().date()
    date2 = profile.Membership
    if date2 > date:
        membership = True
    context_dict = {'profile': profile, 'membership': membership}
    return render(request, 'magportal/view_profile.html', context_dict)

@login_required
def edit_profile(request, username):
    #fml
    try:
        profile_to_edit = UserProfile.objects.get(UserAccount=request.user)
    except UserProfile.DoesNotExist:
        return HttpResponse("Trying to edit a profile that doesn't exist")

    membership = False
    date = datetime.now().date()
    date2 = profile_to_edit.Membership
    if date2 > date:
        membership = True
    if request.method == 'POST':
        user_form = EditUserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            if request.POST['username']:
                newusername=request.POST['username']
                request.user.username = newusername
            if request.POST['password']:
                request.user.set_password(request.POST['password'])
            
            user_form.save()
            user.save()
            profile_to_edit.save()

            #return redirect(reverse('magportal:view_profile', kwargs={'username': profile_to_edit.Slug}))
            return render(request, 'magportal/edit_profile.html', {'user_form': user_form,'membership':membership, 'profile':profile_to_edit})
        else:
            return render(request, 'magportal/edit_profile.html', {'user_form': user_form,'membership':membership, 'profile':profile_to_edit})
    else:
        return render(request, 'magportal/edit_profile.html', {
            'user_form': EditUserForm(), 'membership':membership, 'profile':profile_to_edit
        })

@login_required   
def membership(request):
    context_dict={}
    try:
        profile = UserProfile.objects.get(UserAccount=request.user)
    except:
        return render(request, 'magportal/magazines.html', context=context_dict)
    membership = False
    date = datetime.now().date()
    date2 = profile.Membership
    if date2 > date:
        membership = True
    context_dict['profile'] = profile
    context_dict['membership'] = membership
    return render(request, 'magportal/membership.html', context_dict)

@login_required
def cancel_membership(request):
    try:
        profile = UserProfile.objects.get(UserAccount=request.user) 
    except UserProfile.DoesNotExist:
        return render(request, 'magportal/home.html')
    date = datetime.now().date()
    profile.Membership = date
    profile.save()
    
    context_dict = {}
    membership = False
    date = datetime.now().date()
    date2 = profile.Membership
    if date2 > date:
        membership = True
    context_dict = {'profile': profile, 'membership': membership}
    return render(request, 'magportal/membership.html', context_dict)

@login_required    
def discountcode(request, mag_name_Slug):
    try:
        profile = UserProfile.objects.get(UserAccount=request.user) 
    except UserProfile.DoesNotExist:
        return render(request, 'magportal/home.html')
    try:
        mag_to_favourite = Magazine.objects.get(Slug = mag_name_Slug)
    except Magazine.DoesNotExist:
        return HttpResponse("Sorry, something went wrong!")
    membership = False
    date = datetime.now().date()
    date2 = profile.Membership
    if date2 > date:
        membership = True
    context_dict = {'profile': profile, 'membership': membership, 'result':mag_to_favourite}
    
    month = int(datetime.now().month)
    year = int(datetime.now().year)
    hashed = hex(hash((mag_to_favourite.Discount) * (profile.MembershipID+1)*month)-year)[-8:]
    code = mag_to_favourite.Discount + "-" + hashed
    context_dict['hashcode'] = code
    
    if membership == False:
        return render(request, 'magportal/membership.html', context_dict)
    
    return render(request, 'magportal/discountcode.html', context_dict)


@staff_member_required 
def view_codes(request):
    month = int(datetime.now().month)
    year = int(datetime.now().year)
    
    mags = Magazine.objects.all()
    
    codes = []
    for mag in mags:
        magcodes = []
        for i in range(30):
            hashed = hex(hash((mag.Discount) * (i+1)*month)-year)[-8:]
            code = mag.Discount + "-" + hashed
            magcodes.append(code)
        codes.append(magcodes)
        
    return render(request, 'magportal/codes.html', {'codes':codes})
            
@login_required
def favourite(request, mag_name_Slug):
    try:
        mag_to_favourite = Magazine.objects.get(Slug = mag_name_Slug)
    except Magazine.DoesNotExist:
        return HttpResponse("Sorry, something went wrong!")
    

    logged_in_profile = UserProfile.objects.get(UserAccount=request.user)
    logged_in_profile.Favourites.add(mag_to_favourite)
    logged_in_profile.save()

    
    
    return redirect(reverse('magportal:browse_magazines'))

@login_required
def unfavourite(request, mag_name_Slug):
    try:
        mag_to_favourite = Magazine.objects.get(Slug = mag_name_Slug)
        mag_to_favourite.save()
    except Magazine.DoesNotExist:
        return HttpResponse("Sorry, something went wrong!")
    
    logged_in_profile = UserProfile.objects.get(UserAccount=request.user)
    logged_in_profile.Favourites.remove(mag_to_favourite)
    logged_in_profile.save()
    
    return redirect(reverse('magportal:browse_magazines'))

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://127.0.0.1:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                client_reference_id = request.user.id,
                success_url=domain_url + '',
                cancel_url=domain_url + 'membership/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'price': 'price_1KTbeRAggb8ZLVL8Q8piuQqP',
                        'quantity': 1,
                    },
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        
@csrf_exempt
def create_checkout_session_6(request):
    if request.method == 'GET':
        domain_url = 'http://127.0.0.1:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                client_reference_id = request.user.id,
                success_url=domain_url + '',
                cancel_url=domain_url + 'membership/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[

                    {
                        'price': 'price_1KWJNsAggb8ZLVL8gLbqq86b',
                        'quantity': 1,
                    },
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        
        
@csrf_exempt
def create_checkout_session_year(request):
    if request.method == 'GET':
        domain_url = 'http://127.0.0.1:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                client_reference_id = request.user.id,
                success_url=domain_url + '',
                cancel_url=domain_url + 'membership/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'price': 'price_1KWJOSAggb8ZLVL8Lzr97pCl',
                        'quantity': 1,
                    },
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

class CancelledView(TemplateView):
    template_name = 'magportal/cancelled.html'
    
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        #limit members to 30
        users = UserProfile.objects.all()
        members = 0
        max_member_id = 0
        #check whether there are over 30 members
        for profile in users:
            date = datetime.now().date()
            date2 = profile.Membership
            if date2 > date:
                members += 1
            if profile.MembershipID is None:
                pass
            else:
                if profile.MembershipID > max_member_id:
                    max_member_id = profile.MembershipID
                    
        if members > 29:
            return redirect(reverse('magportal:browse_magazines')) 
        
        if body['data']['object']['amount_total'] == 900:
            
            try:
                profile = UserProfile.objects.get(UserID=body['data']['object']['client_reference_id'])
            except UserProfile.DoesNotExist:
                return render(request, 'magportal/home.html')
            date = profile.Membership
            date = date + relativedelta(months=6)
            profile.Membership = date
            profile.MembershipID = max_member_id+1
            profile.save()
            
            
        elif body['data']['object']['amount_total'] == 1500:
            
            try:
                profile = UserProfile.objects.get(UserID=body['data']['object']['client_reference_id'])
            except UserProfile.DoesNotExist:
                return render(request, 'magportal/home.html')
            date = profile.Membership
            date = date + relativedelta(months=6)
            profile.Membership = date
            profile.MembershipID = max_member_id+1
            profile.save()
            
        elif body['data']['object']['amount_total'] == 2500:
            try:
                profile = UserProfile.objects.get(UserID=body['data']['object']['client_reference_id'])
            except UserProfile.DoesNotExist:
                return render(request, 'magportal/home.html')
            date = profile.Membership
            date = date + relativedelta(months=12)
            profile.Membership = date
            profile.MembershipID = max_member_id+1
            profile.save()
            
            
    return HttpResponse(status=200)
