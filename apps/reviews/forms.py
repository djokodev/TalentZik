"""
Formulaires pour le système d'avis et notations
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Review, ReviewRequest, ReviewResponse


class ReviewForm(forms.ModelForm):
    """
    Formulaire pour laisser un avis sur un artiste
    """

    class Meta:
        model = Review
        fields = ["rating", "comment", "event_date", "event_type", "event_location"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)],
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                },
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                    "rows": 4,
                    "placeholder": "Partagez votre expérience avec cet artiste...",
                }
            ),
            "event_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                }
            ),
            "event_type": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                }
            ),
            "event_location": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                    "placeholder": "Ville ou lieu de l'événement",
                }
            ),
        }

    def clean_event_date(self):
        event_date = self.cleaned_data.get("event_date")
        if event_date and event_date > timezone.now().date():
            raise ValidationError(
                "La date de l'événement ne peut pas être dans le futur."
            )
        if event_date and event_date < timezone.now().date() - timedelta(days=365):
            raise ValidationError(
                "La date de l'événement ne peut pas être antérieure à 1 an."
            )
        return event_date

    def clean_comment(self):
        comment = self.cleaned_data.get("comment")
        if comment and len(comment.strip()) < 10:
            raise ValidationError(
                "Le commentaire doit contenir au moins 10 caractères."
            )
        return comment


class ReviewRequestForm(forms.ModelForm):
    """
    Formulaire pour demander un avis à un client
    """

    class Meta:
        model = ReviewRequest
        fields = [
            "client_email",
            "client_name",
            "client_phone",
            "event_date",
            "event_type",
            "event_location",
            "message",
        ]
        widgets = {
            "client_email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                    "placeholder": "Email du client",
                }
            ),
            "client_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                    "placeholder": "Nom complet du client",
                }
            ),
            "client_phone": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                    "placeholder": "+237 6XX XXX XXX",
                }
            ),
            "event_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                }
            ),
            "event_type": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                }
            ),
            "event_location": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                    "placeholder": "Ville ou lieu de l'événement",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                    "rows": 3,
                    "placeholder": "Message personnalisé (optionnel)",
                }
            ),
        }

    def clean_event_date(self):
        event_date = self.cleaned_data.get("event_date")
        if event_date and event_date > timezone.now().date():
            raise ValidationError(
                "La date de l'événement ne peut pas être dans le futur."
            )
        return event_date

    def save(self, commit=True):
        review_request = super().save(commit=False)
        # Définir la date d'expiration (30 jours après création)
        review_request.expires_at = timezone.now() + timedelta(days=30)
        if commit:
            review_request.save()
        return review_request


class ReviewResponseForm(forms.ModelForm):
    """
    Formulaire pour répondre à un avis
    """

    class Meta:
        model = ReviewResponse
        fields = ["response_text"]
        widgets = {
            "response_text": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                    "rows": 4,
                    "placeholder": "Répondez de manière professionnelle et courtoise...",
                }
            ),
        }

    def clean_response_text(self):
        response_text = self.cleaned_data.get("response_text")
        if response_text and len(response_text.strip()) < 10:
            raise ValidationError("La réponse doit contenir au moins 10 caractères.")
        return response_text


class PublicReviewForm(forms.ModelForm):
    """
    Formulaire public pour laisser un avis via lien envoyé par l'artiste
    """

    organizer_name = forms.CharField(
        label="Votre nom",
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Votre nom complet",
            }
        ),
    )

    organizer_email = forms.EmailField(
        label="Votre email",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "votre.email@exemple.com",
            }
        ),
    )

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)],
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                },
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                    "rows": 4,
                    "placeholder": "Partagez votre expérience avec cet artiste...",
                }
            ),
        }

    def clean_comment(self):
        comment = self.cleaned_data.get("comment")
        if comment and len(comment.strip()) < 10:
            raise ValidationError(
                "Le commentaire doit contenir au moins 10 caractères."
            )
        return comment
