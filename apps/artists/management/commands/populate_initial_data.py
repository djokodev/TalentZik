"""
Commande Django pour peupler la base de données avec les données initiales
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.artists.models import MusicGenre, ArtistRole, Instrument


class Command(BaseCommand):
    help = "Peuple la base de données avec les genres, rôles et instruments camerounais"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Début du peuplement des données initiales...")
        )

        with transaction.atomic():
            self.create_music_genres()
            self.create_artist_roles()
            self.create_instruments()

        self.stdout.write(self.style.SUCCESS("Données initiales créées avec succès !"))

    def create_music_genres(self):
        """Crée les genres musicaux camerounais et internationaux"""

        # Genres camerounais/africains
        cameroon_genres = [
            (
                "Makossa",
                "Genre musical traditionnel camerounais popularisé par Manu Dibango",
                True,
            ),
            ("Bikutsi", "Musique traditionnelle du peuple Beti du Cameroun", True),
            ("Assiko", "Genre musical traditionnel du peuple Bassa du Cameroun", True),
            (
                "Ndombolo",
                "Style de musique congolaise populaire en Afrique centrale",
                True,
            ),
            (
                "Coupé-Décalé",
                "Genre musical ivoirien populaire en Afrique de l'Ouest",
                True,
            ),
            (
                "Afrobeat",
                "Fusion de jazz, funk et musiques traditionnelles africaines",
                True,
            ),
            ("Afro-trap", "Fusion moderne entre trap et musiques africaines", True),
            ("Gospel", "Musique chrétienne contemporaine", False),
            ("Afro", "Musique africaine contemporaine", True),
            ("Africaine", "Musiques traditionnelles africaines", True),
            ("Antillaise", "Musiques des Antilles", False),
            ("Chaabi", "Genre musical populaire du Maghreb", False),
            ("Slave", "Musique traditionnelle afro-américaine", False),
        ]

        # Genres internationaux populaires
        international_genres = [
            ("Hip-hop", "Genre musical né aux États-Unis", False),
            ("Rap", "Style vocal du hip-hop", False),
            ("RnB", "Rhythm and Blues contemporain", False),
            ("Jazz", "Genre musical né aux États-Unis", False),
            ("Blues", "Genre musical afro-américain", False),
            ("Soul", "Musique soul américaine", False),
            ("Funk", "Genre musical groove", False),
            ("Reggae", "Musique jamaïcaine", False),
            ("Dancehall", "Genre dérivé du reggae", False),
            ("Reggaeton", "Genre musical latino-américain", False),
            ("Zouk", "Musique des Antilles françaises", False),
            ("Salsa", "Musique latino-américaine", False),
            ("Pop", "Musique populaire", False),
            ("Rock", "Rock and roll", False),
            ("Électronique", "Musique électronique", False),
            ("House", "Musique house", False),
            ("Techno", "Musique techno", False),
            ("Dance", "Musique de danse", False),
            ("Latino", "Musiques latino-américaines", False),
            ("Acoustique", "Musique acoustique", False),
        ]

        all_genres = cameroon_genres + international_genres

        for name, description, is_traditional in all_genres:
            genre, created = MusicGenre.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "is_traditional": is_traditional,
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"Genre créé: {name}")

    def create_artist_roles(self):
        """Crée les rôles/spécialités d'artistes"""

        roles = [
            # Artistes/Interprètes
            ("Chanteur/Chanteuse", "Artiste vocal principal"),
            ("Choriste", "Chanteur d'accompagnement"),
            ("Rappeur/Rappeuse", "Artiste de rap/hip-hop"),
            ("MC/Animateur", "Maître de cérémonie et animateur"),
            ("DJ", "Disc-jockey"),
            ("DJ Vinyle", "DJ spécialisé dans les vinyles"),
            ("VJ (Video Jockey)", "Artiste visuel et vidéo"),
            # Groupes/Ensembles
            ("Groupe/Band", "Groupe musical"),
            ("Duo", "Formation à deux artistes"),
            ("Trio", "Formation à trois artistes"),
            ("Quartet", "Formation à quatre artistes"),
            ("Chorale", "Ensemble vocal"),
            ("Chœur Gospel", "Chœur spécialisé dans le gospel"),
            ("Orchestre", "Grand ensemble instrumental"),
            ("Fanfare", "Ensemble de cuivres et percussions"),
            ("Orchestre traditionnel", "Ensemble d'instruments traditionnels"),
            # Professionnels Techniques
            ("Arrangeur musical", "Spécialiste des arrangements"),
            ("Producteur", "Producteur musical"),
            ("Compositeur", "Créateur de compositions musicales"),
            ("Parolier", "Auteur de paroles"),
            ("Chef de chœur", "Directeur de chœur"),
            ("Chef d'orchestre", "Directeur d'orchestre"),
            ("Technicien son", "Technicien audio"),
            ("Ingénieur du son", "Ingénieur audio professionnel"),
            ("Mixeur", "Spécialiste du mixage audio"),
            ("Sound Designer", "Créateur de paysages sonores"),
            # Multi-compétences
            ("Multi-instrumentiste", "Musicien polyvalent"),
            ("Artiste complet", "Artiste aux multiples talents"),
            ("Professeur de musique", "Enseignant musical"),
        ]

        for name, description in roles:
            role, created = ArtistRole.objects.get_or_create(
                name=name, defaults={"description": description, "is_active": True}
            )
            if created:
                self.stdout.write(f"Rôle créé: {name}")

    def create_instruments(self):
        """Crée les instruments traditionnels et modernes"""

        # Instruments traditionnels camerounais
        traditional_instruments = [
            ("Balafon", "Xylophone traditionnel africain"),
            ("Tam-tam", "Tambour traditionnel"),
            ("Djembé", "Tambour en forme de calice"),
            ("Sanza (Piano à pouces)", "Instrument à lamelles métalliques"),
            ("Kora", "Harpe-luth ouest-africaine"),
            ("Xylophone traditionnel", "Xylophone en bois traditionnel"),
            ("Percussion traditionnelle", "Instruments de percussion traditionnels"),
            ("Cornes traditionnelles", "Instruments à vent traditionnels"),
        ]

        # Instruments modernes
        modern_instruments = [
            ("Guitare", "Guitare acoustique"),
            ("Guitare électrique", "Guitare électrique"),
            ("Piano", "Piano acoustique"),
            ("Clavier/Synthé", "Clavier électronique et synthétiseur"),
            ("Batterie", "Batterie complète"),
            ("Basse", "Guitare basse"),
            ("Contrebasse", "Contrebasse acoustique"),
            ("Violon", "Violon"),
            ("Alto", "Alto"),
            ("Violoncelle", "Violoncelle"),
            ("Harpe", "Harpe classique"),
            ("Saxophone", "Saxophone"),
            ("Trompette", "Trompette"),
            ("Trombone", "Trombone"),
            ("Flûte", "Flûte traversière"),
            ("Clarinette", "Clarinette"),
            ("Hautbois", "Hautbois"),
            ("Basson", "Basson"),
            ("Orgue", "Orgue"),
            ("Accordéon", "Accordéon"),
            ("Harmonica", "Harmonica"),
            ("Tuba", "Tuba"),
            ("Percussion", "Instruments de percussion"),
            ("Xylophone", "Xylophone moderne"),
            ("Luth", "Luth"),
            ("Sitar", "Sitar"),
        ]

        # Créer les instruments traditionnels
        for name, description in traditional_instruments:
            instrument, created = Instrument.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "category": "traditional",
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"Instrument traditionnel créé: {name}")

        # Créer les instruments modernes
        for name, description in modern_instruments:
            instrument, created = Instrument.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "category": "modern",
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"Instrument moderne créé: {name}")
