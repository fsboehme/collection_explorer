import mimetypes
import time
from http.client import IncompleteRead
from tempfile import NamedTemporaryFile
from urllib import request
from urllib.error import URLError

from PIL import ImageColor
from django.conf import settings
from django.core.files import File
from django.db import models
from django.utils.functional import cached_property
from easy_thumbnails.files import generate_all_aliases
from easy_thumbnails.templatetags.thumbnail import thumbnail_url
from slugify import slugify

from collex.colors import ColorAnalyzer
from collex.eth_queries import fetch_items, convert_to_https


class Collection(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    address = models.CharField(max_length=255)
    abi = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    colors = models.ManyToManyField('Color', blank=True)
    color_filters = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def update_items(self):
        fetch_items(self)

    def update_color_palettes(self):
        for item in self.items.all():
            item.update_color_palette()

    def add_color(self, hex):
        color = Color.objects.get_or_create(_hex=f'#{hex}')[0]
        self.colors.add(color)
        self.save()


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

    colors = models.ManyToManyField('Color', through='ItemColor', blank=True)
    colors_string = models.TextField(blank=True)
    colors_n = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['collection', 'token_id']

    def __str__(self):
        return f"{self.token_id} - {self.name}"

    def save(self, *args, **kwargs):
        self.colors_string = ','.join(
            list(self.filtered_colors.values_list('color___hex', flat=True)))
        self.colors_n = self.filtered_colors.count()
        super().save(*args, **kwargs)

    @cached_property
    def filtered_colors(self):
        return self.itemcolor_set.filter(manually_removed=False)

    def next(self):
        try:
            return self.collection.items.get(token_id=self.token_id + 1)
        except Item.DoesNotExist:
            return None

    def previous(self):
        try:
            return self.collection.items.get(token_id=self.token_id - 1)
        except Item.DoesNotExist:
            return None

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

    def update_color_palette(self, color=None, tolerance=4, limit=20):
        """
        Update the color palette for this item.
        :param color: optionally pass a Color instance to add just that color to the palette
        """
        img = self.thumbnail_path('xs')
        ca = ColorAnalyzer(img, tolerance=tolerance, limit=limit)
        palette_colors = []
        collection_colors = self.collection.colors.all()
        colors = [color] if color else collection_colors
        for c in colors:
            amount = ca.find_in_image(c.rgb)
            if amount:
                item_color, created = ItemColor.objects.get_or_create(item=self, color=c)
                item_color.amount = amount
                item_color.save()
                palette_colors.append(c.pk)
        # remove colors not in the collection palette
        self.itemcolor_set.filter(manually_added=False).exclude(color__in=collection_colors).delete()
        # remove any colors not found, unless they were manually added (useful if tolerance has changed)
        if not color:
            self.itemcolor_set.filter(manually_added=False).exclude(color__in=palette_colors).delete()
        self.save()  # save the colors_string

    def thumbnail_path(self, size='small'):
        url = thumbnail_url(self.image, size)
        img = str(settings.BASE_DIR / url[1:])
        return img

    def extract_colors(self, tolerance=None, limit=None, save=False):
        img = self.thumbnail_path('xs')
        ca = ColorAnalyzer(img, tolerance=tolerance, limit=limit)
        palette_colors = []
        for rgb, amount in ca.extract_colors():
            hex = Color.rgb_to_hex(*rgb)
            rgb_str = f"{rgb[0]},{rgb[1]},{rgb[2]}"
            palette_colors.append(hex)
            if save:
                color, created = Color.objects.get_or_create(rgb=rgb_str)
                ItemColor.objects.get_or_create(item=self, color=color)
        return palette_colors

    def add_color(self, hex, tolerance=7):
        color = Color.objects.get_or_create(_hex=f'#{hex}'.upper())[0]
        item_color, created = ItemColor.objects.get_or_create(item=self, color=color, defaults={'manually_added': True})
        # find color in image and update amount
        self.update_color_palette(color=color, tolerance=tolerance)

    def remove_color(self, hex):
        color = Color.objects.get_or_create(_hex=f'#{hex}')[0]
        # delete if manually added
        self.itemcolor_set.filter(color=color, manually_added=True).delete()
        # update if it was regularly found
        self.itemcolor_set.filter(color=color).update(manually_removed=True)
        self.save()

    def unremove_color(self, hex):
        color = Color.objects.get_or_create(_hex=f'#{hex}')[0]
        self.itemcolor_set.filter(color=color).update(manually_removed=False)
        self.save()


class Color(models.Model):
    _rgb = models.CharField(max_length=15, blank=True, null=True)
    _hex = models.CharField(max_length=7, blank=True, null=True)

    class Meta:
        ordering = ['_hex']

    def __str__(self):
        return f"{self._hex}"

    def save(self, *args, **kwargs):
        if self._hex and not self._rgb:
            self._rgb = str(ImageColor.getrgb(self._hex))[1:-1]
        self._rgb = self._rgb.replace(' ', '')
        if self._rgb and not self._hex:
            self._hex = self.rgb_to_hex(*self.rgb)
        super().save(*args, **kwargs)

    @staticmethod
    def rgb_to_hex(r, g, b):
        return '#{:X}{:X}{:X}'.format(r, g, b)

    @property
    def rgb(self):
        return tuple(int(x) for x in self._rgb.split(','))

    @property
    def hex(self):
        return self._hex

    @property
    def hex_naked(self):
        return self._hex[1:]


class ItemColor(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    manually_removed = models.BooleanField(default=False)
    manually_added = models.BooleanField(default=False)

    class Meta:
        ordering = ['manually_removed', '-amount']
