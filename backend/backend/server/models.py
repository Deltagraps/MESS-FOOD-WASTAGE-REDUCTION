from django import forms
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


def image_handler(instance, filename):
    ext = filename.split('.')[-1]
    return "/".join(["photos", '{}.{}'.format(instance.rollNumber, ext)])

def council_handler(instance, filename):
    ext = filename.split('.')[-1]
    return "/".join(["council", '{}.{}'.format(instance.por, ext)])


def post_handler(instance, filename):
    ext = filename.split('.')[-1]
    return "/".join(["posts", '{}.{}'.format(instance.title, ext)])

def menu_handler(instance, filename):
    ext = filename.split('.')[-1]
    return "/".join(["pdf", '{}.{}'.format("menu", ext)])

def hostelfile_handler(instance, filename):
    ext = filename.split('.')[-1]
    return "/".join(["pdf", '{}.{}'.format(instance.name, ext)])


def inventory_handler(instance, filename):
    ext = filename.split('.')[-1]
    return "/".join(["inventory/", '{}.{}'.format(instance.name, ext)])


def complaint_handler(instance, filename):
    ext = filename.split('.')[-1]
    return "/".join(["complaints", '{}.{}'.format(instance.title, ext)])


def otherimages(instance, filename):
    ext = filename.split('.')[-1]
    return "/".join(["images", '{}.{}'.format(instance.title, ext)])


TECH_INVENTORY = [("E", "Electrical"), ("M", "Mechanical")]


MEAL_CHOICES = [('B', 'Breakfast'),
                ('L', 'Lunch'),
                ('S', 'Snacks'),
                ('D', 'Dinner')]


STATUS = [('A', "Allowed"),
          ('NA', "Not Allowed")]


DOMAIN = [('Cult', 'Cult'), ('Sports', 'Sports'), ('Tech', 'Tech')]

def image_name_validation(filename):
    print(len(filename.split(" ")))
    if len(filename.split(" "))> 1:
        print("entry")
        raise ValidationError(
            ("%(filename)s must not contain spaces!"),
            params={"filename": filename},
        )



class MyAccountManager(BaseUserManager):
    def create_user(self, rollNumber, name, mobileNumber, password=None):
        if not rollNumber:
            raise ValueError("Provide a username")
        if not mobileNumber:
            raise ValueError('Mobile Number is required')
        user = self.model(rollNumber=rollNumber, name=name, mobileNumber=mobileNumber)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, rollNumber, name, mobileNumber, password):
        user = self.create_user(
            name = name,
            rollNumber = rollNumber,
            mobileNumber=mobileNumber,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user



class Student(AbstractBaseUser):
    name                     = models.CharField(max_length=50)
    nickName                 = models.CharField(max_length=15, blank=True)
    rollNumber               = models.CharField(max_length=50, unique=True)
    mobileNumber             = models.CharField(max_length=20)
    roomNumber               = models.CharField(max_length=3, blank=True)
    RFID                     = models.CharField(max_length=10, blank=True)
    photo                    = models.ImageField(upload_to=image_handler, blank=True)
    isCompleted              = models.BooleanField(default=False)
    isVerified               = models.BooleanField(default=False)
    is_admin                 = models.BooleanField(default=False)
    is_active                = models.BooleanField(default=True)
    is_staff                 = models.BooleanField(default=False)
    is_superuser             = models.BooleanField(default=False)

    objects = MyAccountManager()

    USERNAME_FIELD = 'rollNumber'
    REQUIRED_FIELDS = ['name', 'mobileNumber']

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, server):
        return True
    
    class Meta:
        ordering = ['roomNumber']
    





class Council(models.Model):
    por = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    mobile =  models.CharField(max_length=15)
    image = models.ImageField(upload_to=council_handler, default='default.jpg')

    def __str__(self):
        return self.por


class Event(models.Model):
    title = models.CharField(max_length=20, blank=False)
    post = models.ImageField(upload_to=post_handler)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(max_length=500)
    likes = models.IntegerField()

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ['-date']


class MessMenu(models.Model):
    file = models.FileField(upload_to=menu_handler)
    start = models.DateField(auto_now=False, default=now)

    def __str__(self):
        return str(self.start.day) + str(self.start.strftime('%b'))

    class Meta:
        ordering = ["start"]


class HostelFile(models.Model):
    name = models.CharField(max_length=15)
    file = models.FileField(upload_to=hostelfile_handler)
    def __str__(self):
        return self.name


class InventoryCategory(models.Model):
    domain = models.CharField(max_length=10, choices=DOMAIN)
    heading = models.CharField(max_length=50)

    class Meta:
        ordering = ["domain"]

    def __str__(self):
        return self.heading


class InventoryItem(models.Model):
    item = models.ForeignKey(InventoryCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=50)
    quantity = models.IntegerField()
    photo = models.ImageField(upload_to=inventory_handler, default='static/none.jpg')
    damage_reports = models.IntegerField()

    class Meta:
        ordering = ['item__domain']

    def __str__(self):
         return self.name        


class Meal(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    breakfast = models.CharField(max_length=6, blank=True, null=True)
    lunch = models.CharField(max_length=6, blank=True, null=True)
    snacks = models.CharField(max_length=6, blank=True, null=True)
    dinner = models.CharField(max_length=6, blank=True, null=True)
    date = models.DateField()
    

    class Meta:
        ordering = ["-date", "student__rollNumber"]

    def __str__(self):    
        return self.student.rollNumber + "/" + str(self.date)


COMPLAINT_CATEGORY = [("Mess", "Mess"), ("Maint", "Maintanence"), ("Sports", "Sports"), ("Tech", "Tech"), ("Network", "Network")]
COMPLAINT_STATUS = [('Completed', 'Completed'), ('Pending', 'Pending'), ('Rejected', 'Rejected')]

class Complaint(models.Model):
    title = models.CharField(max_length=20)
    type = models.CharField(max_length = 20, choices=COMPLAINT_CATEGORY)
    date = models.DateField(auto_now_add=now)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=complaint_handler, blank=True)
    details = models.TextField(max_length=200)
    status = models.CharField(max_length = 20, choices = COMPLAINT_STATUS, default='Pending')





class OtherImages(models.Model):
    title = models.CharField(max_length=20, validators=[image_name_validation])
    image = models.ImageField(upload_to=otherimages)
    
    def __str__(self):
        return self.title



