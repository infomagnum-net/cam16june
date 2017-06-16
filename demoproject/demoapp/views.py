from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from PIL import Image
import os,time,datetime
import numpy as np
from .forms import *
from time import gmtime, strftime
from datetime import timedelta
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import logout
import logging
import uuid
import requests
import json
from django.template.loader import get_template
from xhtml2pdf import pisa
import StringIO
from django.template import Context
from django.conf import settings
from wsgiref.util import FileWrapper
import mimetypes
import shutil
from svm_training import svmtrainer
from django.contrib.auth.decorators import login_required

log = logging.getLogger(__name__)
log.debug("Hey there it works!!")
log.info("Hey there it works!!")
log.warn("Hey there it works!!")
log.error("Hey there it works!!")

# Create your views here.



@login_required
def Ledger(request):
    userdata=VideoCaptured.objects.all()[::-1]
    return render(request,"test3.html",{"userinfo":userdata,})

@login_required
def indexpage(request):
    known_names_list=[]
    total_unknown=VideoCaptured.objects.filter(status="UnTrained").count()
    total_known_ppl=VideoCaptured.objects.filter(status="Known")
    for name in total_known_ppl:
        known_names_list.append(name.name)
    total_captured=len(set(VideoCaptured.objects.filter(status='Known').values_list('uuid')))
    total_lpr=VideoCaptured.objects.filter(status="Numberplate").count()
    StartDate = (datetime.datetime.now()) - datetime.timedelta(days=1)
    end_date = (StartDate + datetime.timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    thirtydays_unknown=VideoCaptured.objects.filter(created_at__range=(StartDate,end_date),status="UnTrained").count()
    
    thirtydays_known=VideoCaptured.objects.filter(created_at__range=(StartDate,end_date),status="Known").count()
    thirtydays_all=VideoCaptured.objects.filter(created_at__range=(StartDate,end_date)).count()
    total_known=len(set(known_names_list))

    today_start=((datetime.datetime.now()).strftime('%Y-%m-%d'))+" 00:00:00"
    today_end=(datetime.datetime.now()).strftime('%Y-%m-%d')+" 23:59:59"
    today_unknown = VideoCaptured.objects.filter(created_at__range=(today_start,today_end),status="UnTrained").count()
    today_known = VideoCaptured.objects.filter(created_at__range=(today_start,today_end),status="Known").count()
    total_today=today_unknown+today_known

    return render(request,"index.html",{"total_unknown":total_unknown,
        "total_known":total_known,"total_captured":total_captured,"total_lpr":total_lpr,
        'thirtydays_unknown':thirtydays_unknown,'thirtydays_known':thirtydays_known,
        'thirtydays_all':thirtydays_all,'today_unknown':today_unknown,
        'today_known':today_known,'total_today':total_today})

def signup(request):
    error_msg=""
    success_msg=""
    form = RegistrationForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            uname=request.POST.get("username")
            email=request.POST.get("email")
            pass1=request.POST.get("password1")
            pass2=request.POST.get("password2")
            
            user_check=User.objects.filter(username=uname)
            if user_check:
                error_msg="Username Already Exists"
            else:
                User.objects.create_user(username=uname,email=email,password=pass1)
                success_msg="User Successfully Created."
        else:
            print ("form not valid")
    
    print '********'*20
    print success_msg
    print error_msg

    return render(request,"newsignup.html",{"form":form,"errormsg":error_msg,"success_msg":success_msg})

def login(request):
    error_msg=""
    success_msg=""
    form = LoginForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            uname=request.POST.get("username")
            pass1=request.POST.get("password")
            user = authenticate(username=uname, password=pass1)
            if user:
                auth_login(request, user)
                return redirect('/')
            else:
                error_msg="Invalid Username/Password."

        else:
            print ("form not valid")

    return render(request,"newlogin.html",{"form":form,"errormsg":error_msg,"success_msg":success_msg})

def logoutuser(request):
    ''' Logout '''
    logout(request)
    return redirect('/')

@login_required
def KnownFaces(request):
    unique_uuid=VideoCaptured.objects.values_list('name',flat=True).distinct()
    userinfo={}
    for name in unique_uuid:
        usritag_info=VideoCaptured.objects.filter(name=name)
        usrimages=VideoCaptured.objects.filter(name=name,status="Known").last()
        if usrimages:
        
            udict={str((usrimages.image)).split("<ImageFieldFile:")[0]:usrimages.name}
            userinfo.update(udict)
    return render(request,"knownfaces.html",{"userinfo":userinfo})


@login_required
def UknownFaces(request):
    unique_uuid=VideoCaptured.objects.values_list('uuid',flat=True).distinct()
    userinfo={}
    for unqid in unique_uuid:
        usritag_info=VideoCaptured.objects.filter(uuid=unqid)
        usrimages=VideoCaptured.objects.filter(uuid=unqid,status="UnTrained").last()
        if usrimages:
        
            udict={str((usrimages.image)).split("<ImageFieldFile:")[0]:usrimages.uuid}
            userinfo.update(udict)

    return render(request,"untrained.html",{"userinfo":userinfo})
  

@login_required
def TrainingFaces(request):
    unique_uuid=VideoCaptured.objects.values_list('uuid',flat=True).distinct()
    userinfo={}
    for unqid in unique_uuid:
        usritag_info=VideoCaptured.objects.filter(uuid=unqid)
        usrimages=VideoCaptured.objects.filter(uuid=unqid,status="UnTrained").last()
        if usrimages:
        
            udict={str((usrimages.image)).split("<ImageFieldFile:")[0]:usrimages.uuid}
            userinfo.update(udict)

    return render(request,"training.html",{"userinfo":userinfo})

def UserTagging(request,userid):
    print ('******************')
    print (userid)
    userdata=VideoCaptured.objects.filter(uuid=userid).last()
    form = TaggingForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            uname=request.POST.get("username")
            mnum=request.POST.get("mobile")
            occupation=request.POST.get("occupation")
            VideoCaptured.objects.filter(uuid=userid).update(status="Known",name=uname,occupation=occupation)
            return redirect("/known")
    else:
        print (form.errors)
    return render(request,"tagging.html",{'userdata':userdata,'form':form})


def test(request):
    datadict={}
    datalist=[]
    unique_uuid=VideoCaptured.objects.filter(uuid='059edfda-5fe4-407f-a875-f1fbe5629814')
    for usr in unique_uuid:
        print (usr.uuid)
    return HttpResponse(unique_uuid)

def Numberplate(request):
    data = VideoCaptured.objects.filter(status="LPR")[::-1]
    return render(request,"untrained.html",{"data":data})

def ClearAll(request):
    VideoCaptured.objects.all().delete()
    #TagUserInfo.objects.all().delete()
    #redisdb.flushdb()
    return render(request,"ClearSuccess.html")

def EditInfo(request):
    uname=request.GET.get("username")
    userid=request.GET.get('userid')
    username = VideoCaptured.objects.filter(name=uname)
    if username:
        useruuid = VideoCaptured.objects.filter(name=uname).values_list('uuid')
        VideoCaptured.objects.filter(id=userid).update(uuid=useruuid[0],name=uname)
    else:
        print "Else Block"
        VideoCaptured.objects.filter(id=userid).update(uuid=uuid.uuid4(),name=uname)
    return render(request,"popupname.html",{'name':uname})

def TimelinePopup(request):
    print '*************'
    uuid=request.GET.get('uuid')
    userinfo = VideoCaptured.objects.filter(id=uuid)
    image=""
    name=""
    useruuid=""
    created_at_list=[]
    for x in userinfo:
        image=x.image
        name=x.name
        useruuid=x.uuid
        break
    uuiddata=VideoCaptured.objects.filter(uuid=useruuid)
    for x in uuiddata:
        created_at_list.append(x.created_at)

    return render(request,"timelinepopup.html",{'image':image,'name':name,
        'created_at_list':set(created_at_list[:11]),'uuid':uuid})


def PopUpUserTagging(request):
    print ('******************')
    print request.GET
    uname=request.GET.get('username')
    usrid=request.GET.get('userid')
    print usrid
    print uname
    useruuid = VideoCaptured.objects.filter(id=usrid).values_list('uuid')
    print useruuid
    VideoCaptured.objects.filter(uuid=useruuid[0][0]).update(name=uname)
    return render(request,"popupname.html",{'name':uname})
def DeleteRecord(request,userid):
    VideoCaptured.objects.filter(id=userid).delete()
    return HttpResponse("Record Successfully Deleted")
def MultiTraining(request):
    uuid_list=request.GET.getlist('uuid[]')
    print '*******************'
    print uuid_list
    print '*****************'
    username=request.GET.get('usrname')
    VideoCaptured.objects.filter(uuid__in=uuid_list).update(name=username,status="Known")
    return HttpResponse("name changed successfully")

def LedgerPopup(request):
    username=request.GET.get("username")
    return render(request,"ledgerpopup.html",{'username':username})


def Lastdaytimeline(request):
    return HttpResponse("this is sample")

def timelineaddname(request):
    userinfo={}
    untrained_photos = VideoCaptured.objects.filter(status="UnTrained")
    for untrain in untrained_photos:
        userinfo.update({untrain.uuid:untrain.image})
    return render(request,"untrained_photos.html",{'userinfo':userinfo})


# def timelineeditname(request):
#     userinfo={}
#     trained_photos = VideoCaptured.objects.filter(status="Known")
#     for train in trained_photos:
#         userinfo.update({train.name:[train.image,train.uuid]})
#     return render(request,"trained_photos.html",{'userinfo':userinfo})



def timelineeditname(request):
    userinfo={}
    trained_photos = VideoCaptured.objects.all()
    for train in trained_photos:
        userinfo.update({train.uuid:[train.image,train.name]})
    return render(request,"trained_photos.html",{'userinfo':userinfo})




def timelinedeletename(request):
    trained_photos = VideoCaptured.objects.all()
    print '**************'
    print trained_photos
    return render(request,"delete_photos.html",{'trained_photos':trained_photos})


def timelineinfo(request):
    userinfo={}
    untrained_photos = VideoCaptured.objects.filter(status="UnTrained")
    for untrain in untrained_photos:
        userinfo.update({untrain.uuid:untrain.image})
    return render(request,"untrained_photos.html",{'userinfo':userinfo})


def MultiEdit(request):
    filepath = os.getcwd()
    id_list=request.GET.getlist('id[]')
    uname=request.GET.get('usrname')
    uuidinfo=VideoCaptured.objects.filter(id__in=id_list)
    num_of_records = len(uuidinfo)
    for i,uid in enumerate(uuidinfo):
        path1 = filepath+"/demoapp"+str(uid.image)
        path2=filepath+"/demoapp/static/media/TrainingPhotos/"+uname+"-"+str(i)+".jpg"
        shutil.copy(path1,path2)
    VideoCaptured.objects.filter(id__in=id_list).update(name=uname,uuid=uname)

    #     uuid_list.append(uid.uuid)
    # username = VideoCaptured.objects.filter(name=uname).values_list('uuid')
    # if username:
    #     username = VideoCaptured.objects.filter(uuid__in=uuid_list).update(name=uname,uuid=username[0][0],status="Known")
    # else:
    #     unqid=uuid.uuid4()
    #     #VideoCaptured.objects.filter(uuid__in=uuid_list).update(uuid=unqid,name=uname,status="Known")
    #     VideoCaptured.objects.filter(uuid__in=uuid_list).update(name=uname,status="Known")
    return HttpResponse("this is multiedit")


def DeleteMultiple(request):
    id_list=request.GET.getlist('id[]')
    VideoCaptured.objects.filter(id__in=id_list).delete()
    return HttpResponse("delete")


def infotimeline(request):
    userinfo={}
    trained_photos = VideoCaptured.objects.all()
    for train in trained_photos:
        userinfo.update({train.uuid:[train.image,train.name]})
    return render(request,"info.html",{'userinfo':userinfo})

def multiinfo(request):
    datadict={}
    id_list=request.GET.getlist('id[]')
    uuidele = (((id_list[0].split("(")[1]).split(")")[0]).split("'")[1])
    for x in id_list:
        db = VideoCaptured.objects.filter(x)
        for x in db:
            pass

    return render(request,"multiinfo.html")

@login_required
def Completetimeline(request):
    today_dte = datetime.datetime.now().strftime('%Y-%m-%d')
    timelineresults={}
    for i in range(24):
        date_val=("%02d" % (i))
        satart_time=today_dte+" "+("%02d" % (i))+":00:00"
        end_time=today_dte+" "+("%02d" % (i))+":59:59"
        knownfaces = VideoCaptured.objects.filter(created_at__range=(satart_time,end_time),status="Known")
        unknownfaces = VideoCaptured.objects.filter(created_at__range=(satart_time,end_time),status="UnTrained")
        sample_dict={}
        for face in knownfaces:
            sample_dict.update({face.uuid:[face.image,face.id,face.name,((face.created_at).split(" "))[1]]})
        for face in unknownfaces:
            sample_dict.update({face.uuid:[face.image,face.id,face.name,((face.created_at).split(" "))[1]]})
        timelineresults.update({int(date_val):sample_dict})
    #return HttpResponse("this is complete timeline")
    return render (request,"completetimeline.html",{'timelineresults':timelineresults,'today_dte':today_dte})

# def Completetimeline(request):
#     today_start=((datetime.datetime.now()).strftime('%Y-%m-%d'))+" 00:00:00"
#     today_end=(datetime.datetime.now()).strftime('%Y-%m-%d')+" 23:59:59"
#     today_dte = datetime.datetime.now().strftime('%Y-%m-%d')
#     check_exists = VideoCaptured.objects.filter(created_at__range=(today_start,today_end))
#     error_msg=""
#     if not check_exists:
#         error_msg = "Sorry Results Not Available"
#     timelineresults={}
     
#     for i in range(24):
#         date_val=("%02d" % (i))
#         satart_time=today_dte+" "+("%02d" % (i))+":00:00"
#         end_time=today_dte+" "+("%02d" % (i))+":59:59"
#         knownfaces = VideoCaptured.objects.filter(created_at__range=(satart_time,end_time),status="Known")
#         unknownfaces = VideoCaptured.objects.filter(created_at__range=(satart_time,end_time),status="UnTrained")
#         sample_dict={}
#         for face in knownfaces:
#             sample_dict.update({face.uuid:[face.image,face.id,face.name,((face.created_at).split(" "))[1]]})
#         for face in unknownfaces:
#             sample_dict.update({face.uuid:[face.image,face.id,face.name,((face.created_at).split(" "))[1]]})
#         timelineresults.update({int(date_val):sample_dict})
#     return render (request,"completetimeline.html",{'timelineresults':timelineresults,
#         'today_dte':today_dte,'error_msg':error_msg})
    #return HttpResponse("this is complete timeline")


    



def GetInfo(request):
    id_list=request.GET.getlist('id[]')
    uuid_list=[]
    maindict={}
    uuidinfo=VideoCaptured.objects.filter(id__in=id_list)
    for uid in uuidinfo:
        uuid_list.append(uid.uuid)
    #print '**************'
    uuid_results = set(uuid_list)
    for x in uuid_results:
        data = VideoCaptured.objects.filter(uuid=x)
        for y in data:
            maindict.update({y.uuid:[data.count(),y.name,y.image]})
            break
   
    return render(request,"info.html",{'maindict':maindict})

def TrainedPeopleGroup(request):
    trained_dict={}
    trained_ppl = VideoCaptured.objects.filter(status="Known")
    for trnd in trained_ppl:
        trained_dict.update({trnd.name:trnd.image})

    return render(request,"trainedgrp.html",{"trained_dict":trained_dict})


@login_required
def VisitingReports(request):
    form = VisitorReportsForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            startdate=(str(request.POST.get("startdate"))).split("/")
            enddate=(str(request.POST.get("enddate"))).split("/")
            st_date=int(startdate[0])
            st_month=int(startdate[1])
            st_year=int(startdate[2])
            enddate=(str(request.POST.get("enddate"))).split("/")
            en_date=int(enddate[0])
            en_month=int(enddate[1])
            en_year=int(enddate[2])
            start_date=((datetime.datetime(st_year, st_month, st_date)).strftime('%Y-%m-%d'))+" "+"00:00:00"
            end_date=((datetime.datetime(en_year, en_month, en_date)).strftime('%Y-%m-%d'))+" "+"23:59:59"
            print start_date
            print end_date
            visitor_results= VideoCaptured.objects.filter(created_at__range=(start_date,enddate))
            data = {"userinfo":visitor_results}
            #return render(request,"template_testing.html",data)
            template = get_template('template_testing.html')
            html  = template.render(Context(data))
            result = StringIO.StringIO()
            rendering = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
            if not rendering.err:
                return HttpResponse(result.getvalue(),  content_type='application/pdf')
            return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))
        else:
            print '*************'
            print form.errors

    return render(request,"reports.html")


@login_required
def Videos(request):
    vid = request.GET.get("id")
    capturevideos = EventVideos.objects.filter(id=vid)
    return render(request,"videopopup.html",{"capturevideos":capturevideos})
@login_required
def addcamera(request):
    return render(request,"addcam.html")

@login_required
def eventresults(request):
    capturevideos=EventVideos.objects.all()
    return render(request,"events.html",{"capturevideos":capturevideos})

# def download(request, path):
#     file_path = os.path.join(settings.MEDIA_ROOT, "videos/11.mp4")
#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
#             return response

def smart_str(x):
    if isinstance(x, unicode):
        return unicode(x).encode("utf-8")
    elif isinstance(x, int) or isinstance(x, float):
        return str(x)
    return x

def download(request,eid):
    filename = ((EventVideos.objects.get(id=eid).path).split("/static/media/")[1]).encode('utf-8')
    print filename
    file_path = settings.MEDIA_ROOT +'/'+ filename
    file_wrapper = FileWrapper(file(file_path,'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype )
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s/' % smart_str(filename) 
    return response

def deletevideo(request,eid):
    EventVideos.objects.get(id=eid).delete()
    return redirect("/eventresults/")

def trainsvm(request):
    svmtrainer()
    return HttpResponse("training completed")
    
def Testlogin(request):
    error_msg=""
    success_msg=""
    form = RegistrationForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            print request.POST
            uname=request.POST.get("username")
            email=request.POST.get("email")
            pass1=request.POST.get("password")
            user_check=User.objects.filter(username=uname)
            if user_check:
                error_msg="Username Already Exists"
            else:
                User.objects.create_user(username=uname,email=email,password=pass1)
                success_msg="User Successfully Created."
        else:
            print ("form not valid")
    return render(request,"newsignup.html",{"form":form,"errormsg":error_msg,"success_msg":success_msg})


def Lockscreen(request):
    error_msg=""
    success_msg=""
    form = LockscreenForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            uname=request.user.username
            pass1=request.POST.get("password")
            print uname
            print pass1
            user = authenticate(username=uname, password=pass1)
            if user:
                return redirect('/')
            else:
                error_msg="Invalid Username/Password."
           
        else:
            print ("form not valid")
    return render(request,"lockscreen.html",{'form':form})