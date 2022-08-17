from django.contrib import admin

from magportal.models import UserProfile, Magazine, Category

class MagazineAdmin(admin.ModelAdmin):
    list_display=("MagazineID", "Name", "Description", "Date", "URL", "Discount")
    
class CategoryAdmin(admin.ModelAdmin):
    list_display=("CategoryID", "Name")
    
    
admin.site.register(Magazine, MagazineAdmin)
admin.site.register(Category, CategoryAdmin)