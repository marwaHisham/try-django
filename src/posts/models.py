from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
#from django.urls import reverse
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.utils import timezone


class PostManager(models.Manager):
    def active(self,*args,**kwargs):
        return super(PostManager ,self).filter(draft=False)

# Create your models here.
def upload_location(instance ,filename):
    #filebase ,extension=filename.split('.')
    return "%s/%s" %(instance.id,filename)



class Post (models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,default=1)
    title = models.CharField(max_length=255)
    slug= models.SlugField(unique=True)
    #image = models.FileField(null = True , blank=True)
    height_field=models.IntegerField(default=0)
    width_field=models.IntegerField(default=0)
    image = models.ImageField(upload_to=upload_location,
        null = True , blank=True, 
        width_field="width_field",height_field="height_field")
    content= models.TextField()
    draft=models.BooleanField(default= False)
    publish = models.DateTimeField(default=timezone.now)
    updated=models.DateTimeField(auto_now=True ,auto_now_add=False)
    timestamp=models.DateTimeField(auto_now=False ,auto_now_add=True)



    objects=PostManager()
    
    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("detail",kwargs={"slug":self.slug})
        #return "/posts/detail/%s/" %(self.id)

    class Meta:
        ordering = ['timestamp']



def create_slug(instance , new_slug=None):
    slug=slugify(instance.title)
    if new_slug is not None:
        slug=new_slug
    qs=Post.objects.filter(slug =slug).order_by("_id")
    exists=qs.exists()
    if exists:
        new_slug="%s-%s"%(slug,qs.first().id)
        return create_slug(instance,new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender , instance ,*args , **kwargs):
    # slug=slugify(instance.title)
    # exists=Post.objects.filter(slug =slug).exists()
    # if exists:
    #     slug="%s-%s"%(slug,instance.id)
    # instance.slug =slug
    if not instance.slug:
         instance.slug=create_slug(instance)


pre_save.connect(pre_save_post_receiver ,sender= Post)