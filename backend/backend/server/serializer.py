from .models import Meal, Student, Event, Council, InventoryCategory, InventoryItem, Complaint
from rest_framework import serializers

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['name', 'nickName', 'rollNumber', 'mobileNumber', 'roomNumber', 'isVerified', 'photo', 'isCompleted']
        
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['date', 'breakfast', 'lunch', 'snacks', 'dinner']

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = "__all__"

class CouncilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Council
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCategory
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['name', 'location', 'photo', 'quantity']