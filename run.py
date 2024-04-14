import UnityPy
import orjson
from pathlib import Path
from tqdm import tqdm

langs = ["fr", "en", "es", "de", "pt"]
i18n = {}

input_path = Path("input")
working_path = Path("tmp")
output_path = Path("output")

def unpack(file: Path, output: Path, data_file: bool = False):
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

def translate_item(type, keys, language):
    path = Path(f"tmp/i18n/{language}/{type}.json")
    try:
        data = i18n[language][type]
    except KeyError:
        data = False
    if not data:
        try:
            with open(path, 'r') as f:
                data = i18n[language][type] = orjson.loads(f.read())
        except FileNotFoundError:
            return False
    try:
        index = next(i for i, obj in enumerate(data['m_data']['m_keys']) if all(obj[k] == keys[k] for k in keys))
    except StopIteration:
        return False
    return data['m_data']['m_values'][index]['value']

def translate_file(file_path: Path):
    with open(file_path, 'r') as f:
        data = orjson.loads(f.read())
    for key, value in list(data.items()):
        if key.startswith("m_i18n") and key.endswith("Id"):
            attribute = key[6:-2]
            attribute = attribute[0].lower() + attribute[1:]
            for lang in langs:
                translation = translate_item(type_dir.name, value, lang)
                if translation:
                    try:
                        data.get(attribute).get(lang)
                    except AttributeError:
                        data[attribute] = {}
                    except KeyError:
                        data[attribute][lang] = {}                            
                    data[attribute][lang] = translation
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
    
    for lang in langs:
        i18n[lang] = {}
    data_path = Path(f"{working_path}/data")
    for type_dir in data_path.iterdir():
        for file_path in tqdm(type_dir.iterdir(), desc=f"Translate {type_dir.name}"):
            translate_file(file_path)
