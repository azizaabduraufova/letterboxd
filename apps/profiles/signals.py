# apps/profiles/signals.py
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Profile, WatchedFilm


@receiver(m2m_changed, sender=Profile.favorite_films.through)
def favorite_films_changed(sender, instance, action, reverse, pk_set, **kwargs):
    """
    Whenever films are added to favorite_films, also mark them as watched.
    """
    # Only care when items are added
    if action not in ("post_add",):
        return

    # instance is a Profile (because sender is Profile.favorite_films.through)
    profile = instance

    # pk_set contains the primary keys of Films that were added as favorites
    for film_pk in pk_set:
        WatchedFilm.objects.get_or_create(
            profile=profile,
            film_id=film_pk,
        )