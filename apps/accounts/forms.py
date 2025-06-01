"""
Formulaires pour l'authentification et les profils utilisateurs
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User, ArtistProfile, OrganizerProfile
from apps.artists.models import (
    MusicGenre,
    ArtistRole,
    Instrument,
    ArtistGenre,
    ArtistRoleAssignment,
    ArtistInstrument,
)


class TalentZikLoginForm(AuthenticationForm):
    """
    Formulaire de connexion personnalisé
    """

    username = forms.EmailField(
        label=_("Adresse email"),
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "votre@email.com",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Votre mot de passe",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Adresse email")


class UserRegistrationForm(UserCreationForm):
    """
    Formulaire de base pour l'inscription d'un utilisateur
    """

    email = forms.EmailField(
        label=_("Adresse email"),
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "votre@email.com",
            }
        ),
    )
    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Votre prénom",
            }
        ),
    )
    last_name = forms.CharField(
        label=_("Nom"),
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Votre nom",
            }
        ),
    )
    password1 = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Choisissez un mot de passe",
            }
        ),
    )
    password2 = forms.CharField(
        label=_("Confirmer le mot de passe"),
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Confirmez votre mot de passe",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Un compte avec cette adresse email existe déjà."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class ArtistRegistrationForm(UserRegistrationForm):
    """
    Formulaire d'inscription pour les artistes
    """

    stage_name = forms.CharField(
        label=_("Nom de scène"),
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Votre nom d'artiste (optionnel)",
            }
        ),
        help_text=_("Nom artistique ou nom de scène (optionnel)"),
    )
    phone_number = forms.CharField(
        label=_("Numéro de téléphone"),
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "+237 XXX XXX XXX",
            }
        ),
    )
    whatsapp_number = forms.CharField(
        label=_("Numéro WhatsApp"),
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "+237 XXX XXX XXX (optionnel)",
            }
        ),
        help_text=_("Numéro WhatsApp pour contact direct (optionnel)"),
    )
    city = forms.CharField(
        label=_("Ville"),
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Douala, Yaoundé, Bafoussam...",
            }
        ),
    )
    region = forms.CharField(
        label=_("Région"),
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Littoral, Centre, Ouest...",
            }
        ),
    )
    bio = forms.CharField(
        label=_("Biographie"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "rows": 4,
                "placeholder": "Parlez-nous de votre parcours musical, votre style, vos influences...",
            }
        ),
        help_text=_("Description de votre parcours et style musical (optionnel)"),
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "stage_name",
            "phone_number",
            "whatsapp_number",
            "city",
            "region",
            "bio",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = "artist"
        if commit:
            user.save()
            # Créer le profil artiste
            profile = ArtistProfile.objects.create(
                user=user,
                stage_name=self.cleaned_data.get("stage_name", ""),
                phone_number=self.cleaned_data["phone_number"],
                whatsapp_number=self.cleaned_data.get("whatsapp_number", ""),
                city=self.cleaned_data["city"],
                region=self.cleaned_data["region"],
                bio=self.cleaned_data.get("bio", ""),
            )
        return user


class OrganizerRegistrationForm(UserRegistrationForm):
    """
    Formulaire d'inscription pour les organisateurs
    """

    organization_name = forms.CharField(
        label=_("Nom de l'organisation"),
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Nom de votre entreprise, église, association... (optionnel)",
            }
        ),
        help_text=_("Nom de l'entreprise, église, association, etc. (optionnel)"),
    )
    organization_type = forms.ChoiceField(
        label=_("Type d'organisation"),
        choices=OrganizerProfile.ORGANIZATION_TYPE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            }
        ),
    )
    phone_number = forms.CharField(
        label=_("Numéro de téléphone"),
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "+237 XXX XXX XXX",
            }
        ),
    )
    whatsapp_number = forms.CharField(
        label=_("Numéro WhatsApp"),
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "+237 XXX XXX XXX (optionnel)",
            }
        ),
        help_text=_("Numéro WhatsApp pour contact direct (optionnel)"),
    )
    city = forms.CharField(
        label=_("Ville"),
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Douala, Yaoundé, Bafoussam...",
            }
        ),
    )
    region = forms.CharField(
        label=_("Région"),
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Littoral, Centre, Ouest...",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "organization_name",
            "organization_type",
            "phone_number",
            "whatsapp_number",
            "city",
            "region",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = "organizer"
        if commit:
            user.save()
            # Créer le profil organisateur
            profile = OrganizerProfile.objects.create(
                user=user,
                organization_name=self.cleaned_data.get("organization_name", ""),
                organization_type=self.cleaned_data["organization_type"],
                phone_number=self.cleaned_data["phone_number"],
                whatsapp_number=self.cleaned_data.get("whatsapp_number", ""),
                city=self.cleaned_data["city"],
                region=self.cleaned_data["region"],
            )
        return user


class ArtistProfileForm(forms.ModelForm):
    """
    Formulaire de modification du profil artiste
    """

    class Meta:
        model = ArtistProfile
        fields = [
            "stage_name",
            "phone_number",
            "whatsapp_number",
            "bio",
            "profile_picture",
            "city",
            "region",
            "is_available",
        ]
        widgets = {
            "stage_name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "Votre nom de scène",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "+237 XXX XXX XXX",
                }
            ),
            "whatsapp_number": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "+237 XXX XXX XXX",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "rows": 4,
                    "placeholder": "Parlez-nous de votre parcours musical...",
                }
            ),
            "profile_picture": forms.FileInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "accept": "image/*",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "Votre ville",
                }
            ),
            "region": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "Votre région",
                }
            ),
            "is_available": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-orange-600 shadow-sm focus:border-orange-300 focus:ring focus:ring-orange-200 focus:ring-opacity-50",
                }
            ),
        }


class OrganizerProfileForm(forms.ModelForm):
    """
    Formulaire de modification du profil organisateur
    """

    class Meta:
        model = OrganizerProfile
        fields = [
            "organization_name",
            "organization_type",
            "phone_number",
            "whatsapp_number",
            "city",
            "region",
        ]
        widgets = {
            "organization_name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "Nom de votre organisation",
                }
            ),
            "organization_type": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "+237 XXX XXX XXX",
                }
            ),
            "whatsapp_number": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "+237 XXX XXX XXX",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "Votre ville",
                }
            ),
            "region": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "Votre région",
                }
            ),
        }


class EnhancedEditProfileForm(forms.Form):
    """
    Formulaire d'édition complet du profil avec UX améliorée pour la culture camerounaise
    """

    # Champs User
    first_name = forms.CharField(
        label="Prénom",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
            }
        ),
    )

    last_name = forms.CharField(
        label="Nom",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
            }
        ),
    )

    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
            }
        ),
    )

    # Champs ArtistProfile
    phone_number = forms.CharField(
        label="Numéro de téléphone",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                "placeholder": "+237 XXX XXX XXX",
            }
        ),
        help_text="Numéro de téléphone principal",
    )

    city = forms.CharField(
        label="Ville",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
            }
        ),
    )

    # Champs spécifiques aux artistes
    stage_name = forms.CharField(
        label="Nom de scène",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
            }
        ),
        help_text="Nom artistique ou nom de scène (optionnel)",
    )

    bio = forms.CharField(
        label="Biographie",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                "rows": 4,
            }
        ),
        help_text="Description de votre parcours et style musical",
    )

    profile_picture = forms.ImageField(
        label="Photo de profil",
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                "accept": "image/*",
            }
        ),
    )

    # Genres musicaux avec groupement par tradition/modernité
    genres_traditional = forms.ModelMultipleChoiceField(
        label="🎵 Genres traditionnels camerounais",
        queryset=MusicGenre.objects.filter(
            is_active=True, is_traditional=True
        ).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "grid grid-cols-2 gap-2",
            }
        ),
        help_text="Sélectionnez vos genres traditionnels camerounais de prédilection",
    )

    genres_modern = forms.ModelMultipleChoiceField(
        label="🌍 Genres modernes et internationaux",
        queryset=MusicGenre.objects.filter(
            is_active=True, is_traditional=False
        ).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "grid grid-cols-2 gap-2",
            }
        ),
        help_text="Sélectionnez vos genres modernes et internationaux",
    )

    # Rôles artistiques avec descriptions
    roles = forms.ModelMultipleChoiceField(
        label="🎭 Rôles et spécialités artistiques",
        queryset=ArtistRole.objects.filter(is_active=True).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "grid grid-cols-1 gap-2",
                "data-toggle": "tooltip",
            }
        ),
        help_text="Sélectionnez vos spécialités (cliquez pour voir les descriptions)",
    )

    # Instruments par catégorie
    instruments_traditional = forms.ModelMultipleChoiceField(
        label="🥁 Instruments traditionnels africains",
        queryset=Instrument.objects.filter(
            is_active=True, category="traditional"
        ).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "grid grid-cols-2 gap-2",
            }
        ),
        help_text="Instruments traditionnels camerounais et africains que vous maîtrisez",
    )

    instruments_modern = forms.ModelMultipleChoiceField(
        label="🎹 Instruments modernes",
        queryset=Instrument.objects.filter(is_active=True, category="modern").order_by(
            "name"
        ),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "grid grid-cols-2 gap-2",
            }
        ),
        help_text="Instruments modernes que vous maîtrisez",
    )

    # Champs spécifiques aux organisateurs
    organization_name = forms.CharField(
        label="Nom de l'organisation",
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent",
            }
        ),
        help_text="Nom de votre entreprise, église, association, etc. (optionnel)",
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            # Préremplir les champs avec les données existantes
            if self.user.user_type == "artist" and hasattr(self.user, "artist_profile"):
                profile = self.user.artist_profile
                self.fields["first_name"].initial = self.user.first_name
                self.fields["last_name"].initial = self.user.last_name
                self.fields["email"].initial = self.user.email
                self.fields["phone_number"].initial = profile.phone_number
                self.fields["city"].initial = profile.city
                self.fields["stage_name"].initial = profile.stage_name
                self.fields["bio"].initial = profile.bio

                # Préremplir les relations many-to-many avec séparation
                artist_genres = [ag.genre for ag in profile.genres.all()]
                self.fields["genres_traditional"].initial = [
                    g for g in artist_genres if g.is_traditional
                ]
                self.fields["genres_modern"].initial = [
                    g for g in artist_genres if not g.is_traditional
                ]

                self.fields["roles"].initial = [ar.role for ar in profile.roles.all()]

                artist_instruments = [ai.instrument for ai in profile.instruments.all()]
                self.fields["instruments_traditional"].initial = [
                    i for i in artist_instruments if i.category == "traditional"
                ]
                self.fields["instruments_modern"].initial = [
                    i for i in artist_instruments if i.category == "modern"
                ]

                # Masquer les champs organisateur
                del self.fields["organization_name"]

            elif self.user.user_type == "organizer" and hasattr(
                self.user, "organizer_profile"
            ):
                profile = self.user.organizer_profile
                self.fields["first_name"].initial = self.user.first_name
                self.fields["last_name"].initial = self.user.last_name
                self.fields["email"].initial = self.user.email
                self.fields["phone_number"].initial = profile.phone_number
                self.fields["city"].initial = profile.city
                self.fields["organization_name"].initial = profile.organization_name

                # Masquer les champs artiste
                del self.fields["stage_name"]
                del self.fields["bio"]
                del self.fields["profile_picture"]
                del self.fields["genres_traditional"]
                del self.fields["genres_modern"]
                del self.fields["roles"]
                del self.fields["instruments_traditional"]
                del self.fields["instruments_modern"]

    def get_grouped_data(self):
        """Retourne les données groupées pour un affichage organisé"""
        if not self.user:
            return {}

        data = {
            "user_info": {
                "title": "👤 Informations personnelles",
                "fields": ["first_name", "last_name", "email", "phone_number", "city"],
            }
        }

        if self.user.user_type == "artist":
            data.update(
                {
                    "artist_info": {
                        "title": "🎤 Informations artistiques",
                        "fields": ["stage_name", "bio", "profile_picture"],
                    },
                    "musical_identity": {
                        "title": "🎵 Identité musicale",
                        "sections": [
                            {
                                "title": "Genres traditionnels camerounais",
                                "field": "genres_traditional",
                                "description": "Sélectionnez les genres traditionnels que vous pratiquez",
                            },
                            {
                                "title": "Genres modernes et internationaux",
                                "field": "genres_modern",
                                "description": "Sélectionnez les genres modernes que vous pratiquez",
                            },
                        ],
                    },
                    "skills": {
                        "title": "🎭 Compétences et instruments",
                        "sections": [
                            {
                                "title": "Rôles et spécialités",
                                "field": "roles",
                                "description": "Vos rôles dans le monde musical",
                            },
                            {
                                "title": "Instruments traditionnels",
                                "field": "instruments_traditional",
                                "description": "Instruments traditionnels que vous maîtrisez",
                            },
                            {
                                "title": "Instruments modernes",
                                "field": "instruments_modern",
                                "description": "Instruments modernes que vous maîtrisez",
                            },
                        ],
                    },
                }
            )
        else:
            data.update(
                {
                    "organization_info": {
                        "title": "🏢 Informations organisationnelles",
                        "fields": ["organization_name"],
                    }
                }
            )

        return data

    def save(self, user):
        """Sauvegarder les modifications avec gestion des catégories"""
        from django.db import transaction

        with transaction.atomic():
            # Sauvegarder les champs User
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.email = self.cleaned_data["email"]
            user.save()

            if user.user_type == "artist" and hasattr(user, "artist_profile"):
                profile = user.artist_profile
                profile.phone_number = self.cleaned_data["phone_number"]
                profile.city = self.cleaned_data["city"]
                profile.stage_name = self.cleaned_data.get("stage_name", "")
                profile.bio = self.cleaned_data.get("bio", "")

                # Gestion de la photo de profil
                if self.cleaned_data.get("profile_picture"):
                    profile.profile_picture = self.cleaned_data["profile_picture"]

                profile.save()

                # Gestion des relations Many-to-Many avec fusion des catégories
                # Genres (fusion traditional + modern)
                profile.genres.all().delete()
                all_genres = list(
                    self.cleaned_data.get("genres_traditional", [])
                ) + list(self.cleaned_data.get("genres_modern", []))
                for genre in all_genres:
                    ArtistGenre.objects.create(artist=profile, genre=genre)

                # Rôles
                if "roles" in self.cleaned_data:
                    profile.roles.all().delete()
                    for role in self.cleaned_data["roles"]:
                        ArtistRoleAssignment.objects.create(artist=profile, role=role)

                # Instruments (fusion traditional + modern)
                profile.instruments.all().delete()
                all_instruments = list(
                    self.cleaned_data.get("instruments_traditional", [])
                ) + list(self.cleaned_data.get("instruments_modern", []))
                for instrument in all_instruments:
                    ArtistInstrument.objects.create(
                        artist=profile,
                        instrument=instrument,
                        proficiency_level="intermediate",  # Valeur par défaut
                    )

            elif user.user_type == "organizer" and hasattr(user, "organizer_profile"):
                profile = user.organizer_profile
                profile.phone_number = self.cleaned_data["phone_number"]
                profile.city = self.cleaned_data["city"]
                profile.organization_name = self.cleaned_data.get(
                    "organization_name", ""
                )
                profile.save()


# Gardons l'ancien formulaire pour la compatibilité
EditProfileForm = EnhancedEditProfileForm
