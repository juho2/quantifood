from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User  # django built-in User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    food_history = JSONField(default=list(), blank=True)

    def __repr__(self):
        return(self.food_history)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
class Food(models.Model):
#    id = models.IntegerField(primary_key=True)
    id_string = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    recipe_yield = models.CharField(max_length=20)
    servings = models.CharField(max_length=20)
    url = models.CharField(max_length=200)
    ingredients = JSONField(default=dict())
    nutrients = JSONField(default=dict())
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __repr__(self):
        return(self.name)        

#class User(models.Model):
# #   id = models.IntegerField(primary_key=True)
#    name = models.CharField(max_length=200)
#    join_date = models.DateTimeField('Date joined')
#    
#    def joined_recently(self):
#        return self.join_date >= timezone.now() - datetime.timedelta(weeks=1)
#    def __repr__(self):
#        return(self.name)