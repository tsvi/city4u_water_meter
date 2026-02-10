"""Municipality data for City4U integration.

This list contains municipalities verified to have water consumption support.
Verification checks for water menu in the portal page.

To update this list, run:
    python3 scripts/update_municipalities.py

Last updated: 2026-02-10
Total municipalities: 77
"""

from dataclasses import dataclass
from enum import IntEnum


class City4uID(IntEnum):
    """City4U customer IDs for municipalities with water consumption support."""

    ID_999999 = 999999  # onecity
    ID_524000 = 524000  # אור יהודה
    ID_510200 = 510200  # אור עקיבא
    ID_600410 = 600410  # אליכין
    ID_813090 = 813090  # אלעד
    ID_835600 = 835600  # אלקנה
    ID_51240 = 51240  # אפעל
    ID_836500 = 836500  # אפרת
    ID_390000 = 390000  # באר שבע
    ID_537800 = 537800  # ביתר עילית
    ID_261000 = 261000  # בני ברק
    ID_62410 = 62410  # בני שמעון
    ID_698000 = 698000  # בנימינה-גבעת עדה
    ID_262000 = 262000  # בת ים
    ID_807300 = 807300  # גבעת זאב
    ID_837300 = 837300  # גבעת זאב - חינוך
    ID_43300 = 43300  # גזר
    ID_904890 = 904890  # דבוריה
    ID_322000 = 322000  # דימונה
    ID_42200 = 42200  # דרום השרון
    ID_62540 = 62540  # הערבה התיכונה
    ID_264000 = 264000  # הרצליה
    ID_42250 = 42250  # חבל מודיעין
    ID_32150 = 32150  # חוף הכרמל
    ID_913030 = 913030  # חורה
    ID_904960 = 904960  # חורפיש
    ID_520340 = 520340  # חצור הגלילית
    ID_812470 = 812470  # חריש
    ID_521000 = 521000  # טירת כרמל
    ID_594000 = 594000  # יהוד - מונוסון
    ID_904990 = 904990  # יפיע
    ID_602400 = 602400  # יקנעם
    ID_906540 = 906540  # כפר קרע
    ID_800470 = 800470  # כפר תבור
    ID_712710 = 712710  # להבים
    ID_370000 = 370000  # לוד
    ID_510150 = 510150  # מבשרת ציון
    ID_23130 = 23130  # מגידו
    ID_905170 = 905170  # מזרעה
    ID_700430 = 700430  # מטולה
    ID_697100 = 697100  # מי הוד השרון
    ID_264100 = 264100  # מי הרצליה
    ID_140100 = 140100  # מי כרמל
    ID_812100 = 812100  # מי מודיעין
    ID_927150 = 927150  # מי עירון
    ID_474050 = 474050  # מי ציונה- מזכרת בתיה
    ID_472050 = 472050  # מי ציונה- נס ציונה
    ID_473050 = 473050  # מי ציונה- קריית עקרון
    ID_367700 = 367700  # מי רקת
    ID_712680 = 712680  # מיתר
    ID_712730 = 712730  # מכבים רעות
    ID_880300 = 880300  # מעיינות העמקים
    ID_836160 = 836160  # מעלה אדומים
    ID_269100 = 269100  # מפעל המים כפר סבא
    ID_500990 = 500990  # מצפה רמון
    ID_2000 = 2000  # מרכז מסחרי שהם
    ID_24560 = 24560  # משגב
    ID_502460 = 502460  # נתיבות
    ID_705870 = 705870  # סביון
    ID_975000 = 975000  # סח'נין
    ID_905300 = 905300  # עילבון
    ID_22060 = 22060  # עמק הירדן
    ID_377000 = 377000  # עפולה
    ID_906370 = 906370  # ערערה
    ID_600530 = 600530  # עתלית
    ID_801710 = 801710  # פרדסיה
    ID_813080 = 813080  # צורן
    ID_835570 = 835570  # קדומים
    ID_841000 = 841000  # קצרין
    ID_426200 = 426200  # קרית אונו
    ID_395000 = 395000  # קרית ביאליק
    ID_326310 = 326310  # קרית גת ? מרכז מריאן
    ID_284000 = 284000  # רחובות
    ID_801220 = 801220  # רמת ישי
    ID_61340 = 61340  # שפיר
    ID_150000 = 150000  # תל אביב
    ID_989000 = 989000  # תמרה


@dataclass
class Municipality:
    """Represents a municipality in the City4U system."""

    customer_id: City4uID
    name_he: str
    logo_url: str | None = None


# Verified municipalities with water consumption support
MUNICIPALITIES = [
    Municipality(
        customer_id=City4uID.ID_999999,
        name_he="onecity",
        logo_url="logos/999999.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_524000,
        name_he="אור יהודה",
        logo_url="logos/524000.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_510200,
        name_he="אור עקיבא",
        logo_url="logos/510200.png",
    ),
    Municipality(
        customer_id=City4uID.ID_600410,
        name_he="אליכין",
        logo_url="logos/600410.png",
    ),
    Municipality(
        customer_id=City4uID.ID_813090,
        name_he="אלעד",
        logo_url="logos/813090.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_835600,
        name_he="אלקנה",
    ),
    Municipality(
        customer_id=City4uID.ID_51240,
        name_he="אפעל",
    ),
    Municipality(
        customer_id=City4uID.ID_836500,
        name_he="אפרת",
    ),
    Municipality(
        customer_id=City4uID.ID_390000,
        name_he="באר שבע",
        logo_url="logos/390000.png",
    ),
    Municipality(
        customer_id=City4uID.ID_537800,
        name_he="ביתר עילית",
    ),
    Municipality(
        customer_id=City4uID.ID_261000,
        name_he="בני ברק",
        logo_url="logos/261000.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_62410,
        name_he="בני שמעון",
    ),
    Municipality(
        customer_id=City4uID.ID_698000,
        name_he="בנימינה-גבעת עדה",
    ),
    Municipality(
        customer_id=City4uID.ID_262000,
        name_he="בת ים",
    ),
    Municipality(
        customer_id=City4uID.ID_807300,
        name_he="גבעת זאב",
        logo_url="logos/807300.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_837300,
        name_he="גבעת זאב - חינוך",
        logo_url="logos/837300.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_43300,
        name_he="גזר",
    ),
    Municipality(
        customer_id=City4uID.ID_904890,
        name_he="דבוריה",
        logo_url="logos/904890.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_322000,
        name_he="דימונה",
        logo_url="logos/322000.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_42200,
        name_he="דרום השרון",
    ),
    Municipality(
        customer_id=City4uID.ID_62540,
        name_he="הערבה התיכונה",
    ),
    Municipality(
        customer_id=City4uID.ID_264000,
        name_he="הרצליה",
        logo_url="logos/264000.png",
    ),
    Municipality(
        customer_id=City4uID.ID_42250,
        name_he="חבל מודיעין",
        logo_url="logos/42250.png",
    ),
    Municipality(
        customer_id=City4uID.ID_32150,
        name_he="חוף הכרמל",
    ),
    Municipality(
        customer_id=City4uID.ID_913030,
        name_he="חורה",
    ),
    Municipality(
        customer_id=City4uID.ID_904960,
        name_he="חורפיש",
        logo_url="logos/904960.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_520340,
        name_he="חצור הגלילית",
    ),
    Municipality(
        customer_id=City4uID.ID_812470,
        name_he="חריש",
        logo_url="logos/812470.png",
    ),
    Municipality(
        customer_id=City4uID.ID_521000,
        name_he="טירת כרמל",
        logo_url="logos/521000.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_594000,
        name_he="יהוד - מונוסון",
        logo_url="logos/594000.png",
    ),
    Municipality(
        customer_id=City4uID.ID_904990,
        name_he="יפיע",
    ),
    Municipality(
        customer_id=City4uID.ID_602400,
        name_he="יקנעם",
        logo_url="logos/602400.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_906540,
        name_he="כפר קרע",
        logo_url="logos/906540.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_800470,
        name_he="כפר תבור",
        logo_url="logos/800470.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_712710,
        name_he="להבים",
    ),
    Municipality(
        customer_id=City4uID.ID_370000,
        name_he="לוד",
        logo_url="logos/370000.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_510150,
        name_he="מבשרת ציון",
        logo_url="logos/510150.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_23130,
        name_he="מגידו",
    ),
    Municipality(
        customer_id=City4uID.ID_905170,
        name_he="מזרעה",
        logo_url="logos/905170.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_700430,
        name_he="מטולה",
    ),
    Municipality(
        customer_id=City4uID.ID_697100,
        name_he="מי הוד השרון",
        logo_url="logos/697100.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_264100,
        name_he="מי הרצליה",
        logo_url="logos/264100.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_140100,
        name_he="מי כרמל",
        logo_url="logos/140100.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_812100,
        name_he="מי מודיעין",
        logo_url="logos/812100.gif",
    ),
    Municipality(
        customer_id=City4uID.ID_927150,
        name_he="מי עירון",
        logo_url="logos/927150.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_474050,
        name_he="מי ציונה- מזכרת בתיה",
        logo_url="logos/474050.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_472050,
        name_he="מי ציונה- נס ציונה",
        logo_url="logos/472050.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_473050,
        name_he="מי ציונה- קריית עקרון",
        logo_url="logos/473050.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_367700,
        name_he="מי רקת",
        logo_url="logos/367700.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_712680,
        name_he="מיתר",
        logo_url="logos/712680.png",
    ),
    Municipality(
        customer_id=City4uID.ID_712730,
        name_he="מכבים רעות",
    ),
    Municipality(
        customer_id=City4uID.ID_880300,
        name_he="מעיינות העמקים",
        logo_url="logos/880300.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_836160,
        name_he="מעלה אדומים",
    ),
    Municipality(
        customer_id=City4uID.ID_269100,
        name_he="מפעל המים כפר סבא",
        logo_url="logos/269100.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_500990,
        name_he="מצפה רמון",
    ),
    Municipality(
        customer_id=City4uID.ID_2000,
        name_he="מרכז מסחרי שהם",
        logo_url="logos/2000.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_24560,
        name_he="משגב",
    ),
    Municipality(
        customer_id=City4uID.ID_502460,
        name_he="נתיבות",
    ),
    Municipality(
        customer_id=City4uID.ID_705870,
        name_he="סביון",
        logo_url="logos/705870.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_975000,
        name_he="סח'נין",
        logo_url="logos/975000.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_905300,
        name_he="עילבון",
        logo_url="logos/905300.png",
    ),
    Municipality(
        customer_id=City4uID.ID_22060,
        name_he="עמק הירדן",
        logo_url="logos/22060.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_377000,
        name_he="עפולה",
    ),
    Municipality(
        customer_id=City4uID.ID_906370,
        name_he="ערערה",
        logo_url="logos/906370.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_600530,
        name_he="עתלית",
    ),
    Municipality(
        customer_id=City4uID.ID_801710,
        name_he="פרדסיה",
        logo_url="logos/801710.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_813080,
        name_he="צורן",
    ),
    Municipality(
        customer_id=City4uID.ID_835570,
        name_he="קדומים",
    ),
    Municipality(
        customer_id=City4uID.ID_841000,
        name_he="קצרין",
        logo_url="logos/841000.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_426200,
        name_he="קרית אונו",
        logo_url="logos/426200.png",
    ),
    Municipality(
        customer_id=City4uID.ID_395000,
        name_he="קרית ביאליק",
    ),
    Municipality(
        customer_id=City4uID.ID_326310,
        name_he="קרית גת ? מרכז מריאן",
        logo_url="logos/326310.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_284000,
        name_he="רחובות",
        logo_url="logos/284000.png",
    ),
    Municipality(
        customer_id=City4uID.ID_801220,
        name_he="רמת ישי",
        logo_url="logos/801220.jpg",
    ),
    Municipality(
        customer_id=City4uID.ID_61340,
        name_he="שפיר",
    ),
    Municipality(
        customer_id=City4uID.ID_150000,
        name_he="תל אביב",
    ),
    Municipality(
        customer_id=City4uID.ID_989000,
        name_he="תמרה",
        logo_url="logos/989000.png",
    ),
]


# Sorted lists for UI display
MUNICIPALITIES_SORTED_HE = sorted(MUNICIPALITIES, key=lambda m: m.name_he)


def get_municipality_by_id(customer_id: int) -> Municipality | None:
    """Get municipality by customer ID."""
    for muni in MUNICIPALITIES:
        if muni.customer_id == customer_id:
            return muni
    return None


def get_municipality_name(customer_id: int) -> str:
    """Get municipality name by customer ID."""
    muni = get_municipality_by_id(customer_id)
    if muni:
        return muni.name_he
    return f"Unknown ({customer_id})"
