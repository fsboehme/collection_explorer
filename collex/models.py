import mimetypes
import time
from http.client import IncompleteRead
from tempfile import NamedTemporaryFile
from urllib import request
from urllib.error import URLError

from django.core.files import File
from django.db import models
from easy_thumbnails.files import generate_all_aliases
from slugify import slugify

from collex.eth_queries import fetch_items, convert_to_https


class Collection(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    address = models.CharField(max_length=255)
    abi = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def update_items(self):
        fetch_items(self)


class Item(models.Model):
    collection = models.ForeignKey(Collection, related_name='items', on_delete=models.CASCADE)
    token_id = models.IntegerField()
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    tokenUri = models.URLField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['collection', 'token_id']

    def __str__(self):
        return f"{self.token_id} - {self.name}"

    def get_remote_image(self, force_update=False):
        if self.image_url and (not self.image or force_update):
            print('Fetching image for', self.collection, self.token_id, self.name)
            img_temp = NamedTemporaryFile(delete=True)
            url = convert_to_https(self.image_url)
            response, content = self.safe_request(url)
            content_type = response.headers['content-type']
            extension = mimetypes.guess_extension(content_type)
            img_temp.write(content)
            img_temp.flush()
            self.image.save(f"{self.collection.slug}/{self.token_id}{extension}", File(img_temp))
            generate_all_aliases(self.image, include_global=True)
            self.save()

    def safe_request(self, url):
        try:
            response = request.urlopen(url)
        except URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
            print('Retrying in 5 seconds...')
            time.sleep(5)
            return self.safe_request(url)
        if not response.getcode() == 200:
            print('Error:', response.getcode())
            print('Retrying in 5 seconds...')
            time.sleep(5)
            return self.safe_request(url)
        try:
            content = response.read()
        except (IncompleteRead) as e:
            print('Incomplete read:', e)
            print('Retrying...')
            return self.safe_request(url)
        return response, content
