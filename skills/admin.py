from django.contrib import admin
from .models import Skill, Category, SkillDeal, Review

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(Skill)
admin.site.register(SkillDeal)
admin.site.register(Review)
