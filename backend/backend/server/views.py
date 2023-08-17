from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Student, Meal, MessMenu, Event, Council, InventoryCategory, InventoryItem, MyAccountManager, Complaint
from .serializer import StudentSerializer, EventSerializer, CouncilSerializer, CategorySerializer, InventorySerializer, ComplaintSerializer, MealSerializer
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import functools
from backend.settings import MESS_STATE
from server.features import get_meal_type, broadcast
from datetime import datetime
from server import features
from backend.settings import REGISTER_MACHINES, PLATE_MACHINES, WEIGHT_MACHINES





@api_view(['POST'])
def login_student(request):
      print(request.data)
      rollNumber = request.data.get('rollNumber')
      print(rollNumber)
      password = request.data.get('password')
      print(password)
      user = authenticate(username=rollNumber, password=password)
      if user is not None:
            login(request, user)
            student = StudentSerializer(Student.objects.get(rollNumber=rollNumber))
            return Response(student.data, status=status.HTTP_202_ACCEPTED)
      else:
            return Response(status=status.HTTP_208_ALREADY_REPORTED)



@api_view(['POST'])
def signup_student(request):
      rollNumber = request.data.get('rollNumber')
      name = request.data.get('name')
      password1 = request.data.get('password1')
      password2 = request.data.get('password2')
      User = get_user_model()
      if password1 != password2:
            return Response({'Password doesnt match'}, status=status.HTTP_304_NOT_MODIFIED)
      elif User.objects.filter(rollNumber=rollNumber).exists():
            return Response(f'user with roll number {rollNumber} already exists.', status=status.HTTP_208_ALREADY_REPORTED)
      else:
            student = User.objects.create_user(rollNumber=rollNumber, name=name, password=password1)
            student.save()
            return Response('User created', status=status.HTTP_201_CREATED)
 

@login_required
@api_view(['GET'])
def logout_student(request):
      logout(request)
      return Response(status=status.HTTP_202_ACCEPTED)

   


@login_required
@api_view(['GET'])
def fetch_profile(request, roll):
      student = Student.objects.get(rollNumber = roll)
      profile = StudentSerializer(student)
      return Response(profile.data)



@login_required
@api_view(['GET'])
def fetch_events(request):
      print(request.headers)
      print(request.COOKIES)
      events = EventSerializer(Event.objects.all(), many =True)
      return Response(events.data)


@api_view(['GET'])
def fetch_complains(request):
      complains = ComplaintSerializer(Complaint.objects.all(), many =True)
      return Response(complains.data)

@login_required   
@api_view(['POST'])
def submit_complaint(request):
      print(request.user.rollNumber)
      student = Student.objects.get(rollNumber = request.user.rollNumber)
      print(request.data.get('title'))
      complaint = Complaint(  title=request.data.get('title'), 
                              type=request.data.get('type'),
                              student=student, 
                              details=request.data.get('details'),)
      if request.FILES.get('image') is not None:
            complaint.image = request.data['image'] 
      complaint.save()
      return Response(status=status.HTTP_200_OK)


@login_required   
@api_view(['POST'])
def save_profile(request):
      try:
            rollnumber = request.user.rollNumber
      except:
            return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
      student = Student.objects.get(rollNumber =  rollnumber)
      student.nickName = request.data['nickName']
      if request.FILES.get('image') is not None:
            student.photo = request.data['image']
      student.isCompleted = True
      student.save()
      updated_profile = StudentSerializer(student)
      return Response(updated_profile.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def fetch_council(request):
      council = CouncilSerializer(Council.objects.all(), many=True)
      return Response(council.data)


@api_view(['GET'])
def fetch_categories(request):
      categories = InventoryCategory.objects.all()
      response = CategorySerializer(categories, many=True)
      return Response(response.data)


@login_required
@api_view(['DELETE'])
def complaint_delete(request):
      id = request.data['id']
      print(id)
      complaint = Complaint.objects.get(id = id)
      complaint.delete()
      complains = ComplaintSerializer(Complaint.objects.all(), many =True)
      return Response(complains.data)
      


@api_view(['GET'])
def fetch_inventory(request, category):
      if category =='test': 
            return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
      items = InventoryItem.objects.filter(item__heading = category)
      if (len(items) > 0):
            response = InventorySerializer(items, many=True)
            return Response(response.data)
      else:
            return Response(status=status.HTTP_204_NO_CONTENT)
      

@login_required
@api_view(['POST'])
def user_check(request):
      try:
            rollnumber = request.user.rollNumber
      except:
            return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
      student = Student.objects.get(rollNumber =  rollnumber)
      profile = StudentSerializer(student)
      return Response(profile.data, status=status.HTTP_200_OK)
      


@login_required
@api_view(['GET'])
def get_mess_state(request):
      try:
            rollnumber = request.user.rollNumber
            return Response(mess_status(rollnumber), status=status.HTTP_200_OK)
      except:
            return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
      


@login_required
@api_view(['GET'])
def mess_history(request):
      try:
            rollnumber = request.user.rollNumber
            print(rollnumber)
            meal = Meal.objects.filter(student__rollNumber = rollnumber)
            meals = MealSerializer(meal, many=True)
            return Response(meals.data, status=status.HTTP_200_OK)
      except:
            return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
      
      


def mess_status(rollnumber):
      response = {
            "isVerified": False,
            "mealType": None,
            "plateTaken": False,
            "weight": None,
            "count":PLATE_MACHINES
      }
      print(rollnumber)
      student = Student.objects.get(rollNumber=rollnumber)
      print(student.RFID)
      if len(student.RFID) == 8:
            print(1)
            response['isVerified'] = True
      meal_type = get_meal_type()

      response['mealType'] = meal_type
      try:
            meal = Meal.objects.get(student=student, date=datetime.now().date())
            meal_status =  getattr(meal, meal_type)
            if meal_status != None:
                  response['plateTaken'] = True
                  response['count'] = WEIGHT_MACHINES
                  if meal_status != 'NM':
                        response['weight'] = meal_status
      except Meal.DoesNotExist:
            pass
      return response
      

@login_required
@api_view(['POST'])
def app_handler(request):
      id = request.data['id']
      operation = id[0]
      pin = request.data['pin']
      print(id)
      print(pin)
      match operation:
            case 'R':
                  statusCode = features.app_reg(id, pin, request.user.rollNumber)
                  return Response(status=statusCode)
            case 'L':
                  statusCode = features.app_plate(id, pin, request.user.rollNumber)
                  return Response(mess_status(request.user.rollNumber), status=statusCode)
            case 'W':
                  statusCode = features.app_weigh(id, pin, request.user.rollNumber)
                  return Response(mess_status(request.user.rollNumber), status=statusCode)
            case 'E':
                  return Response(mess_status(request.data), status=status.HTTP_200_OK)


@api_view(['GET'])
def reg_machines(request):
      return Response({'count':REGISTER_MACHINES}, status=status.HTTP_200_OK)



@api_view(['GET'])
def up(request):
      broadcast({"id": "W1", "context": "UP"})
      print('Broadcasted')
      return Response(status=status.HTTP_202_ACCEPTED)

@api_view(['GET'])
def down(request):
      broadcast({"id": "W1", "context": "DOWN"})
      print('Broadcasted')
      return Response(status=status.HTTP_202_ACCEPTED)
