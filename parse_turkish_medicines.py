
#!/usr/bin/env python3
"""Parse Turkish medicine names into components.

This script implements the steps described in README.md. It expects a CSV file
with a column named "Название лекарства" and produces a new CSV with additional
columns:
    - "Название лекарства (чисто)"
    - "PURE"
    - "DOSE"
    - "PACK"
    - "FORMS"

Usage:
    python3 parse_turkish_medicines.py input.csv
The output will be saved next to the input file as ``parsed_<input>.csv``.
"""
import sys
import os
import re
import pandas as pd


def load_terms(filename):
    """Load list of terms from a text file, uppercase"""
    """Load terms from a text file, one per line."""
    with open(filename, encoding="utf-8") as f:
        return [line.strip().upper() for line in f if line.strip()]

def better_parse_drug_name(name, form_terms, dose_units):
    """Parse drug name into PURE, DOSE, PACK, FORMS"""
    name_up = name.upper()

    # 1) Dose: first occurrence of number + dose unit
def better_parse_drug_name(name: str, form_terms, dose_units):
    """Return Series(pure, dose, pack, forms) for the given name."""
    name_up = str(name).upper()

    # 1) first dose: number + unit from dose_units
    dose_pattern = r"(\d+(?:[\.,]\d+)?\s*(%s))" % "|".join(dose_units)
    dose_match = re.search(dose_pattern, name_up)
    dose = dose_match.group(0).replace(" ", "") if dose_match else ""

    # 2) Pack: first occurrence of number + form term
    # 2) first pack: number + form from form_terms
    pack_pattern = r"(\d+\s?(%s))" % "|".join(form_terms)
    pack_match = re.search(pack_pattern, name_up)
    pack = pack_match.group(0).replace(" ", "") if pack_match else ""

    # 3) Cut out found dose and pack for form detection
    # 3) remove dose and pack to find remaining forms
    name_cut = name_up
    if dose:
        name_cut = name_cut.replace(dose, "")
    if pack:
        name_cut = name_cut.replace(pack, "")

    # 4) Remaining form terms
    form_pattern = r"\b(" + "|".join(form_terms) + r")\b"
    forms = " ".join(re.findall(form_pattern, name_cut))

    # 5) Pure name: remove dose, pack and forms
    tmp = name_up
    for to_remove in [dose, pack] + forms.split():
        if to_remove:
            tmp = re.sub(r"\b{}\b".format(re.escape(to_remove)), "", tmp)
    pure = re.sub(r"\s+", " ", tmp.strip())
    # 4) all remaining forms
    form_pattern = r"\b(" + "|".join(form_terms) + r")\b"
    forms_list = re.findall(form_pattern, name_cut)
    forms = " ".join(forms_list)

    # 5) pure name: remove dose, pack and forms
    tmp = name_up
    for to_remove in [dose, pack] + forms_list:
        if to_remove:
            tmp = re.sub(r"\b{}\b".format(re.escape(to_remove)), "", tmp)
    pure = re.sub(r"\s+", " ", tmp).strip()
    return pd.Series([pure, dose, pack, forms])

def main():
    file_path = "турецкие лекарства 31_05_25 - WEBLISTE.csv"
    df = pd.read_csv(file_path, dtype=str, encoding="utf-8-sig")

    df['Название лекарства (чисто)'] = (
        df['Название лекарства']
        .astype(str)
        .str.replace(r"[.\*\s]+$", "", regex=True)
        .str.replace(r"^[-\s]+|[-\s]+$", "", regex=True)
    )

    form_terms = [x for x in load_terms("form_terms.txt") if x not in load_terms("dose_units.txt")]
    dose_units = load_terms("dose_units.txt")

    df[['PURE', 'DOSE', 'PACK', 'FORMS']] = df['Название лекарства (чисто)'].apply(
        lambda x: better_parse_drug_name(x, form_terms, dose_units)
    )

    df.to_csv("турецкие_лекарства_результат.csv", index=False, encoding="utf-8-sig")
    print("✅ Финальный файл сохранён как 'турецкие_лекарства_результат.csv'")

    # Save rows where PURE, DOSE or PACK are empty
    unparsed = df[(df['PURE'] == "") | (df['DOSE'] == "") | (df['PACK'] == "")]
    if not unparsed.empty:
        unparsed.to_csv("unparsed_rows.csv", index=False, encoding="utf-8-sig")
        print(f"⚠️ Сохранено {len(unparsed)} нераспарсенных строк в 'unparsed_rows.csv'")
    else:
        print("✅ Все строки успешно распарсены")


if __name__ == "__main__":
    main()
def main(path):
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")

    df["Название лекарства (чисто)"] = (
        df["Название лекарства"].astype(str)
        .str.replace(r"[.*\s]+$", "", regex=True)
        .str.replace(r"^[-\s]+|[-\s]+$", "", regex=True)
    )

    dose_units = load_terms("dose_units.txt")
    form_terms = [x for x in load_terms("form_terms.txt") if x not in dose_units]

    df[["PURE", "DOSE", "PACK", "FORMS"]] = df[
        "Название лекарства (чисто)"
    ].apply(lambda x: better_parse_drug_name(x, form_terms, dose_units))

    base = os.path.splitext(os.path.basename(path))[0]
    output = os.path.join(os.path.dirname(path), f"parsed_{base}.csv")
    df.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"✅ Финальный файл сохранён как '{output}'")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parse_turkish_medicines.py <input.csv>")
        sys.exit(1)
    main(sys.argv[1])
