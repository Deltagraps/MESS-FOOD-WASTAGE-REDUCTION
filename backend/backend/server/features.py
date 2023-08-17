import backend.settings as settings
from .models import Student, Meal
from rest_framework import status
from .serializer import StudentSerializer
from datetime import datetime
from backend.settings import MESS_STATE
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


REGISTER = [None]*settings.REGISTER_MACHINES
REGISTER_WAITING = [None]*settings.REGISTER_MACHINES
PLATE = [None]*settings.PLATE_MACHINES
WEIGHT = [None]*settings.WEIGHT_MACHINES
WASH = [None]*settings.WASH_MACHINES


def get_meal_type():
    hours = datetime.now().hour
    if hours in range(0, 11):
        return 'breakfast'
    elif hours in range(11, 16):
        return 'lunch'
    elif hours in range(16, 19):
        return 'snacks'
    elif hours in range(19, 24):
        return 'dinner'
    else:
        return None


def broadcast(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'hostel5',
        {'type': 'chat_message','message': message}
    )

############## REGISTRATION ################

def reg_handler(json_data):
    global REGISTER
    global REGISTER_WAITING
    index = int(json_data['id'][1:]) - 1
    payload = json_data['data']
    operation = json_data['context']
    response = {}
    response['id'] = json_data['id']
    response['context'] = operation
    match operation:
        case 'PIN':
            REGISTER[index] = payload
            response['status'] = status.HTTP_202_ACCEPTED
        case 'REG':
            user = json_data['user']
            try:
                student = Student.objects.get(rollNumber=user)
                if (student.RFID == None or len(student.RFID) < 4):
                    student.RFID = payload
                    student.isVerified = True
                    student.save()
                    response['data'] = student.rollNumber
                    response['status'] = status.HTTP_423_LOCKED
                else:
                    response['data'] = student.rollNumber
                    response['status'] = status.HTTP_304_NOT_MODIFIED
            except Student.DoesNotExist:
                response['status'] = status.HTTP_403_FORBIDDEN
    return response


################ PLATE ###################

def plate_handler(json_data):
    global PLATE
    index = int(json_data['id'][1:]) - 1
    payload = json_data['data']
    operation = json_data['context']
    response = {}
    response['id'] = json_data['id']
    response['context'] = operation
    match operation:
        case 'PIN':
            print("Pin Recived")
            PLATE[index] = payload
            response['status'] = status.HTTP_202_ACCEPTED  
        case 'AUTH':
            print("Auth Recived")
            try:
                student = Student.objects.get(RFID=payload)
                response['data'] = student.nickName
                print(response['data'])
                if (not Meal.objects.filter(student=student, date=datetime.now().date()).exists()):
                    meal = Meal(student=student, date=datetime.now().date())
                    meal.save()
                meal = Meal.objects.get(student=student, date=datetime.now().date())
                if get_meal_type() == None:
                    response['status'] = status.HTTP_503_SERVICE_UNAVAILABLE
                else:
                    meal_state = getattr(meal, get_meal_type())  
                    print(meal_state)     
                    if meal_state ==None:
                        setattr(meal, get_meal_type(), 'NM')
                        meal.save()
                        response['status'] = status.HTTP_201_CREATED
                    else:
                        response['status'] = status.HTTP_208_ALREADY_REPORTED
            except Student.DoesNotExist:
                  response['data'] = None
                  response['status'] = status.HTTP_404_NOT_FOUND
    return response


################ WEIGHT ###################


def weight_handler(json_data):
    global WEIGHT
    index = int(json_data['id'][1:]) - 1
    payload = json_data['data']
    operation = json_data['context']
    response = {}
    response['id'] = json_data['id']
    response['context'] = operation
    match operation:
        case 'PIN':
            print("Pin Recived")
            WEIGHT[index] = payload
            response['status'] = status.HTTP_202_ACCEPTED  
        case 'WEIGHT':
            weight = json_data['weight']
            print("Weight Recived")
            try:
                student = Student.objects.get(RFID=payload)
                response['data'] = student.nickName
                print(response['data'])
                try: 
                    meal = Meal.objects.get(student=student, date=datetime.now().date())
                    if get_meal_type() == None:
                        response['status'] = status.HTTP_503_SERVICE_UNAVAILABLE
                    else:
                        meal_state = getattr(meal, get_meal_type())  
                    print(meal_state)     
                    if meal_state == "NM":
                        setattr(meal, get_meal_type(), weight)
                        meal.save()
                        response['status'] = status.HTTP_202_ACCEPTED
                    elif meal_state == None or meal_state == '':
                        response['status'] = status.HTTP_204_NO_CONTENT
                    else:
                        response['status'] = status.HTTP_208_ALREADY_REPORTED
                except Meal.DoesNotExist:
                    response['status'] = status.HTTP_204_NO_CONTENT
            except Student.DoesNotExist:
                  response['data'] = None
                  response['status'] = status.HTTP_404_NOT_FOUND
    return response


#################### APP  ########################


def app_state(json_data):
    index = json_data['index']
    payload = json_data['payload']
    user = json_data['user']
    response = {}
    student = Student.objects.get(rollNumber=user)
    if student.RFID != None:
        response['isVerified'] = True
    response['mealType'] = get_meal_type()
    try:
        meal = Meal.objects.filter(student=student, type=get_meal_type(), date=datetime.now().date())
        response['plateTaken'] = True
        if meal.weight != None:
            response['weight'] = meal.weight
    except Meal.DoesNotExist:
        pass


def app_reg(id, pin, user):
    index = int(id[1:]) - 1
    global REGISTER
    global REGISTER_WAITING
    response = {}
    response['id'] = id
    response['context'] = 'REG'
    if pin == REGISTER[index]:
        REGISTER[index] = None
        try:
            student = Student.objects.get(rollNumber=user)
            response['data'] = student.rollNumber
            response['status'] = status.HTTP_202_ACCEPTED
            broadcast(response)
            return status.HTTP_202_ACCEPTED
        except Student.DoesNotExist:
            response['status'] = status.HTTP_406_NOT_ACCEPTABLE
            broadcast(response)
            return status.HTTP_406_NOT_ACCEPTABLE

    else:
        response['status'] = status.HTTP_401_UNAUTHORIZED
        broadcast(response)
        return status.HTTP_401_UNAUTHORIZED

def app_plate(id, pin, user):
    global PLATE
    index = int(id[1:]) - 1 
    response = {}
    response['id'] = id
    response['context'] = 'AUTH'
    if pin == PLATE[index]:
        PLATE[index]= None
        try:
            student = Student.objects.get(rollNumber=user)
            response['data'] = student.nickName
            if (not Meal.objects.filter(student=student, date=datetime.now().date()).exists()):
                meal = Meal(student=student, date=datetime.now().date())
                meal.save()
            meal = Meal.objects.get(student=student, date=datetime.now().date())
            if get_meal_type() == None:
                response['status'] = 503
                broadcast(response)
                return status.HTTP_503_SERVICE_UNAVAILABLE
            else:
                meal_state = getattr(meal, get_meal_type())       
                if meal_state ==None:
                    setattr(meal, get_meal_type(), 'NM')
                    meal.save()
                    response['status'] = 201
                    broadcast(response)
                    return status.HTTP_201_CREATED
                else:
                    response['status'] = 208
                    broadcast(response)
                    return status.HTTP_208_ALREADY_REPORTED
        except Student.DoesNotExist:
                response['status'] = 404
                broadcast(response)
                return status.HTTP_404_NOT_FOUND
    else:
        response['status'] = 401
        broadcast(response)
        return status.HTTP_401_UNAUTHORIZED
     
        

def app_weigh(id, pin, user):
    global WEIGHT
    index = int(id[1:]) - 1
    response = {}
    response['id'] = id
    response['context'] = 'CNFM'
    print(WEIGHT[index])
    if WEIGHT[index] == pin:
        WEIGHT[index]= None
        try:
            student = Student.objects.get(rollNumber=user)
            response['name'] = student.nickName
            response['user'] = student.RFID
            response['status'] = status.HTTP_202_ACCEPTED
            broadcast(response)
            return status.HTTP_202_ACCEPTED
        except Student.DoesNotExist:
                response['status'] = 404
                broadcast(response)
                return status.HTTP_404_NOT_FOUND
    else:
        response['status'] = 401
        broadcast(response)
        return status.HTTP_401_UNAUTHORIZED


