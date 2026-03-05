# 🚀 Android Strings Auto Translator

A fast Python tool to automatically translate **Android `strings.xml`** into multiple languages using **Google Translate**.

This script is optimized for **Android developers** who want to localize their apps quickly without manually translating hundreds of strings.

⚡ **Performance:**
Translates **300+ strings into 18 languages in ~10 minutes**.

---

# ✨ Features

* 🌍 Translate Android `strings.xml` into **18 languages**
* ⚡ **Parallel translation** using multithreading
* 📦 **Batch translation** for faster API calls
* 🔁 **Incremental translation** (skip already translated strings)
* 🛡 Protects:

  * Android format arguments (`%s`, `%d`, `%1$s`, etc.)
  * HTML tags (`<b>`, `<i>`, `<font>`, etc.)
  * URLs
* 🔒 Escapes Android special characters automatically
* 🚫 Skips non-translatable values (numbers, URLs, short system words)

---

# 🌐 Supported Languages

The script automatically generates Android `values-*` folders for the following languages:

| Language             | Android Folder |
| -------------------- | -------------- |
| Hindi                | values-hi      |
| Portuguese           | values-pt      |
| Indonesian           | values-in      |
| Spanish              | values-es      |
| French               | values-fr      |
| Arabic               | values-ar      |
| Korean               | values-ko      |
| Japanese             | values-ja      |
| Chinese (Simplified) | values-zh      |
| Vietnamese           | values-vi      |
| Italian              | values-it      |
| Russian              | values-ru      |
| Turkish              | values-tr      |
| Marathi              | values-mr      |
| Tamil                | values-ta      |
| Telugu               | values-te      |
| Bengali              | values-bn      |
| Thai                 | values-th      |

---

# 📂 Project Structure

```
project-root
│
├── app/
│   └── src/main/res/
│       ├── values/
│       │   └── strings.xml
│       ├── values-es/
│       ├── values-fr/
│       ├── values-ja/
│       └── ...
│
├── translate_strings.py
└── README.md
```

---

# 🛠 Installation

### 1️⃣ Install Python dependencies

```bash
pip install deep-translator
```

---

### 2️⃣ Place the script in your project root

Example:

```
your-android-project/
│
├── app/
├── translate_strings.py
```

---

# ▶️ Usage

Run the script:

```bash
python3 translate_strings.py
```

The script will:

1. Read the base file:

```
app/src/main/res/values/strings.xml
```

2. Automatically generate translated files:

```
values-es/strings.xml
values-fr/strings.xml
values-ja/strings.xml
...
```

---

# ⚡ Performance

Typical translation speed:

| Strings | Languages | Time        |
| ------- | --------- | ----------- |
| 300     | 18        | ~10 minutes |
| 500     | 18        | ~15 minutes |

Speed improvements come from:

* Multithreading
* Batch translation
* Skipping existing translations

---

# 🧠 Smart Skipping

The script will **NOT translate**:

* URLs
* Numbers
* System words (`ok`, `yes`, `no`, `on`, `off`)
* Strings marked with

```xml
translatable="false"
```

Example:

```xml
<string name="privacy_url" translatable="false">
https://example.com/privacy
</string>
```

---

# 🛡 Format Protection

The script safely preserves Android placeholders.

Example:

```
Hello %1$s, you have %2$d messages
```

Translated result keeps format intact.

---

# 🧪 HTML Tag Support

Supported tags are preserved:

```
<b>
<i>
<u>
<font>
```

Example:

```xml
<string name="welcome">
Welcome <b>User</b>
</string>
```

---

# 🔁 Incremental Translation

If a translation file already exists:

```
values-es/strings.xml
```

The script will **reuse existing translations** and **only translate new strings**.

This prevents unnecessary API calls and makes repeated runs much faster.

---

# ⚠️ Notes

* The base language should be **English**.
* Ensure your base file exists:

```
app/src/main/res/values/strings.xml
```

* Internet connection is required for Google Translate.

---

# 👨‍💻 Use Case

Perfect for:

* Android app localization
* Play Store multi-language apps
* Rapid MVP translation
* Indie developers shipping globally

---

# ⭐ Example Result

Before:

```
values/strings.xml
```

After running the script:

```
values-es/strings.xml
values-fr/strings.xml
values-ja/strings.xml
values-vi/strings.xml
...
```

All generated automatically.

---

# 📜 License

MIT License.
Feel free to use and modify.

---

# ❤️ Contribution

Pull requests and improvements are welcome.
