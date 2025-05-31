import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from drug_parser import better_parse_drug_name

form_terms = ["TB", "FTB"]
dose_units = ["MG"]


def test_basic_case():
    result = better_parse_drug_name("BETASERC 16 MG 30 TB", form_terms, dose_units)
    pure, dose, pack, forms = result.tolist()
    assert pure == "BETASERC"
    assert dose == "16MG"
    assert pack == "30TB"
    assert forms == "TB"


def test_fractional_dose():
    result = better_parse_drug_name("TARKA 180/2 MG 28 FTB", form_terms, dose_units)
    pure, dose, pack, forms = result.tolist()
    assert pure == "TARKA"
    assert dose == "180/2MG"
    assert pack == "28FTB"
    assert forms == "FTB"


def test_unexpected_chars():
    result = better_parse_drug_name("BIZARREΩ 100 MG ??? 30 TB", form_terms, dose_units)
    pure, dose, pack, forms = result.tolist()
    assert pure.strip() == "BIZARREΩ ???".strip()
    assert dose == "100MG"
    assert pack == "30TB"
    assert forms == "TB"
