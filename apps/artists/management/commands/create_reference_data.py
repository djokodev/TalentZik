"""
Commande pour créer les données de référence musicales
"""

from django.core.management.base import BaseCommand
from apps.artists.models import MusicGenre, ArtistRole, Instrument


class Command(BaseCommand):
    help = "Crée les données de référence pour les genres, rôles et instruments"

    def handle(self, *args, **options):
        self.stdout.write("Création des données de référence...")

        # Genres musicaux camerounais et africains
        genres_data = [
            # Genres traditionnels camerounais
            {
                "name": "Makossa",
                "is_traditional": True,
                "description": "Genre musical traditionnel du Cameroun, originaire de Douala",
            },
            {
                "name": "Bikutsi",
                "is_traditional": True,
                "description": "Genre musical traditionnel du centre du Cameroun",
            },
            {
                "name": "Mangambeu",
                "is_traditional": True,
                "description": "Musique traditionnelle du peuple Bassa",
            },
            {
                "name": "Assiko",
                "is_traditional": True,
                "description": "Genre traditionnel du sud du Cameroun",
            },
            {
                "name": "Bend-skin",
                "is_traditional": True,
                "description": "Musique populaire urbaine camerounaise",
            },
            # Genres modernes populaires
            {
                "name": "Afrobeat",
                "is_traditional": False,
                "description": "Fusion de musique yoruba, jazz, highlife et funk",
            },
            {
                "name": "Afropop",
                "is_traditional": False,
                "description": "Pop africaine moderne",
            },
            {
                "name": "Coupé-décalé",
                "is_traditional": False,
                "description": "Genre musical ivoirien populaire en Afrique centrale",
            },
            {
                "name": "Ndombolo",
                "is_traditional": False,
                "description": "Variante moderne de la rumba congolaise",
            },
            {
                "name": "Highlife",
                "is_traditional": False,
                "description": "Genre musical d'Afrique de l'Ouest",
            },
            # Genres spirituels
            {
                "name": "Gospel",
                "is_traditional": False,
                "description": "Musique chrétienne contemporaine",
            },
            {
                "name": "Spiritual",
                "is_traditional": False,
                "description": "Musique spirituelle traditionnelle",
            },
            # Genres internationaux
            {"name": "R&B", "is_traditional": False, "description": "Rhythm and Blues"},
            {
                "name": "Hip-Hop",
                "is_traditional": False,
                "description": "Culture musicale urbaine",
            },
            {
                "name": "Reggae",
                "is_traditional": False,
                "description": "Genre musical jamaïcain",
            },
            {
                "name": "Jazz",
                "is_traditional": False,
                "description": "Genre musical afro-américain",
            },
            {
                "name": "Blues",
                "is_traditional": False,
                "description": "Genre musical afro-américain",
            },
            {
                "name": "Soul",
                "is_traditional": False,
                "description": "Musique soul afro-américaine",
            },
            {
                "name": "Funk",
                "is_traditional": False,
                "description": "Genre musical groove afro-américain",
            },
        ]

        # Rôles et spécialités d'artistes
        roles_data = [
            {"name": "Chanteur/Chanteuse", "description": "Artiste vocal principal"},
            {"name": "Choriste", "description": "Chanteur d'accompagnement"},
            {"name": "Rappeur/Rappeuse", "description": "Artiste de rap et hip-hop"},
            {"name": "DJ", "description": "Disc-jockey, mixeur de musique"},
            {"name": "Producteur", "description": "Producteur musical et beatmaker"},
            {"name": "Compositeur", "description": "Créateur de mélodies et harmonies"},
            {"name": "Parolier", "description": "Auteur de textes et paroles"},
            {"name": "Arrangeur", "description": "Arrangeur musical et orchestrateur"},
            {"name": "Instrumentiste", "description": "Musicien instrumentaliste"},
            {
                "name": "Chef d'orchestre",
                "description": "Directeur musical et chef d'ensemble",
            },
            {"name": "Soliste", "description": "Artiste solo et interprète"},
            {"name": "Membre de groupe", "description": "Musicien membre d'un groupe"},
        ]

        # Instruments traditionnels et modernes
        instruments_data = [
            # Instruments traditionnels camerounais/africains
            {
                "name": "Balafon",
                "category": "traditional",
                "description": "Xylophone africain traditionnel",
            },
            {
                "name": "Djembé",
                "category": "traditional",
                "description": "Tambour en forme de calice",
            },
            {
                "name": "Kora",
                "category": "traditional",
                "description": "Harpe-luth d'Afrique de l'Ouest",
            },
            {
                "name": "Talking Drum",
                "category": "traditional",
                "description": "Tambour parlant yoruba",
            },
            {
                "name": "Mbira",
                "category": "traditional",
                "description": "Piano à pouces africain",
            },
            {
                "name": "Sanza",
                "category": "traditional",
                "description": "Lamellophone africain",
            },
            {
                "name": "Bendir",
                "category": "traditional",
                "description": "Tambour sur cadre traditionnel",
            },
            {
                "name": "Dunun",
                "category": "traditional",
                "description": "Famille de tambours graves",
            },
            # Instruments modernes
            {
                "name": "Piano",
                "category": "modern",
                "description": "Instrument à clavier classique",
            },
            {
                "name": "Guitare acoustique",
                "category": "modern",
                "description": "Guitare à cordes non amplifiée",
            },
            {
                "name": "Guitare électrique",
                "category": "modern",
                "description": "Guitare amplifiée électroniquement",
            },
            {
                "name": "Guitare basse",
                "category": "modern",
                "description": "Instrument de basse électrique",
            },
            {
                "name": "Batterie",
                "category": "modern",
                "description": "Ensemble de percussions modernes",
            },
            {
                "name": "Saxophone",
                "category": "modern",
                "description": "Instrument à vent de la famille des bois",
            },
            {
                "name": "Trompette",
                "category": "modern",
                "description": "Instrument de cuivre",
            },
            {
                "name": "Violon",
                "category": "modern",
                "description": "Instrument à cordes frottées",
            },
            {
                "name": "Flûte",
                "category": "modern",
                "description": "Instrument à vent traversière",
            },
            {
                "name": "Synthétiseur",
                "category": "modern",
                "description": "Clavier électronique",
            },
            {
                "name": "Microphone",
                "category": "modern",
                "description": "Équipement vocal et instrumental",
            },
        ]

        # Création des genres
        for genre_data in genres_data:
            genre, created = MusicGenre.objects.get_or_create(
                name=genre_data["name"],
                defaults={
                    "description": genre_data["description"],
                    "is_traditional": genre_data["is_traditional"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"  ✓ Genre créé: {genre.name}")
            else:
                self.stdout.write(f"  - Genre existant: {genre.name}")

        # Création des rôles
        for role_data in roles_data:
            role, created = ArtistRole.objects.get_or_create(
                name=role_data["name"],
                defaults={
                    "description": role_data["description"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"  ✓ Rôle créé: {role.name}")
            else:
                self.stdout.write(f"  - Rôle existant: {role.name}")

        # Création des instruments
        for instrument_data in instruments_data:
            instrument, created = Instrument.objects.get_or_create(
                name=instrument_data["name"],
                defaults={
                    "category": instrument_data["category"],
                    "description": instrument_data["description"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"  ✓ Instrument créé: {instrument.name}")
            else:
                self.stdout.write(f"  - Instrument existant: {instrument.name}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Données de référence créées avec succès!\n"
                f"   - {MusicGenre.objects.count()} genres musicaux\n"
                f"   - {ArtistRole.objects.count()} rôles d'artistes\n"
                f"   - {Instrument.objects.count()} instruments"
            )
        )
