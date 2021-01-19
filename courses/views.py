from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.urls import reverse
from courses.models import Courses,Category, UserProfile
from django.core.paginator import Paginator
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, UserLoginForm, ContactForm
from django.contrib.auth import login, authenticate , logout
from django.contrib import messages
from .models import QuizProfile, QuizQuestion,Quiz, Leadership_board
from django.http import Http404, HttpResponseRedirect
import datetime
from monthdelta import monthdelta
from django.core.mail import send_mail,BadHeaderError
from django.contrib.auth.decorators import login_required




#home page 

def home(request):
    context={}
    return render(request, 'courses/index.html',context)

# about page
def about(request):
    context={}
    return render(request, 'courses/about.html', context)

# all the courses page
def courses_list(request, category_slug=None):
    category =None
    courses = Courses.objects.all()
    if category_slug:
        category = Category.objects.get(slug = category_slug )
        courses =  courses.filter(category=category)
    paginator = Paginator(courses, 4)
    page_number=request.GET.get('page')
    courses = paginator.get_page(page_number)
    
    context = {'course':courses}
    return render(request, 'courses/course_list.html', context)


# summary of each course
def course_summary(request, course_slug):
    courses = Courses.objects.get(slug=course_slug)
    context = {'courses':courses}
    return render(request, 'courses/course_summary.html', context)

def contact_us(request):
    if request.method =='POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject="Website Inquiry"
            body={
                'first_name':form.cleaned_data['first_name'],
                'last_name':form.cleaned_data['last_name'],
                'email':form.cleaned_data['email_address'],
                'first_name':form.cleaned_data['message'],
            }
            message ="\n".join(body.values())
            try:
                send_mail(subject, message, 'umohu67@gmail.com', ['umohu67@gmail.com'])
            except BadHeaderError:
                return HttpResponse('invalid header found.')
            return redirect ("courses:home")
        
    form=ContactForm()
    context={'form':form}
    return render(request ,'courses/contact-us.html' , context )

# logout page
def logout_view(request):
    logout(request)
    return redirect("/login")

# register page
def register(request):
    form = RegistrationForm(request.POST)     
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('/courses')

    context = {'form': form}
    return render(request, 'courses/registration/sign_up.html', context=context)

# login page
def login_view(request):
    form =UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('/dashboard')
    return render(request, 'courses/registration/sign_in.html', {"form": form})

# QUIZ SECTION
# login page if user tries to access quiz without login
def login_quiz(request, quiz):
    form =UserLoginForm(request.POST or None)
    quiz = quiz
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)

        return HttpResponseRedirect(reverse('courses:quiz_instructions', args=[quiz]))
        #return HttpResponseRedirect(reverse('courses:course_summary', args=[quiz]))
    return render(request, 'courses/registration/sign_in.html', {"form": form})

def index(request, quiz):

    #If user not logged in
    if not request.user.is_authenticated:
        
        course = Courses.objects.filter(name=quiz).first()
        quizName = course.slug
        return HttpResponseRedirect(reverse('courses:login_quiz', args=[quizName]))

    if request.method == 'POST':
        
        #Login user as user
        user = request.user.username

        quizName = quiz
        
        get_questions = QuizQuestion.objects.filter(quiz__course__name=quizName).all()
       
        if len(get_questions)<= 0:
            return render(request, 'quizTest/error.html',{'error_msg':f"it is not your fault, it is ours. We couldn't find {quizName}"})
        
        try:
            recent = Leadership_board.objects.filter(user=user).filter(course=quizName).last()
            
            renew_access = recent.last_renewal + monthdelta(6)
            
            submission_date =datetime.date.today()
            
            get_time_difference =renew_access - submission_date
            
            time_left_before_renew = get_time_difference.days
            
            if time_left_before_renew>0:
                have_trials=False
                
                if recent.trials>100:
                    have_trials =False
                else:
                    have_trials =True
                    
            else:
                recent.last_renewal=submission_date
                recent.trials =0
                recent.save()
                have_trials = True
                
                
        except:
            have_trials = True
        
            
        if have_trials == True:
          
            get_questions = QuizQuestion.objects.filter(quiz__course__name =quizName).all()
            
            if len(get_questions)>0:
                questionSet=[]
                index = 0
                for question in get_questions:
                    
                    quest = question.question
                    
                    
                    
                    try:
                        
                        
                        questionSet.append({
                            'index': index,
                            'question':quest,
                            'A': question.A,
                            'B': question.B,
                            'C': question.C,
                            'D': question.D,
                            'answer': question.correct_answer,
                        })
                    except:
                        answer = 'None'
                        
                        questionSet.append({
                            'question':quest,
                            'A':'None',
                            'B':'None',
                            'C':'None',
                            'D':'None',
                            
                            'answer':answer
                        })

                    index += 1
                try:
                    course_name = Courses.objects.filter(slug=quizName).first()
                    
                    
                    course_category = course_name.category.name       
                    related_quiz = Quiz.objects.filter(course__category__name=course_category).all()
                    listit = list(related_quiz)
                except:
                    listit = []
                related_quizzes=[]
                
                for i in listit:
                    if i.course.slug == quizName:
                        pass
                    else:
                        related_quizzes.append(i.course.slug)
                        
                quiz_duration =Quiz.objects.filter(course__slug=quizName).first()
                
                try:
                    duration =quiz_duration.duration
                    time_denotation = quiz_duration.time_denotation
                    
                except:
                    duration =30
                    time_denotation ='min'
                    
                context={
                    'questionSet':questionSet,
                    'course':quizName,
                    'user': user,
                    'related_quizzes':related_quizzes,
                    'duration':duration,
                    'time_denotation': time_denotation,
                }
                return render(request, 'quizTest/quiz.html', context)
            else:
                if len(get_questions) <1:
                    return HttpResponse('Error no existing question')
        else:
            return render(request, 'quizTest/error.html',{'error_msg': f'You have used up your trials for {quizName}', 'extra_info': f'Course accessible from {renew_access}'})
                
    else:
        return render(request, 'quizTest/error.html', {'error_msg': f' Wrong turn, it seems you attempted to access this page from the wrong point'})





# def course_main(request, category):
#     category=str(category)
    
#     category =Category.objects.filter(name=category).all()
    
#     try:
#         course_category =category[0].name
#         related_courses =courses.objects.filter(category__name = course_category).all()
        
#         try:
#             listit =list(related_courses)
            
#             return render(request, 'quizTest/course.html',{'related_courses': listit})
#         except:
#             return HttpResponse('No course yet')
#     except:
#         return HttpResponse('Nothing here yet')



# function that handles quiz details.
def quiz_instructions(request, category):
    course = str(category)
    
    #quizName = Quiz.objects.filter(course__slug__icontains = course).all()
    quizName = Quiz.objects.filter(course__slug = course).all()
    
    context={
        'quizName':quizName
    }
    return render(request,'quizTest/quiz_details.html', context)

# def Leadership_board(request, quiz):
#     quizName = str(quiz)
    
#     course_name = Courses.objects.filter(name=quizName).first()
    
    
#     course_category = course_name.category.name
#     related_quiz = Quiz.objects.filter(course__category__name=course_category).all()
#     listit=list(related)

def quiz_performance(request):
    if request.method == 'POST':
        #Get all the passed in data
        score = request.POST['score']
        user = request.POST['user']
        course = request.POST['course']
        
        #new
        solutions = request.POST['alldetails']
        solution_set = eval(solutions)

        list_solution = []

        for solution in solution_set:
            new_solution = {
                'question': solution['question'],
                'answer': solution['answer'],
                'A': solution['A'],
                'B': solution['B'],
                'C': solution['C'],
                'D': solution['D'],
                'index': int(solution['index']),
                'chosenAnswer': solution['chosenAnswer']
            }

            list_solution.append(new_solution)


        

        ## VERSION 2 INCLUSION
        day = int(request.POST['day'])
        month = int(request.POST['month'])
        year = int(request.POST['year'])

        # Store performance in session
        request.session['user'] = user
        request.session['total'] = score
        request.session['course'] = course

        ###############################################################
            #If there is a table e.g Leaderboard, add data to table
            #This will be used for ranking performance, etc
            #This is commented out, because I didn't create such table
        ###############################################################

        ## VERSION 2 MODIFICATION
        ######################################################
        #Save user performance in leadership_board
        #Query for user performance in all courses too
        #Get and save date from javascript
        ######################################################

        
        
        #Create date from javascript input
        submission_date = datetime.date(year, month, day)

        ##VERSION 3 MODIFICATION
        ###Save last_renewal and trials field with "calculated" obtained result
        #################################################################################
        try:
            # Get the last performance from this particular user
            recent = Leadership_board.objects.filter(user=user).filter(course=course).last()

            #Get last renewal from recent, and determine when next access should be renewed
            renew_access = recent.last_renewal + monthdelta(6)  #Add 6 months to last_renewal to determine next renewal

            #Check if last_renewal is upto 6 months away from today
            get_time_difference = renew_access - submission_date

            #convert get_time_difference to integer
            time_left_before_renew = get_time_difference.days

            #If there is still time before next renewal
            if time_left_before_renew > 0:

                #Check if user has used up his trials
                if recent.trials > 1:

                    #If this is the case, add 1 to trials
                    # Do not change last renewal
                    new_performance = Leadership_board(user=user, course=course, score=int(score), date=submission_date, last_renewal=recent.last_renewal, trials=recent.trials+1)
                    new_performance.save()

                else:
                    #also if user haven't used up his trials still add to trials
                    new_performance = Leadership_board(user=user, course=course, score=int(score), date=submission_date, last_renewal=recent.last_renewal, trials=recent.trials+1)
                    new_performance.save()

            #If it is more than 6 months ago, set his trial to 0, and renew_date to the day of submission
            #This will hardly be the case because it will be taken care of in the quiz-index section, but for the sake of completeness, lets implement this
            else:
                new_performance = Leadership_board(user=user, course=course, score=int(score), date=submission_date, last_renewal=submission_date, trials=0)
                new_performance.save()

        except:
            new_performance = Leadership_board(user=user, course=course, score=int(score), date=submission_date, last_renewal=submission_date, trials=0)
            new_performance.save()

        #################################################################################

        ##END OF VERSION 3 ADDITION
        

        #Order the user's perfomance list from most recent to oldest
        user_performances = Leadership_board.objects.filter(user=request.session['user']).all().order_by('-pk')

    
        #Get users score, etc from session
        context = {
            'user': request.session['user'],
            'course': request.session['course'],
            'score':  request.session['total'],
            'submission_date': submission_date,
            ##VERSION 2 MODIFICATION
            'user_performances': user_performances,
            'list_solution': list_solution
        }

        return render(request, 'quizTest/performance.html', context)

    #Order the user's performance list from most recent to oldest
    user_performances = Leadership_board.objects.filter(user=request.session['user']).all().order_by('-pk')

    return render(request, 'quizTest/performance.html', {'user_performances': user_performances,
                                                        'list_solution': list_solution
                                                            })
    
    #return render(request, 'quizTest/quiz_performance.html', {'user_performances': user_performances})

### Leadership_board shows the ranked performance For all test takers for a particular course
def leadership_board(request, quiz):
    #Assuming you have a course called quiz
    quizName = str(quiz)

    # This attempts to populate say nav bar with other courses in the same category
    # Get the course name
    course_name = Courses.objects.filter(slug=quizName).first()

    # Get the category the course falls under 
    course_category = course_name.category.name

    # Get other quiz that falls under the same category
    related_quiz = Quiz.objects.filter(course__category__name=course_category).all()
    # Convert querySet to a more easily iterable list
    listit = list(related_quiz)

    #Get other quizes from the same category apart from the current quiz
    related_quizzes = []

    for i in listit:
        #If it is the current quiz, ignore
        if i.course.slug == quizName:
            pass
        #Else if it is not the current quiz, add to related_quizes
        else:
            related_quizzes.append(i.course.slug)

        #Pass in the related_quizzes in context


        ###########################################################################
        #################################################################################
    ## Rank score performance in a descending order
    ranked_performance = Leadership_board.objects.all().filter(course=course_name.name).order_by('-score')

    return render(request, 'quizTest/ranked_performance.html', {'user_performances': ranked_performance, 'related_quizzes': related_quizzes})    



#New

from django import forms
class ProfileImage(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_image',)

def my_profile(request):
    if request.user.is_authenticated:
        user = request.user
        data_for_performance = Leadership_board.objects.filter(user=user).all()
        user_performances = data_for_performance.order_by('-pk')
        
        
        return render(request, 'aboutUser/userprofile.html', 
                        {"user": request.user, 'user_performances': user_performances,
                                'imageForm': ProfileImage })
    
    else:
        return HttpResponseRedirect(reverse('courses:login'))


def updateprofile(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            profile = UserProfile.objects.filter(user__username = request.user.username).first()
            to_change  = request.POST['tochange']
            
            change_image = to_change == 'image'
            change_institution = to_change == 'institution'
            change_bio = to_change == 'bio'

            if change_image:
                new_profile_image = ProfileImage(request.POST, request.FILES)

                if new_profile_image.is_valid():
                    profile.profile_image = new_profile_image.cleaned_data['profile_image']
                    profile.save()

                

            elif change_institution:
                new_institution = request.POST['changeinstitution']
                valid_institution = len(new_institution) > 1

                if valid_institution:
                    profile.institution = new_institution
                    profile.save()
                
            elif change_bio:
                new_bio = request.POST["changebio"]
                valid_bio = len(new_bio) > 1

                if valid_bio:
                    profile.bio = new_bio
                    profile.save()

            return HttpResponseRedirect(reverse('courses:my_profile'))

        else:
            return HttpResponseRedirect(reverse('courses:my_profile'))
    else:
        return HttpResponseRedirect(reverse('courses:login'))

def listest(request):
    if request.method == 'POST':
        dictionary = request.POST['dictionary']
        listit = eval(dictionary)
        #return HttpResponse(f'{listit}')
        names = ''
        for dic in listit:
            names += f"{dic['n']}, "
        return HttpResponse(f"{names}")
    else:
        return render(request, 'listest.html')