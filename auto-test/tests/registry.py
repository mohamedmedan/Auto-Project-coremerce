from tests.login.test_login import (
    Login001, Login002, Login003, Login004, Login005,
    Login006, Login007, Login008, Login009, Login010,
    Login011, Login012, Login013, Login014, Login015,
    Login016, Login017, Login018, Login019, Login020,
)
from tests.register.test_register import (
    Register001, Register002, Register003, Register004, Register005,
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
