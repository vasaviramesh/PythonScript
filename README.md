# XML Section Merge Utility

A simple standalone Python desktop app (Tkinter) that:

1. Loads one base XML file.
2. Loads multiple sample XML files.
3. Optionally removes every `Extension` node and its children from the base XML.
4. Iterates through each sample file and replaces matching **top-level sections** in the base XML.
5. Saves the merged XML to a new file.

## Matching rule used
A section is considered a match when a **direct child element under the root** of a sample XML has the same tag name as a **direct child under the root** of the base XML.

- If a matching section exists, it is replaced.
- If it does not exist, the section is appended.

## Run it
```bash
python xml_merge_app.py
```

## Optional: build an EXE for Windows
If you want a single-file executable later, you can package it with PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed xml_merge_app.py
```

Your EXE will be created under the `dist` folder.
