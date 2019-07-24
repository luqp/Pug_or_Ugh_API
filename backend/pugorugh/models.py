from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


AGE = (
    ('b', 'baby'),
    ('y', 'young'),
    ('a', 'adult'),
    ('s', 'senior')
)

GENDER = (
    ('m', 'male'),
    ('f', 'female'),
    ('u', 'unknown')
)

SIZE = (
    ('s', 'small'),
    ('m', 'medium'),
    ('l', 'large'),
    ('xl', 'extra large'),
    ('u', 'unknown')
)

STATUS = (
    ('l', 'liked'),
    ('d', 'disliked'),
    ('u', 'undecided')
)


class Dog(models.Model):
    name = models.CharField(max_length=255)
    image_filename = models.CharField(max_length=255)
    breed = models.CharField(max_length=255, blank=True)
    age = models.IntegerField()
    age_status = models.CharField(max_length=1, choices=AGE, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER, default='u')
    size = models.CharField(max_length=1, choices=SIZE, default='u')

    def __str__(self):
        return self.breed + self.name

    def save(self, *args, **kwargs):
        if self.age < 12:
            self.age_status = 'b'
        elif self.age <= 24:
            self.age_status = 'y'
        elif self.age <= 72:
            self.age_status = 'a'
        else:
            self.age_status = 's'
        super(Dog, self).save(*args, **kwargs)


class UserDog(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default='u')


class UserPref(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    age = models.CharField(max_length=255, default="b,y,a,s")
    gender = models.CharField(max_length=255, default="f,m")
    size = models.CharField(max_length=255, default="s,m,l,xl")


@receiver(post_save, sender='auth.User')
def create_user_pref(sender, instance, created, **kwargs):
    ''' Creates a UserPref object when a User object is created
        and fill UserDog table with default values
    '''
    if created:
        UserPref.objects.create(user=instance).save()
        for dog in Dog.objects.all():
            UserDog.objects.create(user=instance, dog=dog).save()
