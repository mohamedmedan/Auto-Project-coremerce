from tests.users.test_users import (
    Users001, Users002, Users003, Users004, Users005,
    Users006, Users007, Users008, Users009, Users010,
    Users011, Users012, Users013, Users014, Users015,
    Users016, Users017, Users018, Users019, Users020,
    Users021, Users022, Users023, Users024, Users025,
    Users026, Users027, Users028, Users029, Users030,
)
from tests.login.test_login import (
    Login001, Login002, Login003, Login004, Login005,
    Login006, Login007, Login008, Login009, Login010,
    Login011, Login012, Login013, Login014, Login015,
    Login016, Login017, Login018, Login019, Login020,
)
from tests.register.test_register import (
    Register001, Register002, Register003, Register004, Register005,
    Register006, Register007, Register008, Register009, Register010,
    Register011, Register012, Register013, Register014, Register015,
    Register016, Register017, Register018, Register019, Register020,
)
from tests.profile.test_profile import (
    Profile001, Profile002, Profile003, Profile004, Profile005,
    Profile006, Profile007, Profile008, Profile009, Profile010,
    Profile011, Profile012, Profile013, Profile014, Profile015,
    Profile016, Profile017, Profile018, Profile019, Profile020,
)


FEATURES = {
    "login": [
        Login001, Login002, Login003, Login004, Login005,
        Login006, Login007, Login008, Login009, Login010,
        Login011, Login012, Login013, Login014, Login015,
        Login016, Login017, Login018, Login019, Login020,
    ],
    "register": [
        Register001, Register002, Register003, Register004, Register005,
        Register006, Register007, Register008, Register009, Register010,
        Register011, Register012, Register013, Register014, Register015,
        Register016, Register017, Register018, Register019, Register020,
    ],
    "profile": [
        Profile001, Profile002, Profile003, Profile004, Profile005,
        Profile006, Profile007, Profile008, Profile009, Profile010,
        Profile011, Profile012, Profile013, Profile014, Profile015,
        Profile016, Profile017, Profile018, Profile019, Profile020,
    ],
    "users": [
        Users001, Users002, Users003, Users004, Users005,
        Users006, Users007, Users008, Users009, Users010,
        Users011, Users012, Users013, Users014, Users015,
        Users016, Users017, Users018, Users019, Users020,
        Users021, Users022, Users023, Users024, Users025,
        Users026, Users027, Users028, Users029, Users030,
    ],
}


def list_features():
    return list(FEATURES.keys())


def get_all_tests():
    return [c for lst in FEATURES.values() for c in lst]


def get_tests_by_feature(feature):
    feature = (feature or "all").lower()
    if feature == "all":
        return get_all_tests()
    return list(FEATURES.get(feature, []))


def get_tests_by_keys(keys, feature="all"):
    s = set(k.strip().upper() for k in keys if k.strip())
    return [c for c in get_tests_by_feature(feature) if c.key.upper() in s]