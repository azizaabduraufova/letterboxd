from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.films.models import Actor, Director

def generate_unique_slug(model, name_field='name', slug_field='slug'):
    """
    Generate a unique slug for a model based on the `name_field`.
    Appends a number if the slug is already taken.
    """
    for obj in model.objects.all():
        base_slug = slugify(getattr(obj, name_field))
        slug = base_slug
        counter = 1
        while model.objects.filter(**{slug_field: slug}).exclude(pk=obj.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        setattr(obj, slug_field, slug)
        obj.save()
        print(f"Set slug for {obj}: {slug}")

class Command(BaseCommand):
    help = "Populate unique slugs for Actors and Directors"

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating slugs for Actors...")
        generate_unique_slug(Actor)
        self.stdout.write("Generating slugs for Directors...")
        generate_unique_slug(Director)
        self.stdout.write(self.style.SUCCESS("Slugs generated successfully!"))
