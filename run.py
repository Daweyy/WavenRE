from pathlib import Path
from tqdm import tqdm
from typing import TypedDict

import UnityPy
import orjson
import shutil


langs = ["fr", "en", "es", "de", "pt"]
i18n = {lang: {} for lang in langs}

input_path = Path("input")
working_path = Path("tmp")
output_path = Path("output")


class I18nKey(TypedDict):
    a: int
    b: int
    c: int
    d: int
    e: int


def unpack(file: Path, output: Path, data_file: bool = False) -> None:
    env = UnityPy.load(str(file))
    for obj in tqdm(env.objects, desc=f"Unpacking {file.name}"):
        if obj.type.name == "MonoBehaviour":
            if obj.serialized_type.nodes:
                data = obj.read_typetree()
                if data_file:
                    json = orjson.loads(data["m_jsonRepresentation"])
                    data["values"] = json
                    del data["m_jsonRepresentation"]
                    type = json["type"].replace("Definition", "")
                    if not type.endswith("s"):
                        type += "s"
                    dest = output / type / f"{json["id"]}.json"
                else:
                    dest = output / f"{data['m_Name']}.json"
                dest.parent.mkdir(exist_ok=True, parents=True)
                dest.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))


def translate_item(type: str, keys: I18nKey, language: str) -> str | None:
    path = working_path / f"i18n/{language}/{type}.json"
    if not (data := i18n[language].get(type)):
        if path.exists():
            data = i18n[language][type] = orjson.loads(path.read_bytes())
        else:
            return None
    try:
        index = data['m_data']['m_keys'].index(keys)
    except ValueError:
        return None
    return data['m_data']['m_values'][index]['value']


def translate_file(file_path: Path) -> None:
    data = orjson.loads(file_path.read_bytes())
    keys = [key for key in data.keys() if key.startswith("m_i18n") and key.endswith("Id")]
    for key in keys:
        attribute = key[6:-2]
        attribute = attribute[0].lower() + attribute[1:]
        translation = {lang: trad for lang in langs
                       if (trad := translate_item(type_dir.name, data[key], lang))}
        if translation:
            data[attribute] = translation
    dest = output_path / type_dir.name / f"{data['values']['id']}.json"
    dest.parent.mkdir(exist_ok=True, parents=True)
    dest.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))


if __name__ == '__main__':
    UnityPy.config.FALLBACK_UNITY_VERSION = "2023.0.0f5"

    for file_path in input_path.iterdir():
        if 'data' in file_path.name:
            unpack(file_path, working_path / 'data', True)
        elif 'localization' in file_path.name:
            language = file_path.name.split('.')[1].split('-')[0]
            unpack(file_path, working_path / 'i18n' / language)
        else:
            print(f"Info: File {file_path.name} does not match 'data' or 'localization', ignored.")

    data_path = working_path / "data"
    for type_dir in data_path.iterdir():
        for file_path in tqdm(list(type_dir.iterdir()), desc=f"Translate {type_dir.name}"):
            translate_file(file_path)

    shutil.rmtree(working_path, ignore_errors=True)
