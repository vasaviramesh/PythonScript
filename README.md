# XML Section Merge Utility

A desktop GUI tool (Tkinter) for merging XML **sections** from one or more sample XML files into a base XML file.

## What this app does

This utility helps you:

1. Select a **base XML** file.
2. Add one or more **sample XML** files.
3. Optionally remove all `<Extension>` nodes (and their children) from both base and sample XMLs before merging.
4. For each sample file, replace the matching section in the base XML (matched by root tag name), or append it if not found.
5. Preview merge actions in a log and save the merged result as a new XML file.

---

## Features

- Simple Tkinter GUI
- Supports multiple sample XML files
- Merge logic by section/root tag name
- Optional cleanup of `<Extension>` elements recursively at parent-child level
- Preview log before save
- Saves merged output with:
  - UTF-8 encoding
  - XML declaration
  - Pretty indentation
- Fallback XML decoding support:
  - `utf-8-sig`
  - `cp1252`
  - `latin-1`

---

## Requirements

- Python **3.8+** (recommended)
- Standard library only (no external dependencies)

Uses:
- `tkinter`
- `xml.etree.ElementTree`
- `copy`
- `os`

---

## File

- `xml_merge_app.py` – main GUI application

---

## How to run

From the project folder:

```bash
python xml_merge_app.py
```

If your system uses `python3`:

```bash
python3 xml_merge_app.py
```

---

## Merge behavior

For each selected sample XML file:

- The sample file’s **root element tag** is used as the section name.
- The app searches the base XML tree for the first child element with the same local tag name.
- If found, that section is **replaced** (keeping sibling position and tail formatting).
- If not found, the section is **appended** to the base XML root.

> Note: Namespace prefixes are normalized by local tag name comparison.

---

## UI workflow

1. **Base XML file** → choose the source XML to update.
2. **Sample XML files** → add one or more XML files containing replacement/new sections.
3. **Output XML file** → choose destination for merged XML.
4. Optional checkbox:
   - **Remove every 'Extension' node and its children before merging**
5. Click:
   - **Preview Merge Log** to validate actions without writing a file.
   - **Merge and Save** to generate the final XML file.

---

## Error handling

- Input validation for missing base/sample/output paths
- XML parse fallback with alternate encodings
- Per-sample parse failures are logged and skipped (merge continues)
- Save errors are shown via dialog

---

## Notes / limitations

- Section matching is based on the **sample root tag only**.
- Only the **first matching section** in base XML is replaced.
- The app does not perform XSD/schema validation.
- It removes elements named `Extension` by local tag name (case-insensitive).

---

## Suggested project structure

```text
PythonScript/
├── xml_merge_app.py
└── README.md
```

---

## License

Add your preferred license here (for example: MIT).
