import os
import re
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor

INPUT_FILE = "app/src/main/res/values/strings.xml"

# Google code -> Android folder
LANGUAGES = {
    "hi": "hi",
    "pt": "pt",
    "id": "in",
    "es": "es",
    "fr": "fr",
    "ar": "ar",
    "ko": "ko",
    "ja": "ja",
    "zh-CN": "zh",
    "vi": "vi",
    "it": "it",
    "ru": "ru",
    "tr": "tr",
    "mr": "mr",
    "ta": "ta",
    "te": "te",
    "bn": "bn",
    "th": "th"
}

MAX_WORKERS = min(10, len(LANGUAGES))

FORMAT_PATTERN = re.compile(r"%(\d+\$)?[sdif]")
HTML_PATTERN = re.compile(r"</?(b|i|u|font)[^>]*>")
URL_PATTERN = re.compile(r"http[s]?://")
NON_TRANSLATABLE_PATTERN = re.compile(r"^[0-9\s\.\,\:\;\-\+\(\)]+$")
SHORT_SKIP_WORDS = {"ok", "no", "yes", "on", "off"}

def should_skip(text):
    if text is None:
        return True
    if URL_PATTERN.search(text):
        return True
    if NON_TRANSLATABLE_PATTERN.match(text):
        return True
    stripped = text.strip()
    if stripped.lower() in SHORT_SKIP_WORDS:
        return True
    return False

def protect_format(text):
    mapping = {}
    protected = text

    for i, match in enumerate(FORMAT_PATTERN.finditer(text)):
        key = f"__FMT{i}__"
        mapping[key] = match.group()
        protected = protected.replace(match.group(), key)

    return protected, mapping

def restore_format(text, mapping):
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

def protect_html(text):
    mapping = {}
    protected = text

    for i, match in enumerate(HTML_PATTERN.finditer(text)):
        key = f"__HTML{i}__"
        mapping[key] = match.group()
        protected = protected.replace(match.group(), key, 1)

    return protected, mapping

def restore_html(text, mapping):
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text


def escape_android_special_chars(text):
    if text is None:
        return text
    # Thứ tự quan trọng: escape backslash trước
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")
    return text


tree = ET.parse(INPUT_FILE)
root = tree.getroot()

strings = []

for child in root:
    if child.tag != "string":
        continue

    if child.attrib.get("translatable") == "false":
        continue

    name = child.attrib.get("name")
    text = child.text

    if name and text:
        strings.append((name, text))


def translate_language(google_code, android_code):

    print("Translating:", android_code)

    folder = f"app/src/main/res/values-{android_code}"
    os.makedirs(folder, exist_ok=True)

    target_file = f"{folder}/strings.xml"

    # Đọc file đích nếu đã tồn tại để tái sử dụng các bản dịch cũ
    existing_translations = {}
    if os.path.exists(target_file):
        try:
            existing_tree = ET.parse(target_file)
            existing_root = existing_tree.getroot()
            for child in existing_root:
                if child.tag != "string":
                    continue
                name = child.attrib.get("name")
                if name:
                    existing_translations[name] = child
        except Exception:
            # Nếu file cũ bị lỗi thì bỏ qua, dịch lại toàn bộ
            existing_translations = {}

    texts_to_translate = []
    format_maps = []
    html_maps = []
    names_to_translate = []
    original_texts_to_translate = []

    for name, text in strings:

        # Nếu string này đã có trong file đích thì không dịch lại
        if name in existing_translations:
            continue

        # Nếu không cần dịch (URL, số, v.v.) thì cũng không đưa vào batch
        if should_skip(text):
            continue

        protected, fmt_map = protect_format(text)
        protected, html_map = protect_html(protected)

        texts_to_translate.append(protected)
        format_maps.append(fmt_map)
        html_maps.append(html_map)
        names_to_translate.append(name)
        original_texts_to_translate.append(text)

    translator = GoogleTranslator(source="en", target=google_code)

    translated_by_name = {}
    if texts_to_translate:
        try:
            translated_batch = translator.translate_batch(texts_to_translate)
        except Exception:
            translated_batch = texts_to_translate

        for name, original_text, translated, fmt_map, html_map in zip(
            names_to_translate,
            original_texts_to_translate,
            translated_batch,
            format_maps,
            html_maps,
        ):
            if translated is None:
                translated = original_text
            else:
                translated = str(translated)

            translated = restore_format(translated, fmt_map)
            translated = restore_html(translated, html_map)
            translated = escape_android_special_chars(translated)
            translated_by_name[name] = translated

    new_root = ET.Element("resources")

    for name, original_text in strings:

        if name in existing_translations:
            # Giữ nguyên bản dịch cũ
            old_elem = existing_translations[name]
            element = ET.SubElement(new_root, "string", old_elem.attrib)
            element.text = old_elem.text
            continue

        if should_skip(original_text):
            # Không dịch, giữ nguyên tiếng Anh (hoặc text gốc)
            element = ET.SubElement(new_root, "string")
            element.set("name", name)
            element.text = escape_android_special_chars(original_text)
            continue

        translated = translated_by_name.get(name, original_text)

        element = ET.SubElement(new_root, "string")
        element.set("name", name)
        element.text = translated

    tree = ET.ElementTree(new_root)

    tree.write(
        target_file,
        encoding="utf-8",
        xml_declaration=True
    )


with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    for google_code, android_code in LANGUAGES.items():
        executor.submit(translate_language, google_code, android_code)


print("✅ All languages translated successfully")