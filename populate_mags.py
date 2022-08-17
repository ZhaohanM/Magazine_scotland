import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boomsaloon.settings')

import django
django.setup()

from magportal.models import Magazine, Category, UserProfile
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from django.contrib.auth.hashers import make_password

def populate():

    useraccounts = [{'username':'TestUsername',
                     'password':'TestPassword',
                     'email':'TestEmail@gmail.com'},
                    {'username':'CreativeUsernameHere',
                     'password':'CreativePassword',
                     'email':'CreativeUsernameHere@gmail.com'},
                    {'username':'NatePham',
                     'password':'NatePassword',
                     'email':'Natefrost@gmail.com'},
                     {'username':'cloadmin',
                     'password':'clopassword123',
                     'email':'cloadmin@email.com'},]
    
    magazines  = [   {'name':'Gold Flake Point: A music journal',
                     'description': 'Placeholder description for the Gold Flake Point',
                     'magazine_image': 'magazine_images/Magazine_photo1.jpg',
                     'date': '2021-9-10',
                     'URL': 'https://goldflakepaint.limitedrun.com/products/712573-a-music-journal-issue-ten',
                     'code':'GFPcode',
                     'Price' : '9.99',
                     'DiscountPrice' : '7.99',},
                    {'name':'COUNTERPOINT: The Play Issue',
                    'description': 'Placeholder description for the COUNTERPOINT magazine',
                    'magazine_image': 'magazine_images/Magazine_photo.jpg',
                    'date': '2021-7-27',
                    'URL':'https://www.google.com',
                    'code':'CPoint',
                    'Price' : '10.99',
                    'DiscountPrice' : '7.99',},
                     {'name':'Magazine3',
                    'description': 'This is a test description for a test magazine',
                    'magazine_image': 'magazine_images/nuva.png',
                    'date': '2021-10-11',
                    'URL':'https://www.google.com',
                    'code': 'Discount',
                    'Price' : '9.99',
                    'DiscountPrice' : '7.99',},
                    {'name':'boom saloon',
                    'description': 'Placeholder description for Boom Saloon',
                    'magazine_image': 'magazine_images/boomsaloon.png',
                    'date': '2022-9-1',
                    'URL':'https://www.boomsaloon.com/',
                    'code': 'bsaloon',
                    'Price' : '11.99',
                    'DiscountPrice' : '9.99',},
                     {'name':'Sweet Tooth',
                    'description': 'Placeholder description for Sweet Tooth',
                    'magazine_image': 'magazine_images/sweettooth.png',
                    'date': '2022-3-16',
                    'URL':'https://www.moma.org/magazine/articles/709',
                    'code': 'SweetT',
                    'Price' : '16.99',
                    'DiscountPrice' : '12.99',}]
    

    categories = [{'name':'Art',
                   'magazines':[2,1,4]},
                  {'name':'Music',
                   'magazines':[2]},
                  {'name':'Food',
                   'magazines':[1, 5]},
                  {'name':'Business',
                   'magazines':[1]},
                  {'name': 'Fashion',
                   'magazines':[3,2,4]},
                  {'name': 'Sports',
                   'magazines':[1,2,5]}]


    for user in useraccounts:
        add_user(user['username'],user['password'],user['email'], datetime.now().strftime("%Y-%m-%d"))

    for magazine in magazines:
        add_magazine(magazine['name'],magazine['description'],magazine['magazine_image'],magazine['URL'],magazine['code'], magazine['Price'], magazine['DiscountPrice'],magazine['date'],)

    for category in categories:
        add_category(category['name'], category['magazines'])
        #mtm_category(category['name'], category['magazines'])
        
    for user in useraccounts:
        add_favourites(user['username'],)
        
    cloadmin = UserProfile.objects.get(Slug='cloadmin')
    cloadmin.MembershipID=1
    cloadmin.Membership = cloadmin.Membership + relativedelta(months=20)
    cloadmin.save()
    user = User.objects.get(username="cloadmin")
    user.is_staff = True
    user.is_superuser = True
    user.save()
            
def add_user(username, password, email, date=datetime.now):
    try:
        useraccount = User.objects.create_user(username)
        userprofile=UserProfile.objects.get_or_create(UserAccount=useraccount,UserID=useraccount.id)[0]
    except:
        useraccount = User.objects.get(username=username)
        userprofile=UserProfile.objects.get_or_create(UserAccount=useraccount,UserID=useraccount.id)[0]
    useraccount.username=username
    useraccount.password= make_password(password)
    useraccount.email=email
    userprofile.Membership=str(date)
    useraccount.save()      
    userprofile.save()
    return useraccount, userprofile


def add_magazine(name, description, image, url, code, price, discountprice, date=datetime.now,):
    
    magazine = Magazine.objects.filter(Name=name, Description=description)
    if magazine.exists():
        pass
    else:
        magazine = Magazine.objects.create(Name=name, Description=description, Image=image, URL=url, Price=price, DiscountPrice=discountprice, Date=datetime.now())
        magazine.Name=name
        magazine.Description=description
        magazine.URL=url
        if image != "":
            magazine.DemoImage="magazine_images/"+image
        magazine.Date=date
        magazine.Discount=code
        magazine.Price=price
        magazine.DiscountPrice=discountprice
        magazine.save()
    return magazine
      
                                            
def add_category(name, magazines):
    category = Category.objects.filter(Name=name)
    if category.exists():
        pass
    else:
        category = Category.objects.create(Name=name)
        for magid in magazines:
            mag=Magazine.objects.get(MagazineID=magid)
            category.Mags.add(mag)
            mag.Categories.add(category)
            mag.save()
        category.save()
    return category

def add_favourites(username):
    try:
        useraccount = User.objects.create_user(username)
        userprofile=UserProfile.objects.get_or_create(UserAccount=useraccount,UserID=useraccount.id)[0]
    except:
        useraccount = User.objects.get(username=username)
        userprofile=UserProfile.objects.get_or_create(UserAccount=useraccount,UserID=useraccount.id)[0]
    mag=Magazine.objects.get(MagazineID=1)
    userprofile.Favourites.add(mag)
    userprofile.save()
    
'''def mtm_category(name, magazines):
    
    category = Category.objects.filter(Name=name)
    
    for magid in magazines:
        print(magid)
        mag=Magazine.objects.get(MagazineID=magid)
        category.Mags.add(mag)
        mag.Categories.add(category)
        mag.save()
    category.save()
    return mag, category'''
   
 
if __name__ == '__main__':
    print('Starting wrkout population script...')
    populate()