from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Rating, NewsArticle

@receiver(post_save, sender=Rating)
def send_rating_notification(sender, instance, created, **kwargs):
    article = instance.article
    author = article.editor
    user = instance.user
    rating_value = instance.ratings

    if author and author.email:
        subject = f"New rating on your article '{article.title}'" if created else f"Rating updated for your article '{article.title}'"
        message = (
            f"Hello {author.get_full_name()},\n\n"
            f"Your article '{article.title}' has {'received a new' if created else 'been updated with a new'} rating.\n"
            f"User: {user.get_full_name()}\n"
            f"Rating: {rating_value} stars\n\n"
            "Best regards,\nTwenty Four 7 News"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [author.email], fail_silently=True)

    if user and user.email:
        subject = f"Thank you for rating '{article.title}'" if created else f"Your rating for '{article.title}' has been updated"
        message = (
            f"Hello {user.get_full_name()},\n\n"
            f"Thank you for {'rating' if created else 'updating your rating for'} the article '{article.title}'.\n"
            f"Your rating: {rating_value} stars\n\n"
            "We appreciate your feedback!\nTwenty Four 7 News"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
