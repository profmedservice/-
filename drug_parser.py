import re
import pandas as pd

def better_parse_drug_name(name, form_terms, dose_units):
    """Parse drug name into PURE, DOSE, PACK and FORMS."""
    name_up = name.upper()

    # dosage pattern accepts decimals and slash-separated fractions
    dose_pattern = r"(\d+(?:[\/.,]\d+)*\s*(%s))" % "|".join(dose_units)
    dose_match = re.search(dose_pattern, name_up)
    dose = dose_match.group(0).replace(" ", "") if dose_match else ""

    pack_pattern = r"(\d+\s?(%s))" % "|".join(form_terms)
    pack_match = re.search(pack_pattern, name_up)
    pack = pack_match.group(0).replace(" ", "") if pack_match else ""

    # use original string when extracting forms so that pack form also appears
    form_pattern = r"\b(" + "|".join(form_terms) + r")\b"
    forms = " ".join(re.findall(form_pattern, name_up))

    tmp = name_up
    for to_remove in [dose_match.group(0) if dose_match else "",
                      pack_match.group(0) if pack_match else ""] + forms.split():
        if to_remove:
            tmp = re.sub(r"\b{}\b".format(re.escape(to_remove)), "", tmp)
    pure = re.sub(r"\s+", " ", tmp).strip()

    return pd.Series([pure, dose, pack, forms])
