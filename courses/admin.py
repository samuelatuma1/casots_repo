from django.contrib import admin
from courses.models import *



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug':('name',)}
    
    
@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display=['name','slug']
    prepopulated_fields={'slug':('name',)}

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['bio', 'institution', 'user']
    raw_id_fields = ['user']
    list_filter = ['institution']
    search_fields = ['user', 'bio']
    
# Register your models here.
admin.site.register(Quiz)
admin.site.register(QuizProfile)
admin.site.register(Leadership_board)
admin.site.register(QuestionChoice)
admin.site.register(QuizQuestion)

