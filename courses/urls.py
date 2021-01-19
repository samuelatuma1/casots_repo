from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url


app_name='courses'

urlpatterns = [
     
    # path('',views.home, name='home'),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('registration/',views.register, name='registration'),
    path('login/', views.login_view, name='login'),
    
    #new
    path('loginquiz/<slug:quiz>/', views.login_quiz, name='login_quiz'),

    path('logout/',views.logout_view, name='logout'),   
    path('allcourses/', views.courses_list, name='course_list' ),
    path('category/<slug:category_slug>/', views.courses_list, name='category_list_by_category'),
    path('contact-us/' ,views.contact_us, name='contact_us'),

 
    path('course/<slug:course_slug>/',views.course_summary, name = 'course_summary'),
    
    
    # reset password
    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name='courses/registration/password_reset.html'),
         name='reset_password'),
    
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name='courses/registration/password_reset_sent.html'),
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='courses/registration/password_reset_form.html'),
         name='password_reset_confirm'),
    
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='courses/registration/password_reset_done.html'),
         name='password_reset_complete'),
    
    
     # QUIZ SECTION
    path('quizinstructions/<str:category>/', views.quiz_instructions, name='quiz_instructions'),
 
     #trial
     path('quiz/<str:quiz>/',views.index, name='index'),

     path('quiz_performance/', views.quiz_performance, name='quiz_performance'),

      # Leadership board. For all test takers
    path('leaderboard/<str:quiz>/', views.leadership_board, name='leadership_board'),

   
    path('my_profile/', views.my_profile, name='my_profile'),


#     path('course/<str:category>/', views.course_main, name='course_main'),
     

     path('updateprofile/', views.updateprofile, name='updateprofile'),

     path('listest/', views.listest, name='listest'),
    
     
]
