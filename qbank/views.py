from unicodedata import category
from django.shortcuts import render
from qbank.forms import ImportForm, ProfileForm,SignUpForm,DeleteForm
from PyPDF2 import PdfReader
from django.views.generic import CreateView, UpdateView
import re
import io
import os
from .models import Category, ExamHeader,ExamQuestion, Profile, Project,Dashboard,Img
from pikepdf import Pdf, PdfImage
from datetime import date
from django.conf import settings
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy

from collections import ChainMap
from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

import pyrebase
# Create your views here.

config={
    "apiKey": "AIzaSyCkcfb7JXcFpGQXZM3mZC6BmJ789kLswkw",
    "authDomain": "fireled-95b8f.firebaseapp.com",
    "databaseURL": "https://fireled-95b8f.firebaseio.com",
    "projectId": "fireled-95b8f",
    "storageBucket": "fireled-95b8f.appspot.com",
    "messagingSenderId": "563718754845",
    "appId": "1:563718754845:web:de4f59dc232a5d4c4aacf4"

}

firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'login.html'

def build_menu ():
    courses = ExamHeader.objects.all().order_by('category_ref', 'name')
    course_list = []
    menu_items = []
    prev_category =''
    category = {}
    for course in courses:
        if course.category_ref is not None:
            curr_category = course.category_ref.category_name
            
        else: 
            curr_category = 'Other'

        course_list.append({ "course_id" :  course.exam_id, "course_name" :course.name, "course_slug" : course.slug})

        
        if ( prev_category != curr_category and prev_category !='' ) : 
            category['category_name'] = prev_category
            category['course_list'] = course_list
            menu_items.append(category)
            course_list = []
            category = {}
        print("Curr cat",curr_category)
        prev_category = curr_category
        
    
    if len(courses) > 0 :
        category['category_name'] = prev_category
        category['course_list'] = course_list
        menu_items.append(category)

    return menu_items

# Create your views here.
def login(request):
   menu_items = build_menu ()
   print (menu_items)
   course = ExamHeader.objects.all()[:3]
   return render(request, 'login.html', {"segment" :"login","base_url" :settings.BASE_URL, "courses" : menu_items,"course_list" : course })
  
def home_view(request):
    menu_items = build_menu ()
    course = ExamHeader.objects.all()[::-1]

    context = {"segment" :"index","base_url" :settings.BASE_URL, "courses" : menu_items, "course_list" : course[:3]}
    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
        context['image'] = "/static" + imgurl[0]

    # print("Courses:", course)
    return render(request, "home.html", context)
    
def courses_view(request):
    menu_items = build_menu ()
    print("Menu items:",menu_items)
    course = ExamHeader.objects.all()
    courses = ExamHeader.objects.all().order_by('category_ref', 'name')
    course_list = []
    menu_items1 = []
    prev_category =''
    category = {}
    category2 = {}
    catlist = []

    context = {"segment" :"courses.html","base_url" :settings.BASE_URL, "course_list" : course}
    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
        context['image'] = "/static" + imgurl[0]

    for course1 in courses:
        if course1.category_ref is not None:
            curr_category = course1.category_ref.category_name

            if curr_category not in menu_items1:
                course_list = []
                category = {}
                catlist.append(curr_category)
                
                course_list.append({ "course_id" :  course1.exam_id, "course_name" :course1.name, "course_slug" : course1.slug})
                # if prev_category != curr_category:
                category['category_name'] = curr_category
                category['course_list'] = course_list
                menu_items1.append(category)
                prev_category = curr_category
                
                
            # if prev_category == curr_category:
            #     # category['category_name'] = prev_category
            #     category['course_list'] = course_list
            #     menu_items1.append(category)
        else: 
            curr_category = 'Other'

    # vvv =  ExamHeader.objects.filter(category_ref='Amazon')
    # print("Menu:",menu_items1)

        
    # print("Categories:",courses)
    # print("Catlist:",catlist)
    men = []
    pcat = ''
    clist = []
    cat = {}

    # for i in range(len()+1)
    for course in menu_items1:
        # print("Course list:",ChainMap(course['course_list']))
        
        # for i,j in course.items():
        #     print("Course item:",i['category_name'],j)
        if pcat != course['category_name']:
            print("Course list:",course['course_list'][0])
            men.append(cat)
            cat = {}
            cat['category_name'] = course['category_name']
            cat['course_list'] = course['course_list']
            
            # print("J is:",course['course_list'])
        if pcat == course['category_name']:
            cat['course_list'].append(course['course_list'][0])
            # print("Same")
        pcat = course['category_name']
        # print("Course is:",course1.category_ref.category_name)
        # course_list.append({ "course_id" :  course1.exam_id, "course_name" :course1.name, "course_slug" : course1.slug})
    
    men.append(cat)
    cat = {}
    print("Men:",men)
    men.pop(0)
    print("Men:",men)

    # if ( prev_category != curr_category and prev_category !='' ) : 
    #         category['category_name'] = prev_category
    #         category['course_list'] = course_list
    #         menu_items1.append(category)
    #         course_list = []
    #         category = {}
    
    # print("Course list",course_list)
    # if len(courses) > 0 :
    #     category['category_name'] = prev_category
    #     category['course_list'] = course_list
    #     menu_items1.append(category)
    
    # print("Course list is:",menu_items1)


    #projects = Project.objects.filter(auth_user_id=request.user.id).all()[:3]
    # print("Menu items:", menu_items)
    # print("Courses:", courses)
    context['courses'] = men
    return render(request, "courses.html", context)
    

def certificate_view(request, slug=""):
    course = ExamHeader.objects.filter(slug=slug).all().first()
    profile = Profile.objects.filter(auth_user_id=request.user.id).all().first()
    duration = settings.DEFAULT_FREE_QUUESTION_DURATION
    
    if request.user.is_authenticated and course.duration_m is not None : 
        duration = course.duration_m
    user_name = profile.first_name + " " +profile.first_name
    today = date.today()
    # print(today)
    # menu_items = build_menu ()
    return render(request, "certificate.html", {"base_url" :settings.BASE_URL, "course_title" : course.name, "course_duration" : duration, "user_name" : user_name, "today" : today})

def profile_view(request):
    menu_items = build_menu ()
    context = {"segment" :"profile","base_url" :settings.BASE_URL, 
    "courses" : menu_items}
    profile = Profile.objects.filter(auth_user_id=request.user.id).all().first()
    profile11 = Profile.objects.filter(auth_user_id=request.user.id)
    # profile11.delete()

    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
    # img = Img.objects.all()
    # img = Img.objects.filter(filetitle=request.user.id)
        print("IMG:","/static" + imgurl[0])
        context['image'] = "/static" + imgurl[0]

    print("Profile11:",profile11)
    # for i in profile11:
    #     print("IIII",i.first_name)
    projects = Project.objects.filter(auth_user_id=request.user.id).all()
    context['projects'] = projects
    print (request.user.id)
    if profile is not None:
        form = ProfileForm(instance=profile)
    else:
        form = ProfileForm()

    message = ""
    if request.method == "POST":
        print ("First name is:",request.POST.get('first_name',''))

        phone = ''
        bachelor_degree = ''
        bachelor_yop = 0
        master_degree = ''
        master_yop = 0
        specialization = ''
        first_name = ''
        last_name = ''
        
        file = request.FILES.get('imgfile')
        # print("FIle is",file)
        phone = request.POST.get('phone')
        bachelor_degree = request.POST.get('bachelor_degree')
        if request.POST.get('bachelor_yop') != 'Select':
            bachelor_yop = request.POST.get('bachelor_yop')
            print("Bacholor:",bachelor_yop)
        master_degree = request.POST.get('master_degree')
        if request.POST.get('bachelor_yop') != 'Select':
            master_yop = request.POST.get('master_yop')
        specialization = request.POST.get('specialization')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # newprofile = Profile(first_name=request.POST.get('first_name'), auth_user_id=request.user.id)
        # newprofile.save()
        
        if file is not None:
            if image:
                image.delete()
                fileadd = Img.objects.create(filetitle=request.user.id,file=file)
                fileadd.save()
            else:
                fileadd = Img.objects.create(filetitle=request.user.id,file=file)
                fileadd.save()

        if profile is not None:
            Profile.objects.update(first_name=first_name, auth_user_id=request.user.id, phone=phone,
                bachelor_degree=bachelor_degree, bachelor_yop=bachelor_yop,master_degree=master_degree,
                master_yop=master_yop,specialization=specialization,last_name=last_name)
            
            form = ProfileForm(request.POST,instance=profile)            
        else:
            newprofile = Profile(first_name=first_name, auth_user_id=request.user.id, phone=phone,
                bachelor_degree=bachelor_degree, bachelor_yop=bachelor_yop,master_degree=master_degree,
                master_yop=master_yop,specialization=specialization,last_name=last_name)
            newprofile.save()
            form = ProfileForm(request.POST)
        if form.is_valid():
            print ("First name is:",request.POST.get('first_name'))
            if request.POST.get('project_title') != '' : 
                project = Project (project_title = request.POST.get('project_title'), auth_user_id =
                request.POST.get('auth_user_id'), duration = request.POST.get('duration'), 
                tech_stack = request.POST.get('tech_stack'), 
                project_description = request.POST.get('project_description'))
                project.save()
            
            form.save()
            message = "Saved Successfully !"
            context['message'] = message
            # profile_info = form.save(commit=False)
            # profile_info.auth_user_id = request.user
            # profile_info.save()
    context['form'] = form
    return render(request, "user_profile.html", context)

def login_view(request):
    menu_items = build_menu ()
    course = ExamHeader.objects.all()[:3]
    return render(request, "login.html", {"base_url" :settings.BASE_URL, "courses" : menu_items,"course_list" : course  })

def dashboard_view(request):
    menu_items = build_menu ()
    dashboards = Dashboard.objects.filter(auth_user_id=request.user.id).all().order_by('date')
    context = {"segment" :"dashboard","base_url" :settings.BASE_URL, "courses" : menu_items,
    "dashboards" : dashboards[::-1][:5]
      }

    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
    # img = Img.objects.all()
    # img = Img.objects.filter(filetitle=request.user.id)
        print("IMG:","/static" + imgurl[0])
        context['image'] = "/static" + imgurl[0]

    # today = date.today()
    # is_pass = 'no'
    # if (total_correct > course.pass_score):
    #     is_pass = 'yes'
    # print("Dashboard",dashboards[::-1])
    return render(request, "dashboard.html", context)

def catalogue_view(request):
    menu_items = build_menu ()
    return render(request, "catalogue.html", {"segment" :"catalogue","base_url" :settings.BASE_URL, "courses" : menu_items })
    


# def exampreview_view(request):
#     menu_items = build_menu ()
#     courses = ExamHeader.objects.filter
   
#     return render(request, "exam_preview.html", {"base_url" :settings.BASE_URL, "courses" : menu_items })
    
def exampreview_view(request, slug=""):
    menu_items = build_menu ()

    context = {"base_url" :settings.BASE_URL, "courses" : menu_items , "topic1" : "my_top1list"}
    

    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
        context['image'] = "/static" + imgurl[0]


    # print("Slug is:",slug)
    course = ExamHeader.objects.filter(slug=slug).all().first()
    context['course_title'] = course.name
    context['keywords'] = course.keywords
    context['course_slug'] = course.slug
    context['course_pass_score'] = course.pass_score
    
    # desctxt11 = ''
    # introtxt = ''
    lstwords = course.desc.split('$$$')
    context['topic2'] = lstwords[1]
    context['coursetime'] = lstwords[2]
    context['course_desc'] = lstwords[0]

    print("Lstwords:",lstwords)
    
    duration = settings.DEFAULT_FREE_QUUESTION_DURATION
    
    if request.user.is_authenticated and course.duration_m is not None : 
        duration = course.duration_m

    context['course_duration'] = duration
    return render(request, "exam_preview.html", context)
    # return render(request, "exam_preview.html", {"base_url" :settings.BASE_URL, "courses" : menu_items , "course_title" : course.name, "course_keywords" : course.keywords,"course_slug" : course.slug, "course_duration" : duration, "course_pass_score" : course.pass_score })



def exam_view(request, slug=""):
    menu_items = build_menu ()
    
    context = {"base_url" :settings.BASE_URL, "courses" : menu_items}

    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
        context['image'] = "/static" + imgurl[0]

    # print("Slug is:",slug)
    # print (question_num)
    
    course = ExamHeader.objects.filter(slug=slug).all().first()
    context['course'] = course
    questions = ExamQuestion.objects.filter(exam_ref=course).all().order_by('question_num')

    # print (len(questions))

    # duration = settings.DEFAULT_FREE_QUUESTION_DURATION
    duration = 10

    max_question = request.GET.get('max_question', 10)
    # question_num =settings.DEFAULT_FREE_QUUESTION
    context['total_question'] = max_question
    du = request.GET.get('duration')
    if du != None:
        duration = du
    print("Duration is:",du)
    context['duration'] = duration
    # if request.user.is_authenticated and course.duration_m is not None : 
    #     duration = course.duration_m

    # print("Questions Are:",questions[question_num-1].question_num)
    # print (question_num+1)
    # print(question_num-1)
    #return render(request, "exam.html", {"base_url" :settings.BASE_URL, "courses" : menu_items, "course_title" : course.name, "question_dtls" : questions[question_num], "total_question" : len(questions), "current_date" : course.date, "next_question" : question_num+1, "previous_question" : question_num-1, "course_slug" : course.slug})
    return render(request, "exam.html", context)

def exam_question (request, slug="", question_num=1):
    
    course = ExamHeader.objects.filter(slug=slug).all().first()
    questions = ExamQuestion.objects.filter(exam_ref=course).all().order_by ('question_num')

    if not request.user.is_authenticated and question_num > settings.DEFAULT_FREE_QUUESTION :
        question_num =settings.DEFAULT_FREE_QUUESTION

    if not request.user.is_authenticated :
        max_question = settings.DEFAULT_FREE_QUUESTION
    else:
        request.session['max_question'] = int(request.GET.get('max_question', len(questions)))
        max_question = int(request.GET.get('max_question', len(questions)))
        #max_question = len(questions)

    print ("Max Question : " + str(max_question))

    if request.GET.get('is_next') == 'true' :
        print (request.GET.get('user_answer_'+str(course.exam_id)+'_'+str((question_num-1))))
        request.session['user_answer_'+str(course.exam_id)+'_'+str((question_num-1))] = request.GET.get('user_answer_'+str(course.exam_id)+'_'+str((question_num-1)))

    option_a ='false'
    option_b ='false'
    option_c ='false'
    option_d ='false'
    
    if 'user_answer_'+str(course.exam_id)+'_'+str((question_num)) in request.session and request.session['user_answer_'+str(course.exam_id)+'_'+str((question_num))] is not None:
        options = request.session['user_answer_'+str(course.exam_id)+'_'+str((question_num))].split(",")
        option_a = options[0].split("~")[1]
        option_b = options[1].split("~")[1]
        option_c = options[2].split("~")[1]
        option_d = options[3].split("~")[1]

    img_file = str(settings.BASE_DIR) + '/media/exam/inline-img-exam'+str(course.exam_id)+'-page'+str(question_num+1)+'-img0.png'
    # print (img_file )

    if os.path.exists(img_file) :
        img_file_exists = 'yes'
    else: 
        img_file_exists = 'no'
  
    # print (len(questions))

    # print (questions[question_num+1])
    # print (question_num+1)
    # print(question_num-1)
    #return render(request, "exam.html", {"base_url" :settings.BASE_URL, "courses" : menu_items, "course_title" : course.name, "question_dtls" : questions[question_num], "total_question" : len(questions), "current_date" : course.date, "next_question" : question_num+1, "previous_question" : question_num-1, "course_slug" : course.slug})
    return render(request, "exam_question.html", {"base_url" :settings.BASE_URL, 
    "question_dtls" : questions[question_num-1], 
    "max_question" : max_question,
    "course_slug" : course.slug, "course_id" : course.exam_id,
    'img_exists' : img_file_exists,
    'option_a' : option_a, 'option_b' : option_b, 'option_c' : option_c,
    'option_d' : option_d
})


def evaluate_exam(request,slug="", last_question=1):
    menu_items = build_menu ()
    course = ExamHeader.objects.filter(slug=slug).all().first()

    questions = ExamQuestion.objects.filter(exam_ref=course).all().order_by ('question_num')

    if request.GET.get('user_answer_'+str(course.exam_id)+'_'+str((last_question))) is not None : 
        request.session['user_answer_'+str(course.exam_id)+'_'+str((last_question))] = request.GET.get('user_answer_'+str(course.exam_id)+'_'+str((last_question)))

    if not request.user.is_authenticated:
        MAX_QUESTION =settings.DEFAULT_FREE_QUUESTION
    else: 
        # MAX_QUESTION = len(questions)
        #MAX_QUESTION = int(request.GET.get('max_question', len(questions)))
        MAX_QUESTION  = request.session['max_question']
    ## ?? to be removed 
    #MAX_QUESTION =settings.DEFAULT_FREE_QUUESTION

    eval_question_list = []
    total_correct = 0
    
    for index, question in enumerate(questions):
        if (index+1) > MAX_QUESTION: break

        question_evaluation = {}

        question_evaluation ["question_dtl"] = question 
        
        multi_selection = False
        user_selection = ""
        if 'user_answer_'+str(course.exam_id)+'_'+str(question.question_num) in request.session :
            user_selected_val = request.session.get('user_answer_'+str(course.exam_id)+'_'+str(question.question_num), '')
            #print (user_selected_val)

            if user_selected_val is not None:
                user_choices = user_selected_val.split(",")
                #print (user_choices)
                if  user_choices[0].split("~")[1] == 'true' : 
                    user_selection ='A'
                    multi_selection = True
                if  user_choices[1].split("~")[1] == 'true' : 
                    if multi_selection : user_selection +=',B'
                    else: user_selection ='B'
                    multi_selection = True
                if  user_choices[2].split("~")[1] == 'true' : 
                    if multi_selection : user_selection +=',C'
                    else: user_selection ='C'
                    multi_selection = True
                if  user_choices[3].split("~")[1] == 'true' : 
                    if multi_selection : user_selection +=',D'
                    else: user_selection ='D'
                    multi_selection = True

        # print ("User selection : " + user_selection + ", correct answer : " + question.answer )

        is_answer_correct = 'false'
        if question.answer == user_selection : 
            is_answer_correct='true'
            total_correct = total_correct +1

        question_evaluation ["user_selection"] = user_selection
        question_evaluation ["is_answer_correct"] = is_answer_correct 


        eval_question_list.append(question_evaluation)

    is_pass = 'no'
    print("total correct:",total_correct)
    print("course pass score:",course.pass_score)
    if (total_correct > course.pass_score):
        is_pass = 'yes'

    if request.GET.get('user_answer_'+str(course.exam_id)+'_'+str((last_question))) is not None and request.user.is_authenticated: 
        dashboard = Dashboard(auth_user_id=request.user.id,course_id=course, score_taken =total_correct,date = date.today() )
        dashboard.save()

    p = Paginator(eval_question_list, 1)  # creating a paginator object
    # getting the desired page number from url
    page_number = request.GET.get('page')
    try:
        question_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        question_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        question_obj = p.page(p.num_pages)

    #context = {'page_obj': page_obj}

    # print (question_obj.object_list)

    return render(request, "eval_report.html", {"base_url" :settings.BASE_URL,"course_name" :course.name,
    "courses" : menu_items ,"course_slug" :course.slug,
     'evaluation_report' : {"total_correct" :total_correct, "total_question" : MAX_QUESTION, 'is_pass' : is_pass,
     "questions" :  eval_question_list, 'question_obj': question_obj} 
    })
    
def reset_exam(request,slug=""):
    # print("Reset exam is on")
    course = ExamHeader.objects.filter(slug=slug).all().first()
    questions = ExamQuestion.objects.filter(exam_ref=course).all().order_by ('question_num')

    if not request.user.is_authenticated : 
        MAX_QUESTION =settings.DEFAULT_FREE_QUUESTION
    else: 
        MAX_QUESTION = len(questions)
    ## ?? to be removed 
    MAX_QUESTION =settings.DEFAULT_FREE_QUUESTION

    for index, question in enumerate(questions):
        if (index+1) > MAX_QUESTION: break
        if 'user_answer_'+str(course.exam_id)+'_'+str(question.question_num) in request.session : 
            del request.session['user_answer_'+str(course.exam_id)+'_'+str(question.question_num)]
    
    return JsonResponse({'is_cleared':'cleared'})

edit1 = ""
edit2 = ""
edit3 = ""

@csrf_exempt
def editor(request):
    if request.method == 'POST':
        usr = request.POST['etxt']
        usr1 = request.POST['etxt1']
        usr2 = request.POST['etxt2']
        global edit1
        global edit2
        global edit3
        edit1 = usr
        edit2 = usr1
        edit3 = usr2
        # choicesgender = usr.dict()['choices-gender']
        # choicesmonth = usr.dict()['choices-month']
        # choicesday = usr.dict()['choices-day']
        # choicesyear = usr.dict()['choices-year']
        
        
        
        return HttpResponse("Success")
        # return JsonResponse({}, status = 400)
        # return redirect('/userform.html')

# Exam Time: 60 mins | Publish Date: 3 Apr 2021
def pdf_upload(request):
    context = {}

    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
        context['image'] = "/static" + imgurl[0]

    # print("Edit1 is:",edit1)
    def _parse_line(line):
        for key, rx in rx_dict.items():
            match = rx.search(line)
            if match:
                return key, match
        # if there are no matches
        return None, None

    if request.method == 'POST' : 
        
        # edittxt = request.POST['etxt']
        # print("Category ID is:",edittxt)

        form = ImportForm(request.POST or None)
        file = request.FILES['pdf_file']
        catid = request.POST['valves']
        print("Cat id:",catid,type(catid))

        catref = Category.objects.filter(category_id=int(catid)).first()
        print("Catref name:",catref)

        pass_score = request.POST['pass_score']
        print("Pass Score is:",pass_score)

        keyword = request.POST['keyword']
        print("keyword is:",keyword)

        coursename = request.POST['coursename']
        print("coursename is:",coursename)

        slug = coursename.replace(" ", "_") + ".html"
        # keywords = coursename.replace(" ", ",")
        keywords = keyword

        # catref = Category.objects.filter(category_id=catid).first()
        
        
        # print("Files:",file)
        rx_dict = {
        'intro': re.compile(r'Introduction:'),
        'table': re.compile(r'T\.'),
        'question_num': re.compile(r'QUESTION NO: (\d*)'),
        'A': re.compile(r'A\.'),
        'B': re.compile(r'B\.'),
        'C': re.compile(r'C\.'),
        'D': re.compile(r'D\.'),
        'E': re.compile(r'E\.'),
        'F': re.compile(r'F\.'),
        'answer': re.compile(r'Answer: (.*)'),
        'explanation': re.compile(r'Explanation:'),
        'reference': re.compile(r'Reference:(.*)'), 
        'page_num': re.compile(r'www.actualtests.com\s+(\d*)'), 
        }
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() +"\n"
        #print (text)
        text = text.replace("\"Pass Any Exam. Any Time.\"", "")
        #text = text.replace("www.actualtests.com", "")
        
        print ( "First Line : " + text.split('\n', 1)[0] ) 
        text = text.replace(text.split('\n', 1)[0] + " Exam", "")

        buffer = text.split ("\n")
        question =""
        A_option =""
        B_option =""
        C_option =""
        D_option =""
        E_option =""
        F_option =""
        answer =""
        reference = ""
        explanation =""
        is_question_on = False
        is_Aoption_on = False
        is_Boption_on = False
        is_Coption_on = False
        is_Doption_on = False
        is_Eoption_on = False
        is_Foption_on = False
        is_answer_on = False
        is_skip_off = True
        prev_question_num =""
        curr_question_num =""
        line_count = 0
        page_num = 0
        exam_header=None

        


        # lst = []
        # lcount1=[]
        # lcount2 = []

        # r = reader.getPage(1)
        # intropage = reader.getPage(2)
        # # print("Page 2 is:",r.extract_text())
        # descline = []
        # desctxt = ""
        # introtxt = ""
        # for line in io.StringIO(r.extract_text()):
        #     print(line.strip('\n'))
        #     r = line.strip('\n')
        #     if r == " ":
        #         continue
        #     else:
        #         desctxt += line.strip('\n') + ","
        #         descline.append(line.strip('\n'))

        # for line in io.StringIO(intropage.extract_text()):
        #     print(line.strip('\n'))
        #     r = line.strip('\n')
        #     if r == " ":
        #         continue
        #     else:
        #         introtxt += line.strip('\n') + ","
        #         # descline.append(line.strip('\n'))

        # print("Introtxt is:",introtxt)
        # print("Desctxt is:",desctxt)intro = introtxt,


        for line in buffer:
            # lst.append(line)
            key, match = _parse_line(line)
            line_count+=1
            if (line_count == 4):

                exam_header =ExamHeader(category_ref = catref ,name= coursename,  desc = edit1 + '$$$' + edit2 + '$$$' + edit3, slug = slug, keywords=keywords,pass_score=pass_score)
                exam_header.save()
                exam_id = exam_header.exam_id
                print ( "Exam ID " + str(exam_id))

                # slug = coursename.replace(" ", "_") + ".html"
                # keywords = coursename.replace(" ", ",")

                # # catref = Category.objects.filter(category_id=catid).first()
                # exam_header =ExamHeader(category_ref = catref ,name= coursename,  desc = edit1 + '$$$' + edit2 + '$$$' + edit3, slug = slug, keywords=keywords,pass_score=pass_score)
                # exam_header.save()
                # exam_id = exam_header.exam_id
                # print ( "Exam ID " + str(exam_id))
                # print ( "Exam head catref:" + exam_header.category_ref)

            # if key == 'table':
            #     lcount1.append(line_count)
            # # #     print("line count is:",line_count)
            # # #     for 
            # #     # lst.append(line)

            # #     # print("Lines are:",i)
            #     t = match.group(1)
            #     print("table is",t)
            #     if key == 'question_num':
            #         break
            # print("lst is:",lst)

            # if key == 'intro':
            #     print("Intro is:",match)


            if key == 'question_num':
                # lcount2.append(line_count)
                # catref = ExamHeader.objects.filter(category_id=int(catid)).first()
                # print("Exam Header is:",exam_header.category_ref)
                is_question_on = True
                curr_question_num = match.group(1)
                if  prev_question_num != '' and curr_question_num != prev_question_num : 
                    exam_question = ExamQuestion(question=question.strip(), option_a =A_option.strip(), 
                     option_b =B_option.strip(), option_c =C_option.strip(), option_d =D_option.strip(),option_e =E_option.strip(), 
                     option_f =F_option.strip(),answer =answer.strip(),referrence =reference.strip(), explanation = explanation.strip(), 
                     exam_ref =  exam_header, question_num=prev_question_num, page_num=page_num)
                    exam_question.save()
                    # print ( "\n\n" + "Question Number : "+ str(prev_question_num) + " : " + question + "\n\n")
                    # print ( "" +A_option )
                    # print ( "" +B_option )
                    # print ( "" +C_option )
                    # print ( "" +D_option )
                    # print ( "" +E_option )
                    # print ( " " +F_option )
                    # print ( "Answer " +answer )
                    # print ( "Reference " +reference )
                    is_Aoption_on = False
                    is_Boption_on = False
                    is_Coption_on = False
                    is_Doption_on = False
                    is_Eoption_on = False
                    is_Foption_on = False
                    question =""
                    A_option =""
                    B_option =""
                    C_option =""
                    D_option =""
                    E_option =""
                    F_option =""
                    reference =""
                    explanation =""
                prev_question_num = match.group(1)
            elif key == 'A':
                is_question_on = False
                is_Aoption_on = True
                is_Boption_on = False
            elif key == 'B':
                is_Aoption_on = False
                is_Boption_on = True
            elif key == 'C':
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = True
            elif key == 'D':
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = False
                is_Doption_on = True
            elif key == 'E':
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = False
                is_Doption_on = False
                is_Eoption_on = True
            elif key == 'F':
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = False
                is_Doption_on = False
                is_Eoption_on = False
                is_Foption_on = True
            elif key == 'answer':
                answer = match.group(1)
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = False
                is_Doption_on = False
                is_Eoption_on = False
                is_Foption_on = False
            elif key == 'reference':
                reference = match.group(1)
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = False
                is_Doption_on = False
                is_Eoption_on = False
                is_Foption_on = False
            elif key == 'page_num':
                page_num = match.group(1)
                is_skip_off = False
                
                
            if (is_skip_off and is_question_on and key!= 'question_num'): question+=line + "\n"
            elif (is_skip_off and is_Aoption_on and key!= 'A'): A_option+=line + "\n"
            elif (is_skip_off and is_Boption_on and key!= 'B'): B_option+=line + "\n"
            elif (is_skip_off and is_Coption_on and key!= 'C'): C_option+=line + "\n"
            elif (is_skip_off and is_Doption_on and key!= 'D'): D_option+=line + "\n"
            elif (is_skip_off and is_Eoption_on and key!= 'E'): E_option+=line + "\n"
            elif (is_skip_off and is_Foption_on and key!= 'F'): F_option+=line + "\n"

            is_skip_off = True
        # key1, match1 = _parse_line(line)
        # for line in buffer:
        #     lst.append(line)
        #     if key1 == 'table':
        #         break
        # print ("line count1 is:",lcount1[0])
        # print ("line count2 is:",lcount2[0])

        # r = reader.getPage(1)
        # # print("Page 2 is:",r.extract_text())
        # descline = []
        # for line in io.StringIO(r.extract_text()):
        #     print(line.strip('\n'))
        #     r = line.strip('\n')
        #     if r == " ":
        #         continue
        #     else:
        #         descline.append(line.strip('\n'))
            # if line == '':
            #     continue
            # else:
            #     descline.append(str(line))
            # print("IO line is:",line)
        # print("descline is:",descline)
        # for i in r.extract_text():
        #     print(i)
        # for line[6-39] in buffer:
        #     print("lines are:",)

        # last question 
        exam_question = ExamQuestion(question=question.strip(), option_a =A_option.strip(), 
                     option_b =B_option.strip(), option_c =C_option.strip(), option_d =D_option.strip(),option_e =E_option.strip(), 
                     option_f =F_option.strip(),answer =answer.strip(),referrence =reference.strip(), explanation = explanation.strip(), 
                     exam_ref =  exam_header, question_num=curr_question_num, page_num=page_num)
        exam_question.save()

        filename = 'inline-img'
        example = Pdf.open(file)

        for i, page in enumerate(example.pages):
            for j, (name, raw_image) in enumerate(page.images.items()):
                image = PdfImage(raw_image)
                out = image.extract_to(fileprefix=f"media/exam/{filename}-exam{exam_id}-page{(i+1)}-img{j}")
            # text = text.replace("\n", "")
        # text = text.replace("\r", "")
        # text = text.replace("\s", "")
        # text = text.replace("\t", "")
        #print (text)
        #q_patten = 'QUESTION NO: (\d*)'
        #q_list = re.compile(q_patten, re.MULTILINE).findall(text)
        #print (q_list)

        #q_patten = 'QUESTION NO: (.*)[?:\n\s\r]+(.*[\r\n\s].*[\r\n\s].*[\r\n\s].*[\r\n\s].*[\r\n\s].*[\r\n\s].*[\r\n\s].*?)'
        #q_patten = 'QUESTION NO: (.*)[?:\n\s\r]+()'


        #q_patten = 'QUESTION NO: (\d*)(.*)'
        #q_list = re.compile(q_patten, re.MULTILINE).findall(text)
        #print (q_list)


        #print ( re.findall( r'^QUESTION NO:(.*)QUESTION((?:\n.+)+)', text, re.MULTILINE) )
        #print (file.read())

        #file_data = file.read().decode("ut")

   
    
    else:
        form = ImportForm()
    
    context['form'] = form
    return render(request, "import_pdf.html", context)

def userslist(request):
    context = {}
    User = get_user_model()
    users = User.objects.all()
    print(users)
    ulst = []
    for i in users:
        print(i.email)
        ulst.append([i.username,i.email])
    context['users'] = ulst

    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
        context['image'] = "/static" + imgurl[0]

    return render(request, "userslist.html", context)


def addcat(request):
    # print("ADDCAT")
    context = {}

    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
        context['image'] = "/static" + imgurl[0]

    if request.method == 'POST':
        u = request.POST['catname']
        print("Cname is:",u)

        newcat = Category(category_name=u)
        newcat.save()
        # return HttpResponse("Success")
        
    return render(request, "addcategory.html",context)


def deletecat(request):
    # print("DELETECAT")
    form = DeleteForm()
    context = {"form" : form}

    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
        context['image'] = "/static" + imgurl[0]

    if request.method == 'POST':
        
        if request.POST.get('valves') is not None:
            u = request.POST.get('valves')
            if u != '':
                Category.objects.filter(category_id=u).first().delete()
                
        # return HttpResponse("Success")
        return render(request, "deletecategory.html",context)
    return render(request, "deletecategory.html",context)


def deletecourse(request):
    form = DeleteForm()
    context = {"form" : form}

    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
        context['image'] = "/static" + imgurl[0]

    if request.method == 'POST':
        CATEGORY_CHOICES1 = []
        
        # print("Exam id:",request.POST.get('examid'))
        # print("Cname is:",u)
        if request.POST.get('examid') is not None:
            examid = request.POST.get('examid')
            print("Exam id:",examid)

            eid = ExamHeader.objects.filter(exam_id=examid).delete()
            # dashid = Dashboard.objects.filter(course_id=eid)[0]
            # print("Dash id",dashid)
            # qid = ExamQuestion.objects.filter(exam_ref=eid)
            # for i in eid:
            #     print("QID:",i.exam_id)
            # return render(request, "deletecategory.html",context)
        if request.POST.get('valves') is not None:
            u = request.POST.get('valves')
            if u != '':
                catref = Category.objects.filter(category_id=u).first()
                que = ExamHeader.objects.filter(category_ref=catref)

                CATEGORY_CHOICES1 = []

                # CATEGORY_CHOICES.append(('-1', 'Select'))
                for choice in ExamHeader.objects.filter(category_ref=catref):
                    CATEGORY_CHOICES1.append((choice.exam_id, choice.name))
                # print("Que:",CATEGORY_CHOICES1)
                context['cat'] = CATEGORY_CHOICES1
        # return HttpResponse("Success")
        return render(request, "deletecourse.html",context)
    return render(request, "deletecourse.html",context)


def updatekeywords(request):
    # print("DELETECAT")
    form = DeleteForm()
    context = {"form" : form}

    image = Img.objects.filter(filetitle=request.user.id)
    imgurl = []
    if image:
        for img11 in image:
            imgurl.append(img11.file.url.split('/media')[1])
        context['image'] = "/static" + imgurl[0]

    if request.method == 'POST':
        CATEGORY_CHOICES1 = []
        
        # print("Exam id:",request.POST.get('examid'))
        # print("Cname is:",u)
        if request.POST.get('examid') is not None:
            examid = request.POST.get('examid')
            print("Exam id:",examid)
            print("Keywords:",request.POST['keyword'])
            ExamHeader.objects.filter(exam_id=examid).update(keywords=request.POST['keyword'])
            # dashid = Dashboard.objects.filter(course_id=eid)[0]
            # print("Dash id",dashid)
            # qid = ExamQuestion.objects.filter(exam_ref=eid)
            # for i in eid:
            #     print("QID:",i.exam_id)
            # return render(request, "deletecategory.html",context)
        if request.POST.get('valves') is not None:
            u = request.POST.get('valves')
            if u != '':
                catref = Category.objects.filter(category_id=u).first()
                que = ExamHeader.objects.filter(category_ref=catref)

                CATEGORY_CHOICES1 = []

                # CATEGORY_CHOICES.append(('-1', 'Select'))
                for choice in ExamHeader.objects.filter(category_ref=catref):
                    CATEGORY_CHOICES1.append((choice.exam_id, choice.name))
                # print("Que:",CATEGORY_CHOICES1)
                context['cat'] = CATEGORY_CHOICES1
                
        # return HttpResponse("Success")
        return render(request, "updatekeyword.html",context)
    return render(request, "updatekeyword.html",context)

def aboutus(request):
    return render(request, "aboutus.html")

def contactus(request):
    # print("Request:",request.user.email)
    # name = database.child('redlight').get().val()
    # print("Database value:",name)
    if request.method == 'POST':
        # print("Data is:",request.POST.get('fullName'))
        data = {
            "name": request.POST.get('fullName'),
            "email": request.POST.get('contactemail'),
            "subject": request.POST.get('subject'),
            "message": request.POST.get('message')
        }
        database.child('users').push(data)
    return render(request, "contact.html")

def signupform(request):
    return render(request, "signup.html")
# def addcourse(request):
    
#     # def _parse_line(line):
#     #     for key, rx in rx_dict.items():
#     #         match = rx.search(line)
#     #         if match:
#     #             return key, match
#     #     # if there are no matches
#     #     return None, None

#     if request.method == 'POST' : 
#         form = ImportForm(request.POST or None)
#         file = request.FILES['pdf_file']
        
#         reader = PdfReader(file)
#         # print("Reader is:", reader)
#         text = ""
#         lst = []
#         for page in reader.pages:
#             text += page.extract_text() +"\n"
#         #     lst.append(page.extract_text() +"\n")
#         # print (lst)
#         buffer = text.split ("\n")
#         # print ( "First Line : " + text.split('\n', 1)[0] ) 
#         print("Buffer is:",buffer[0])
        
#         for i in buffer:
#             lst.append(i)
#         print(len(lst))


#         exam_header =ExamHeader(name= buffer[0], desc = line, slug = slug, keywords=keywords)
#         exam_header.save()
        
#     form = ImportForm()
#     return render(request, "addcourse.html", {"form" : form})
