
# Manual downloaded objects
VIP_STARS = ["Eta Carinae"]

VIP_DSO = ["LMC", "Melotte 25", "Coalsack Nebula"]


STAR_CATALOG_RANKING = {
    '* ': 1,    # Bayer (phi Cas) and Flamsteed (34 Cas)
    'V* ': 2,   # Variable stars
    'HR ': 3,   # Bright Star Catalogue
    'HD ': 4,   # Henry Draper
    'HIP ': 5   # Hipparcos
}


DSO_CATALOG_RANKING = {
    'M ': 1, 'NGC ': 2, 'IC ': 3, 'UGC ': 4, 'PGC ': 5, '3C ': 6
}

TAGS = {
    'galaxy': ['G', 'Gx', 'GiG', 'GiC', 'AGN', 'Sy2', 'Galaxy', 'Seyfert', 'LINER', 'GinPair', 'LIN', 'SyG', 'GiP', 'SBG', 'H2G'],
    'open_cluster': ['OC', 'OpC', 'OpCl', 'Cl', 'C+N', 'Kt'],
    'globular_cluster': ['Gb', 'GlC', 'GlCl'],
    'galactic_cluster': [],
    'nebula': ['Nb', 'HII', 'Cld', 'RNe'],
    'molecular_cloud': ['MCl'],
    'planetary_nebula': ['Pl', 'PN'],
    'supernova_remmant': ['SNR', 'SR'],
    'asterism': ['Ast', 'As', 'As*', 'err'],
    'double_star': ['**', 'D*', 'D*?'],
    'star_system': ['Double', '***'],
    'star': ['Star', '*', '*?'],
    'unknown': ['?', '-']
}

# Unfold it to work better
OBJECT_TAGS = {
    alias: name
    for name, alias_list in TAGS.items()
    for alias in alias_list
}


IAU_CONSTELLATIONS = {
    "And": "Andromeda", "Ant": "Antlia", "Aps": "Apus", "Aqr": "Aquarius", "Aql": "Aquila", "Ara": "Ara", "Ari": "Aries", "Aur": "Auriga",
    "Boo": "Boötes", "Cae": "Caelum", "Cam": "Camelopardalis", "Cnc": "Cancer", "CVn": "Canes Venatici", "CMa": "Canis Major", "CMi": "Canis Minor", "Cap": "Capricornus",
    "Car": "Carina", "Cas": "Cassiopeia", "Cen": "Centaurus", "Cep": "Cepheus", "Cet": "Cetus", "Cha": "Chamaeleon", "Cir": "Circinus", "Col": "Columba",
    "Com": "Coma Berenices", "CrA": "Corona Australis", "CrB": "Corona Borealis", "Crv": "Corvus", "Crt": "Crater", "Cru": "Crux", "Cyg": "Cygnus", "Del": "Delphinus",
    "Dor": "Dorado", "Dra": "Draco", "Equ": "Equuleus", "Eri": "Eridanus", "For": "Fornax", "Gem": "Gemini", "Gru": "Grus", "Her": "Hercules",
    "Hor": "Horologium", "Hya": "Hydra", "Hyi": "Hydrus", "Ind": "Indus", "Lac": "Lacerta", "Leo": "Leo", "LMi": "Leo Minor", "Lep": "Lepus",
    "Lib": "Libra", "Lup": "Lupus", "Lyn": "Lynx", "Lyr": "Lyra", "Men": "Mensa", "Mic": "Microscopium", "Mon": "Monoceros", "Mus": "Musca",
    "Nor": "Norma", "Oct": "Octans", "Oph": "Ophiuchus", "Ori": "Orion", "Pav": "Pavo", "Peg": "Pegasus", "Per": "Perseus", "Phe": "Phoenix",
    "Pic": "Pictor", "Psc": "Pisces", "PsA": "Piscis Austrinus", "Pup": "Puppis", "Pyx": "Pyxis", "Ret": "Reticulum", "Sge": "Sagitta", "Sgr": "Sagittarius",
    "Sco": "Scorpius", "Scl": "Sculptor", "Sct": "Scutum", "Ser": "Serpens", "Sex": "Sextans", "Tau": "Taurus", "Tel": "Telescopium", "Tri": "Triangulum",
    "TrA": "Triangulum Australe", "Tuc": "Tucana", "UMa": "Ursa Major", "UMi": "Ursa Minor", "Vel": "Vela", "Vir": "Virgo", "Vol": "Volans", "Vul": "Vulpecula"
}

IMPORTANT_STAR_NAMES=[
        "Achernar", "Acrux", "Aldebaran", "Algenib", "Algol", "Alioth", "Alkaid", "Alnilam", 
        "Alnitak", "Alphard", "Alphecca", "Alpheratz", "Altair", "Antares", 
        "Arcturus", "Bellatrix", "Betelgeuse", "Canopus", "Capella", "Caph", 
        "Castor", "Deneb", "Denebola", "Dubhe", "Enif", "Fomalhaut", "Gacrux", 
        "Hadar", "Hamal", "Kochab", "Markab", "Megrez", "Merak", "Mimosa", 
        "Mintaka", "Mirach", "Mirfak", "Nunki", "Phecda", "Polaris", "Pollux", 
        "Procyon", "Regulus", "Rigel", "Saiph", "Schedar", "Shaula", "Sirius", 
        "Spica", "Thuban", "Vega"
    ]


# Official Vizier mirrors
VIZIER_MIRRORS = [
    'vizier.cds.unistra.fr',    # FR (Main)
    'vizier.ast.cam.ac.uk',     # UK
    'vizier.cfa.harvard.edu',   # US
    'vizier.nao.ac.jp'          # JP
]

# Official Simbad mirrors
SIMBAD_MIRRORS = [
    'http://simbad.cds.unistra.fr/simbad/sim-script', # FR (Main)
    'http://simbad.harvard.edu/simbad/sim-script'     # US
]

SIMBAD_VOTABLE_FIELDS=['ids', 'otype', 'V', 'B', 'dim', 'r']


