import re
import pandas as pd


def load_terms(filename):
    """Load list of terms from a text file, uppercase"""
    with open(filename, encoding="utf-8") as f:
        return [line.strip().upper() for line in f if line.strip()]


def better_parse_drug_name(name, form_terms, dose_units):
    """Parse drug name into PURE, DOSE, PACK, FORMS"""
    name_up = name.upper()

    # 1) Dose: first occurrence of number + dose unit
    dose_pattern = r"(\d+(?:[\.,]\d+)?\s*(%s))" % "|".join(dose_units)
    dose_match = re.search(dose_pattern, name_up)
    dose = dose_match.group(0).replace(" ", "") if dose_match else ""

    # 2) Pack: first occurrence of number + form term
    pack_pattern = r"(\d+\s?(%s))" % "|".join(form_terms)
    pack_match = re.search(pack_pattern, name_up)
    pack = pack_match.group(0).replace(" ", "") if pack_match else ""

    # 3) Cut out found dose and pack for form detection
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
