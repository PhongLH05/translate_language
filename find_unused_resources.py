import os
import re

PROJECT_DIR = "app/src/main"

RES_DIR = os.path.join(PROJECT_DIR, "res")

CODE_DIRS = [
    os.path.join(PROJECT_DIR, "java"),
    os.path.join(PROJECT_DIR, "kotlin"),
    os.path.join(PROJECT_DIR, "res")
]

RESOURCE_TYPES = {
    "drawable": ["drawable"],
    "layout": ["layout"],
    "menu": ["menu"],
    "raw": ["raw"],
    "font": ["font"],
}

RESOURCE_PATTERN = re.compile(r"R\.(\w+)\.(\w+)")
XML_RESOURCE_PATTERN = re.compile(r"@(\w+)/([\w\.]+)")
KOTLIN_CLASS_PATTERN = re.compile(r"^\s*(class|object)\s+([A-Z]\w*)", re.MULTILINE)
JAVA_CLASS_PATTERN = re.compile(r"^\s*(public\s+)?(class|interface|enum)\s+([A-Z]\w*)", re.MULTILINE)

def collect_resources():

    resources = {}

    for rtype, folders in RESOURCE_TYPES.items():
        resources[rtype] = set()

        for folder in folders:
            full_path = os.path.join(RES_DIR, folder)

            if not os.path.exists(full_path):
                continue

            for file in os.listdir(full_path):
                name = os.path.splitext(file)[0]
                resources[rtype].add(name)

    return resources


def scan_code_for_usage():

    used = {rtype: set() for rtype in RESOURCE_TYPES.keys()}
    files_scanned = 0

    for code_dir in CODE_DIRS:

        if not os.path.exists(code_dir):
            continue

        for root, dirs, files in os.walk(code_dir):

            for file in files:

                if not file.endswith((".kt", ".java", ".xml")):
                    continue

                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf8", errors="ignore") as f:
                        content = f.read()
                except:
                    continue

                files_scanned += 1

                matches = RESOURCE_PATTERN.findall(content)

                for rtype, name in matches:
                    if rtype in used:
                        used[rtype].add(name)

                # Bắt thêm usage dạng @drawable/foo, @layout/bar trong XML
                if file.endswith(".xml"):
                    xml_matches = XML_RESOURCE_PATTERN.findall(content)
                    for rtype, name in xml_matches:
                        if rtype in used:
                            used[rtype].add(name)

    print(f"\nScanned {files_scanned} files for resource usage.")

    return used


def find_unused():

    resources = collect_resources()
    used = scan_code_for_usage()

    total_all = 0
    unused_all = 0

    for rtype in RESOURCE_TYPES.keys():

        unused = resources[rtype] - used[rtype]
        total_all += len(resources[rtype])
        unused_all += len(unused)

        print("\n==============================")
        print(f"Unused {rtype.upper()} ({len(unused)})")
        print("==============================")

        for name in sorted(unused):
            print(name)

    print("\n---------- SUMMARY ----------")
    print(f"Total resources: {total_all}")
    print(f"Total unused:    {unused_all}")


def collect_code_symbols():

    code_files = []
    symbols = {}  # symbol_name -> set of file paths it is defined in

    for code_dir in CODE_DIRS:

        if not os.path.exists(code_dir):
            continue

        for root, dirs, files in os.walk(code_dir):

            for file in files:

                if not file.endswith((".kt", ".java")):
                    continue

                path = os.path.join(root, file)
                code_files.append(path)

                try:
                    with open(path, "r", encoding="utf8", errors="ignore") as f:
                        content = f.read()
                except:
                    continue

                # Kotlin: class/object Name
                for _, name in KOTLIN_CLASS_PATTERN.findall(content):
                    symbols.setdefault(name, set()).add(path)

                # Java: class/interface/enum Name
                for match in JAVA_CLASS_PATTERN.findall(content):
                    name = match[2]
                    symbols.setdefault(name, set()).add(path)

    return code_files, symbols


def find_unused_code_files():

    print("\n========== CODE USAGE ANALYSIS ==========")

    code_files, symbols = collect_code_symbols()

    # Nếu không tìm được symbol nào thì bỏ qua
    if not symbols:
        print("No Kotlin/Java symbols found. Skipping code usage analysis.")
        return

    # Gom tất cả content để tìm reference
    all_contents = {}
    for path in code_files:
        try:
            with open(path, "r", encoding="utf8", errors="ignore") as f:
                all_contents[path] = f.read()
        except:
            all_contents[path] = ""

    # Thêm AndroidManifest.xml nếu có, vì Activity/Service chỉ có thể xuất hiện ở đây
    manifest_path = os.path.join(PROJECT_DIR, "AndroidManifest.xml")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf8", errors="ignore") as f:
                all_contents[manifest_path] = f.read()
        except:
            all_contents[manifest_path] = ""

    referenced_symbols = set()

    # Với mỗi symbol, kiểm tra xem nó có xuất hiện ở bất kỳ file nào khác file định nghĩa không
    for symbol, defining_files in symbols.items():
        pattern = re.compile(r"\b" + re.escape(symbol) + r"\b")

        for path, content in all_contents.items():
            # Nếu symbol xuất hiện ở một file (kể cả chính file đó) thì coi là được tham chiếu
            if pattern.search(content):
                referenced_symbols.add(symbol)
                break

    # File được coi là "ít được dùng" nếu tất cả symbol top-level trong đó đều không được tham chiếu ở nơi nào khác
    unused_files = set()
    for symbol, defining_files in symbols.items():
        if symbol in referenced_symbols:
            continue
        for path in defining_files:
            unused_files.add(path)

    print(f"Total code files scanned: {len(code_files)}")
    print(f"Total symbols found:      {len(symbols)}")
    print(f"Potentially unused files: {len(unused_files)}")

    if unused_files:
        print("\nThese files seem unused (heuristic, may contain false positives):")
        for path in sorted(unused_files):
            print(f"- {path}")
    else:
        print("\nNo obviously unused code files found by this heuristic.")


if __name__ == "__main__":
    find_unused()
    find_unused_code_files()