"""
Commande Django pour nettoyer et repeupler la base de données avec les données musicales camerounaises
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.artists.models import MusicGenre, ArtistRole, Instrument


class Command(BaseCommand):
    help = "Nettoie et repeuple la base de données avec les données musicales camerounaises"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirme la suppression des données existantes",
        )

    def handle(self, *args, **options):
        if not options.get("confirm"):
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Cette commande va SUPPRIMER toutes les données existantes (genres, rôles, instruments).\n"
                    "   Ajoutez --confirm pour confirmer cette action."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                "🧹 Début du nettoyage et peuplement des données musicales camerounaises..."
            )
        )

        with transaction.atomic():
            self.clean_existing_data()
            self.create_music_genres()
            self.create_artist_roles()
            self.create_instruments()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Données musicales nettoyées et créées avec succès!\n"
                f"   🎼 {MusicGenre.objects.count()} genres musicaux\n"
                f"   🎤 {ArtistRole.objects.count()} rôles d'artistes\n"
                f"   🎸 {Instrument.objects.count()} instruments"
            )
        )

    def clean_existing_data(self):
        """Supprime toutes les données existantes"""
        self.stdout.write("🧹 Nettoyage des données existantes...")

        # Supprimer les données de référence
        deleted_genres = MusicGenre.objects.count()
        deleted_roles = ArtistRole.objects.count()
        deleted_instruments = Instrument.objects.count()

        MusicGenre.objects.all().delete()
        ArtistRole.objects.all().delete()
        Instrument.objects.all().delete()

        self.stdout.write(
            f"   🗑️  Supprimés: {deleted_genres} genres, {deleted_roles} rôles, {deleted_instruments} instruments"
        )

    def create_music_genres(self):
        """Crée les genres musicaux camerounais et africains avec descriptions détaillées"""

        self.stdout.write("📚 Création des genres musicaux...")

        genres_data = [
            # Genres traditionnels camerounais (ordre alphabétique)
            {
                "name": "Ambasse Bey",
                "is_traditional": True,
                "description": "Style musical traditionnel du peuple Bassa, mélange de rythmes traditionnels et d'influences modernes populaire dans la région du Centre.",
            },
            {
                "name": "Assiko",
                "is_traditional": True,
                "description": "Rythme ancestral des peuples côtiers du Cameroun (Douala), caractérisé par des percussions rapides et des danses énergiques. Traditionnellement joué lors des cérémonies importantes.",
            },
            {
                "name": "Bend-skin",
                "is_traditional": True,
                "description": "Rythme et danse des Bamilékés de l'Ouest-Cameroun, caractérisé par une posture penchée ('bend') et des mouvements rapides des hanches. Très populaire dans les fêtes.",
            },
            {
                "name": "Bikutsi",
                "is_traditional": True,
                "description": "Musique et danse Beti du Centre-Cameroun, basée sur un rythme ternaire (6/8) hypnotique. Traditionnellement joué lors des cérémonies rituelles et popularisé par les femmes.",
            },
            {
                "name": "Bolobo",
                "is_traditional": True,
                "description": "Musique traditionnelle du peuple Douala, jouée avec des tambours et des instruments à cordes lors des cérémonies de mariage et d'initiation.",
            },
            {
                "name": "Essewe",
                "is_traditional": True,
                "description": "Rythme traditionnel du peuple Bassa, caractérisé par l'utilisation de percussions complexes et de chants polyphoniques lors des rites de passage.",
            },
            {
                "name": "Makossa",
                "is_traditional": True,
                "description": "Rythme urbain né à Douala en 1958, joué en 12/8. Popularisé mondialement par Manu Dibango avec 'Soul Makossa'. Fusion parfaite de rythmes traditionnels et influences jazz.",
            },
            {
                "name": "Mangambeu",
                "is_traditional": True,
                "description": "Genre musical traditionnel Bangangté (Ouest-Cameroun), caractérisé par des percussions complexes et des danses acrobatiques lors des festivités royales.",
            },
            {
                "name": "Mbole",
                "is_traditional": True,
                "description": "Style musical traditionnel basé sur le tambour Mbole, instrument sacré des peuples du Centre et de l'Est-Cameroun. Rythmes cérémoniels accompagnant les rites de passage et communications ancestrales.",
            },
            {
                "name": "Mewoup",
                "is_traditional": True,
                "description": "Musique traditionnelle Bamiléké jouée lors des funérailles et cérémonies importantes, accompagnée de lamentations rituelles et danses sacrées.",
            },
            {
                "name": "Njang",
                "is_traditional": True,
                "description": "Genre musical traditionnel du peuple Beti, spécialement joué lors des rites d'initiation et accompagnant les récits ancestraux.",
            },
            {
                "name": "Tchamassi",
                "is_traditional": True,
                "description": "Musique et danse traditionnelle Bamiléké de la région de Bafoussam, caractérisée par des mouvements de tête rythmés et des costumes colorés.",
            },
            # Genres modernes camerounais et africains
            {
                "name": "Afrobeat",
                "is_traditional": False,
                "description": "Fusion de musiques traditionnelles africaines, jazz, funk et highlife créée par Fela Kuti. Très présent dans la scène camerounaise avec des artistes comme Blick Bassy.",
            },
            {
                "name": "Afro-fusion",
                "is_traditional": False,
                "description": "Mélange contemporain de styles africains traditionnels avec des influences internationales (R&B, pop, électro). Style adopté par de nombreux artistes camerounais modernes.",
            },
            {
                "name": "Afropop",
                "is_traditional": False,
                "description": "Pop africaine moderne mélangeant rythmes traditionnels et production contemporaine. Genre populaire chez les jeunes artistes camerounais urbains.",
            },
            {
                "name": "Afro-trap",
                "is_traditional": False,
                "description": "Fusion moderne entre trap américaine et sonorités africaines, très populaire chez les jeunes. Représenté par des artistes comme Tenor au Cameroun.",
            },
            {
                "name": "Amapiano",
                "is_traditional": False,
                "description": "Genre sud-africain mélant deep house, jazz et percussions africaines, en pleine expansion au Cameroun via les DJ et producteurs locaux.",
            },
            {
                "name": "Bantou Jazz",
                "is_traditional": False,
                "description": "Jazz africain incorporant des éléments traditionnels bantous et des instruments locaux. Développé par des musiciens comme Manu Dibango.",
            },
            {
                "name": "Coupé-Décalé",
                "is_traditional": False,
                "description": "Genre ivoirien très populaire en Afrique centrale, caractérisé par des rythmes dansants et festifs. Très présent dans les clubs de Douala et Yaoundé.",
            },
            {
                "name": "Gospel Camerounais",
                "is_traditional": False,
                "description": "Musique chrétienne camerounaise mélangeant louange occidentale et rythmes locaux (bikutsi gospel, makossa gospel). Très populaire dans les églises.",
            },
            {
                "name": "Highlife",
                "is_traditional": False,
                "description": "Genre d'Afrique de l'Ouest mélangeant instruments traditionnels et guitares jazz. Influencé le développement du makossa au Cameroun.",
            },
            {
                "name": "Hip-Hop Camerounais",
                "is_traditional": False,
                "description": "Rap camerounais souvent en français, anglais et langues locales (ewondo, duala, bamiléké), abordant des thèmes sociaux et culturels camerounais.",
            },
            {
                "name": "Mbalax",
                "is_traditional": False,
                "description": "Style sénégalais popularisé par Youssou N'Dour, influençant la scène camerounaise avec ses percussions sabar et ses rythmes entraînants.",
            },
            {
                "name": "Ndombolo",
                "is_traditional": False,
                "description": "Variante moderne de la rumba congolaise, très dansante et populaire en Afrique centrale. Incontournable dans les soirées camerounaises.",
            },
            {
                "name": "Rumba Camerounaise",
                "is_traditional": False,
                "description": "Adaptation camerounaise de la rumba congolaise avec des influences locales makossa et bikutsi, créant un style unique.",
            },
            {
                "name": "Soukous",
                "is_traditional": False,
                "description": "Évolution moderne de la rumba congolaise, caractérisée par des guitares rapides et virtuoses. Populaire dans toute l'Afrique centrale.",
            },
            # Genres internationaux populaires au Cameroun
            {
                "name": "Blues",
                "is_traditional": False,
                "description": "Genre musical afro-américain aux racines africaines, apprécié par les musiciens camerounais pour ses liens avec les traditions musicales ancestrales.",
            },
            {
                "name": "Dancehall",
                "is_traditional": False,
                "description": "Dérivé du reggae jamaïcain, populaire chez les jeunes camerounais et souvent fusionné avec des rythmes locaux.",
            },
            {
                "name": "Funk",
                "is_traditional": False,
                "description": "Genre groove afro-américain qui a influencé le développement du makossa et d'autres styles camerounais modernes.",
            },
            {
                "name": "Jazz",
                "is_traditional": False,
                "description": "Musique afro-américaine qui a fortement influencé les musiciens camerounais comme Manu Dibango, créant le jazz africain.",
            },
            {
                "name": "R&B",
                "is_traditional": False,
                "description": "Rhythm and Blues moderne, populaire chez les artistes camerounais urbains qui l'adaptent avec des touches locales.",
            },
            {
                "name": "Reggae",
                "is_traditional": False,
                "description": "Musique jamaïcaine appréciée au Cameroun, souvent utilisée pour des messages sociaux et spirituels en langues locales.",
            },
            {
                "name": "Soul",
                "is_traditional": False,
                "description": "Musique soul afro-américaine qui résonne avec les traditions vocales camerounaises et influence de nombreux chanteurs locaux.",
            },
            {
                "name": "Zouk",
                "is_traditional": False,
                "description": "Musique des Antilles françaises très populaire au Cameroun, souvent adaptée avec des rythmes makossa ou bikutsi.",
            },
        ]

        # Tri alphabétique
        genres_data.sort(key=lambda x: x["name"])

        for genre_data in genres_data:
            genre = MusicGenre.objects.create(
                name=genre_data["name"],
                description=genre_data["description"],
                is_traditional=genre_data["is_traditional"],
                is_active=True,
            )
            status = "🆕" if genre_data["is_traditional"] else "🌍"
            self.stdout.write(f"  {status} Genre créé: {genre.name}")

    def create_artist_roles(self):
        """Crée les rôles/spécialités d'artistes avec contexte culturel camerounais"""

        self.stdout.write("\n🎭 Création des rôles d'artistes...")

        roles_data = [
            # Rôles traditionnels camerounais
            (
                "Assikoiste",
                "Interprète spécialisé de l'Assiko, maîtrisant les percussions rapides et danses traditionnelles du peuple Douala",
            ),
            (
                "Auteur-compositeur-interprète",
                "Artiste complet qui écrit, compose et interprète ses propres chansons, souvent en langues locales",
            ),
            (
                "Bend-skiniste",
                "Spécialiste du Bend-skin, expert des danses et rythmes Bamiléké avec la posture caractéristique penchée",
            ),
            (
                "Bikutsiste",
                "Performeur du Bikutsi, maîtrisant le rythme 6/8 hypnotique et les danses traditionnelles du peuple Beti",
            ),
            # Chanteurs spécialisés par régions/langues
            (
                "Chanteur en langue Bassa",
                "Interprète spécialisé dans les chants en langue Bassa, gardien des traditions musicales de cette ethnie",
            ),
            (
                "Chanteur en langue Beti",
                "Interprète spécialisé dans les chants en langues Beti (Ewondo, Bulu, Eton), souvent bikutsi traditionnel",
            ),
            (
                "Chanteur en langue Bamiléké",
                "Interprète spécialisé dans les chants en langues de l'Ouest (Ghomálá, Fe'fe', Medumba, etc.)",
            ),
            (
                "Chanteur en langue Douala",
                "Interprète spécialisé dans les chants en langue Douala, souvent accompagnés de makossa",
            ),
            (
                "Chanteur en langue Fulfuldé",
                "Interprète spécialisé dans les chants en Fulfuldé, musique des bergers Peuls du Nord-Cameroun",
            ),
            (
                "Chanteur Gospel",
                "Artiste spécialisé dans la musique chrétienne camerounaise, mélangeant louange et rythmes locaux",
            ),
            (
                "Chanteur principal",
                "Lead vocal d'un groupe ou artiste solo principal, voix principale de l'ensemble musical",
            ),
            (
                "Chanteur traditionnel",
                "Gardien des chants ancestraux et rituels camerounais, transmetteur de la culture orale",
            ),
            (
                "Choriste",
                "Chanteur d'accompagnement expert en harmonies vocales, soutien essentiel aux chanteurs principaux",
            ),
            (
                "Griot moderne",
                "Conteur musical contemporain, gardien de l'histoire orale et des traditions musicales africaines",
            ),
            # Musiciens instrumentistes
            (
                "Balafonniste",
                "Maître du balafon, xylophone traditionnel africain en bois avec calebasses résonateurs, instrument sacré",
            ),
            (
                "Bassiste",
                "Joueur de guitare basse, fondation rythmique moderne des groupes de makossa, afrobeat et autres styles",
            ),
            (
                "Batteur",
                "Percussionniste spécialisé dans la batterie moderne, adaptant souvent les rythmes traditionnels camerounais",
            ),
            (
                "Claviériste",
                "Joueur de claviers, piano et synthétiseurs, souvent responsable des mélodies dans la musique moderne",
            ),
            (
                "Guitariste",
                "Joueur de guitare acoustique ou électrique, instrument central du makossa et de l'afrobeat camerounais",
            ),
            (
                "Mvetiste",
                "Maître du Mvett, harpe-cithare traditionnelle sacrée des peuples Fang/Beti, accompagnant les épopées",
            ),
            (
                "Percussionniste traditionnel",
                "Expert des tambours et instruments à percussion africains (djembé, tam-tam, talking drums)",
            ),
            (
                "Saxophoniste",
                "Joueur de saxophone, très présent dans l'afro-jazz camerounais et le makossa moderne",
            ),
            (
                "Tam-tamiste",
                "Maître des tam-tams et communications rythmiques traditionnelles, gardien des langages tambourinés",
            ),
            (
                "Trompettiste",
                "Joueur de trompette et cuivres africains, souvent présent dans les fanfares et orchestres modernes",
            ),
            # Danseurs spécialisés
            (
                "Danseur Assiko",
                "Spécialiste des danses rapides et acrobatiques Assiko, performances énergiques du peuple côtier",
            ),
            (
                "Danseur Bikutsi",
                "Expert des mouvements caractéristiques du Bikutsi, danses sensuelles et rythmées du peuple Beti",
            ),
            (
                "Danseur traditionnel",
                "Gardien des danses rituelles et cérémonielles camerounaises, performeur des traditions ancestrales",
            ),
            (
                "Danseur urbain",
                "Spécialiste des danses modernes et urbaines africaines (coupé-décalé, ndombolo, afro-dance)",
            ),
            # Professionnels de la production
            (
                "Arrangeur musical",
                "Créateur d'arrangements musicaux, spécialisé dans l'adaptation des morceaux traditionnels en versions modernes",
            ),
            (
                "Beatmaker",
                "Producteur de rythmes et instrumentales modernes, créateur de beats afro-trap et afrobeat",
            ),
            (
                "Chef d'orchestre",
                "Directeur d'ensemble musical ou orchestre, coordinateur des performances collectives",
            ),
            (
                "Chef de chœur",
                "Directeur de chorale, expert en direction vocale et harmonies, très présent dans les églises",
            ),
            (
                "Compositeur",
                "Créateur de mélodies et structures musicales, souvent puisant dans les gammes traditionnelles africaines",
            ),
            (
                "DJ",
                "Disc-jockey, animateur et mixeur de musique, spécialisé dans les sons africains et internationaux",
            ),
            (
                "Ingénieur du son",
                "Expert technique de l'enregistrement et du mixage, maîtrisant les sonorités africaines spécifiques",
            ),
            (
                "Parolier",
                "Auteur de textes et paroles de chansons, souvent bilingue ou trilingue (français, anglais, langues locales)",
            ),
            (
                "Producteur musical",
                "Responsable de la production et réalisation d'albums, développeur de nouveaux talents camerounais",
            ),
            # Rôles modernes spécialisés
            (
                "Beatboxer",
                "Artiste de percussion vocale, intégrant souvent des rythmes traditionnels camerounais dans ses performances",
            ),
            (
                "Chanteur de chorale",
                "Membre de chorale spécialisé dans le chant harmonique en groupe, très présent dans les églises",
            ),
            (
                "DJ Afrobeat",
                "DJ spécialisé dans les sonorités afrobeat et afro-fusion, promoteur de la musique africaine moderne",
            ),
            (
                "MC/Animateur",
                "Maître de cérémonie et animateur d'événements, souvent bilingue français-anglais et connaisseur de la culture locale",
            ),
            (
                "Multi-instrumentiste",
                "Musicien maîtrisant plusieurs instruments traditionnels et modernes, polyvalence musicale",
            ),
            (
                "Rappeur/Rappeuse",
                "Artiste hip-hop camerounais, expert du flow en français, anglais et langues locales (ewondo, duala, etc.)",
            ),
            (
                "Slammeur",
                "Artiste de slam et poésie orale, moderne héritier de la tradition griotte africaine",
            ),
            (
                "Styliste musical",
                "Professionnel de l'image musicale, spécialisé dans les looks afro-contemporains et traditionnels revisités",
            ),
            (
                "VJ (Video Jockey)",
                "Artiste visuel et vidéo accompagnant les performances musicales, créateur de contenus visuels afro-modernes",
            ),
        ]

        # Tri alphabétique
        roles_data.sort(key=lambda x: x[0])

        for name, description in roles_data:
            role = ArtistRole.objects.create(
                name=name, description=description, is_active=True
            )
            icon = "🎭" if "traditionnel" in description.lower() else "🎤"
            self.stdout.write(f"  {icon} Rôle créé: {name}")

    def create_instruments(self):
        """Crée les instruments avec classification par famille et contexte culturel"""

        self.stdout.write("\n🎸 Création des instruments par famille...")

        instruments_data = {
            "Cordes traditionnelles": [
                (
                    "Harpe arquée",
                    "traditional",
                    "Harpe traditionnelle camerounaise à forme courbée, utilisée par les griots pour accompagner les récits",
                ),
                (
                    "Harpe-luth Sawa",
                    "traditional",
                    "Instrument à cordes des peuples côtiers (Sawa), mélange unique de harpe et luth pour les cérémonies",
                ),
                (
                    "Mvet",
                    "traditional",
                    "Harpe-cithare sacrée des peuples Fang/Beti avec résonateurs multiples, accompagne les épopées traditionnelles",
                ),
                (
                    "Nkuu",
                    "traditional",
                    "Luth traditionnel à une corde des Grassfields de l'Ouest-Cameroun, instrument mélodique pastoral",
                ),
            ],
            "Cordes modernes": [
                (
                    "Banjo",
                    "modern",
                    "Instrument à cordes pincées d'origine africaine-américaine, retour aux sources pour les musiciens camerounais",
                ),
                (
                    "Contrebasse",
                    "modern",
                    "Plus grande des cordes frottées, base harmonique des ensembles de jazz et afrobeat",
                ),
                (
                    "Guitare acoustique",
                    "modern",
                    "Guitare classique ou folk non amplifiée, base du makossa acoustique et de la chanson camerounaise",
                ),
                (
                    "Guitare basse",
                    "modern",
                    "Guitare électrique grave à 4-6 cordes, fondation rythmique du makossa moderne et de l'afrobeat",
                ),
                (
                    "Guitare électrique",
                    "modern",
                    "Guitare amplifiée électroniquement, star du makossa électrique et de l'afro-rock camerounais",
                ),
                (
                    "Harpe classique",
                    "modern",
                    "Grande harpe de concert occidentale, parfois utilisée dans les arrangements afro-classiques",
                ),
                (
                    "Mandoline",
                    "modern",
                    "Petit instrument à cordes doubles pincées, apprécié dans la musique folklorique camerounaise",
                ),
                (
                    "Ukulélé",
                    "modern",
                    "Petite guitare hawaïenne à 4 cordes, instrument accessible pour l'initiation musicale",
                ),
                (
                    "Violon",
                    "modern",
                    "Instrument à cordes frottées aigu, présent dans les orchestres afro-classiques et arrangements modernes",
                ),
                (
                    "Violoncelle",
                    "modern",
                    "Instrument à cordes frottées grave, enrichit les arrangements dans la musique camerounaise contemporaine",
                ),
            ],
            "Vents traditionnels": [
                (
                    "Algaita",
                    "traditional",
                    "Hautbois double anche du Nord-Cameroun, utilisé dans les cérémonies royales et festivités Peules",
                ),
                (
                    "Corne d'antilope",
                    "traditional",
                    "Instrument de communication et rituel fait de corne animale, signalisation traditionnelle",
                ),
                (
                    "Flûte en bambou",
                    "traditional",
                    "Flûte traversière traditionnelle en bambou, instrument pastoral des bergers des hauts plateaux",
                ),
                (
                    "Flûte peule",
                    "traditional",
                    "Flûte traditionnelle des bergers Peuls du Nord, accompagne les chants pastoraux et la méditation",
                ),
                (
                    "Kakaki",
                    "traditional",
                    "Longue trompette royale de cérémonie (3-4 mètres), instrument de prestige des royaumes du Nord",
                ),
                (
                    "Sifflet rituel",
                    "traditional",
                    "Petit instrument pour les cérémonies et communications, signaux sonores traditionnels",
                ),
            ],
            "Vents modernes": [
                (
                    "Clarinette",
                    "modern",
                    "Instrument à anche simple, présent dans les orchestres camerounais et arrangements jazz-afro",
                ),
                (
                    "Flûte traversière",
                    "modern",
                    "Flûte moderne en métal, apporte une couleur aérienne aux compositions afro-contemporaines",
                ),
                (
                    "Harmonica",
                    "modern",
                    "Instrument à anches libres portatif, blues africain et musique de rue camerounaise",
                ),
                (
                    "Hautbois",
                    "modern",
                    "Instrument à double anche, couleur spéciale dans les arrangements orchestraux afro-classiques",
                ),
                (
                    "Saxophone alto",
                    "modern",
                    "Saxophone de tessiture moyenne, voix emblématique du jazz africain et du makossa sophistiqué",
                ),
                (
                    "Saxophone soprano",
                    "modern",
                    "Saxophone aigu, sonorité perçante caractéristique du style Manu Dibango",
                ),
                (
                    "Saxophone ténor",
                    "modern",
                    "Saxophone grave populaire en jazz africain, instrument phare de l'afrobeat et du makossa",
                ),
                (
                    "Trombone",
                    "modern",
                    "Cuivre à coulisse, présent dans les fanfares camerounaises et orchestres de danse",
                ),
                (
                    "Trompette",
                    "modern",
                    "Cuivre à pistons, lead des sections de cuivres dans le makossa et les fanfares traditionnelles",
                ),
                (
                    "Tuba",
                    "modern",
                    "Plus grave des cuivres, base harmonique des fanfares et orchestres de musique populaire",
                ),
            ],
            "Percussions sacrées": [
                (
                    "Balafon",
                    "traditional",
                    "Xylophone sacré en bois avec calebasses résonateurs, instrument royal et cérémoniel majeur",
                ),
                (
                    "Bendré",
                    "traditional",
                    "Tambour sacré des royaumes du Nord, réservé aux cérémonies royales et rituels importants",
                ),
                (
                    "Djembé",
                    "traditional",
                    "Tambour en forme de calice d'Afrique de l'Ouest, adopté par de nombreuses ethnies camerounaises",
                ),
                (
                    "Tam-tam royal",
                    "traditional",
                    "Grand tambour de communication royale, annonciateur des événements majeurs du royaume",
                ),
                (
                    "Tambour parlant",
                    "traditional",
                    "Tambour en sablier (talking drum) reproduisant les tonalités des langues camerounaises",
                ),
            ],
            "Percussions traditionnelles": [
                (
                    "Dum-dum",
                    "traditional",
                    "Tambour à deux peaux caractéristique du makossa traditionnel, rythme de base incontournable",
                ),
                (
                    "Konga",
                    "traditional",
                    "Tambour cylindrique des cérémonies Beti, accompagne le bikutsi et les rites de passage",
                ),
                (
                    "Maracas traditionnelles",
                    "traditional",
                    "Hochets en calebasse avec graines, rythme d'accompagnement des chants et danses",
                ),
                (
                    "Mbole",
                    "traditional",
                    "Tambour traditionnel sacré des peuples du Centre et de l'Est-Cameroun, utilisé pour les cérémonies rituelles et communications ancestrales",
                ),
                (
                    "Nding",
                    "traditional",
                    "Xylophone traditionnel Bamiléké des hauts plateaux de l'Ouest, mélodie des fêtes villageoises",
                ),
                (
                    "Ndong-mo-ba",
                    "traditional",
                    "Tambour parlant des communications traditionnelles, langage musical des ancêtres",
                ),
                (
                    "Tam-tam",
                    "traditional",
                    "Terme générique pour les grands tambours de communication inter-villages",
                ),
            ],
            "Percussions modernes": [
                (
                    "Batterie complète",
                    "modern",
                    "Kit de batterie moderne adapté aux rythmes camerounais (makossa, bikutsi, afrobeat)",
                ),
                (
                    "Bongos",
                    "modern",
                    "Paire de petits tambours cubains, parfaits pour les rythmes afro-latins et salsa africaine",
                ),
                (
                    "Cajon",
                    "modern",
                    "Caisse de percussion péruvienne, instrument compact pour sessions acoustiques et street music",
                ),
                (
                    "Cloches",
                    "modern",
                    "Cloches métalliques diverses (cowbell, etc.), marquage rythmique essentiel du makossa",
                ),
                (
                    "Congas",
                    "modern",
                    "Tambours afro-cubains, pont entre traditions africaines et influences latines",
                ),
                (
                    "Cymbales",
                    "modern",
                    "Disques métalliques pour la batterie, effets et accentuations dans la musique moderne",
                ),
                (
                    "Gong",
                    "modern",
                    "Large disque métallique suspendu, effets dramatiques dans les compositions afro-contemporaines",
                ),
                (
                    "Shaker",
                    "modern",
                    "Instrument secoué moderne, équivalent contemporain des maracas traditionnelles",
                ),
                (
                    "Tambourin",
                    "modern",
                    "Cadre avec cymbalettes, accompagnement rythmique léger pour chants et danses",
                ),
                (
                    "Triangle",
                    "modern",
                    "Tige métallique triangulaire, accent cristallin dans les arrangements afro-orchestraux",
                ),
            ],
            "Claviers et harmoniques": [
                (
                    "Accordéon",
                    "modern",
                    "Instrument à soufflet et touches, populaire dans la musique folklorique des hauts plateaux",
                ),
                (
                    "Clavier MIDI",
                    "modern",
                    "Contrôleur électronique pour sons numériques, création de beats afrobeat et afro-trap modernes",
                ),
                (
                    "Kalimba",
                    "traditional",
                    "Piano à pouces africain (sanza), instrument de méditation et accompagnement mélodique doux",
                ),
                (
                    "Orgue électronique",
                    "modern",
                    "Orgue avec sons électroniques, pilier de la musique gospel camerounaise contemporaine",
                ),
                (
                    "Piano acoustique",
                    "modern",
                    "Piano traditionnel à cordes frappées, base harmonique du jazz africain et de la chanson",
                ),
                (
                    "Piano électrique",
                    "modern",
                    "Piano avec amplification électrique, couleur vintage du makossa électrique des années 80",
                ),
                (
                    "Sanza",
                    "traditional",
                    "Lamellophone traditionnel africain, instrument contemplatif des soirées et récits",
                ),
                (
                    "Synthétiseur",
                    "modern",
                    "Générateur électronique de sons, création des sonorités afrofuturistes et afrobeat moderne",
                ),
            ],
            "Instruments électroniques": [
                (
                    "Boîte à rythmes",
                    "modern",
                    "Machine électronique de percussions, production de beats afrobeat, afro-trap et makossa moderne",
                ),
                (
                    "Sampler",
                    "modern",
                    "Échantillonneur numérique, intégration des sons traditionnels dans la production moderne",
                ),
                (
                    "Turntables",
                    "modern",
                    "Platines DJ pour le scratch et mixage, promotion de la musique africaine en clubs et radios",
                ),
            ],
        }

        for category, instruments in instruments_data.items():
            self.stdout.write(f"\n  📂 {category}:")

            # Tri alphabétique dans chaque catégorie
            instruments.sort(key=lambda x: x[0])

            for name, inst_category, description in instruments:
                instrument = Instrument.objects.create(
                    name=name,
                    category=inst_category,
                    description=description,
                    is_active=True,
                )
                icon = "🥁" if inst_category == "traditional" else "🎹"
                self.stdout.write(f"    {icon} {name}")
