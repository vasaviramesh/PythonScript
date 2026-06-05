import copy
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from xml.etree import ElementTree as ET


def local_name(tag: str) -> str:
    if not isinstance(tag, str):
        return ""
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def indent_xml(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent_xml(child, level + 1)
        if not elem[-1].tail or not elem[-1].tail.strip():
            elem[-1].tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


class XmlMergeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Section Merge Utility")
        self.root.geometry("950x700")

        self.base_xml_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.remove_extension = tk.BooleanVar(value=True)

        self.sample_paths = []

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        title = ttk.Label(main, text="XML Section Merge Utility", font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w", pady=(0, 8))

        help_text = (
            "1) Select a base XML file and one or more sample XML files.\n"
            "2) Optional: remove every <Extension> node and its children.\n"
            "3) For each sample file, replace matching sections in the base XML.\n"
            "   A section matches when the sample section tag has the same name.\n"
            "4) Save the merged result to a new XML file."
        )
        ttk.Label(main, text=help_text, justify="left").pack(anchor="w", pady=(0, 12))

        file_frame = ttk.LabelFrame(main, text="Files", padding=10)
        file_frame.pack(fill="x", pady=(0, 12))

        # Base XML
        ttk.Label(file_frame, text="Base XML file:").grid(row=0, column=0, sticky="w")
        ttk.Entry(file_frame, textvariable=self.base_xml_path, width=85).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(file_frame, text="Browse...", command=self.choose_base_file).grid(row=0, column=2)

        # Sample files
        ttk.Label(file_frame, text="Sample XML files:").grid(row=1, column=0, sticky="nw", pady=(12, 0))
        sample_buttons = ttk.Frame(file_frame)
        sample_buttons.grid(row=1, column=2, sticky="ne", pady=(12, 0))
        ttk.Button(sample_buttons, text="Add samples...", command=self.add_sample_files).pack(fill="x")
        ttk.Button(sample_buttons, text="Clear", command=self.clear_samples).pack(fill="x", pady=(6, 0))

        self.sample_listbox = tk.Listbox(file_frame, height=8, width=80)
        self.sample_listbox.grid(row=1, column=1, sticky="ew", padx=8, pady=(12, 0))

        # Output
        ttk.Label(file_frame, text="Output XML file:").grid(row=2, column=0, sticky="w", pady=(12, 0))
        ttk.Entry(file_frame, textvariable=self.output_path, width=85).grid(row=2, column=1, sticky="ew", padx=8, pady=(12, 0))
        ttk.Button(file_frame, text="Save as...", command=self.choose_output_file).grid(row=2, column=2, pady=(12, 0))

        file_frame.columnconfigure(1, weight=1)

        options = ttk.LabelFrame(main, text="Options", padding=10)
        options.pack(fill="x", pady=(0, 12))
        ttk.Checkbutton(
            options,
            text="Remove every 'Extension' node and its children before merging",
            variable=self.remove_extension,
        ).pack(anchor="w")

        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(0, 12))
        ttk.Button(actions, text="Preview Merge Log", command=self.preview_merge).pack(side="left")
        ttk.Button(actions, text="Merge and Save", command=self.merge_and_save).pack(side="left", padx=8)

        log_frame = ttk.LabelFrame(main, text="Log", padding=10)
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_frame, wrap="word", height=20)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

    def log(self, message: str):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.root.update_idletasks()

    def clear_log(self):
        self.log_text.delete("1.0", "end")

    def choose_base_file(self):
        path = filedialog.askopenfilename(
            title="Select base XML file",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
        )
        if path:
            self.base_xml_path.set(path)
            if not self.output_path.get():
                base_name = os.path.splitext(os.path.basename(path))[0]
                default_out = os.path.join(os.path.dirname(path), f"{base_name}_merged.xml")
                self.output_path.set(default_out)

    def add_sample_files(self):
        paths = filedialog.askopenfilenames(
            title="Select sample XML files",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
        )
        for path in paths:
            if path not in self.sample_paths:
                self.sample_paths.append(path)
                self.sample_listbox.insert("end", path)

    def clear_samples(self):
        self.sample_paths = []
        self.sample_listbox.delete(0, "end")

    def choose_output_file(self):
        path = filedialog.asksaveasfilename(
            title="Select output XML file",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
        )
        if path:
            self.output_path.set(path)

    def validate_inputs(self):
        if not self.base_xml_path.get():
            messagebox.showerror("Missing file", "Please select a base XML file.")
            return False
        if not self.sample_paths:
            messagebox.showerror("Missing files", "Please add at least one sample XML file.")
            return False
        if not self.output_path.get():
            messagebox.showerror("Missing output", "Please choose an output XML file.")
            return False
        return True

    def remove_extension_nodes(self, root):
        removed_count = 0
        for parent in list(root.iter()):
            children = list(parent)
            for child in children:
                if local_name(child.tag).lower() == "extension":
                    parent.remove(child)
                    removed_count += 1
        return removed_count

    def find_element_parent_by_tag(self, root, target_tag_name):
        for parent in root.iter():
            for child in list(parent):
                if local_name(child.tag) == target_tag_name:
                    return parent, child
        return None, None

    def _find_parent_child_by_path(self, root, tag_path):
        """
        Find parent/child in base tree using an exact local-name path.
        tag_path is a list like ["Message","Body","NewRx","MedicationPrescribed"].
        Returns (parent, child) for the final node, or (None, None).
        """
        if not tag_path or local_name(root.tag) != tag_path[0]:
            return None, None

        current = root
        for name in tag_path[1:-1]:
            nxt = None
            for ch in list(current):
                if isinstance(ch.tag, str) and local_name(ch.tag) == name:
                    nxt = ch
                    break
            if nxt is None:
                return None, None
            current = nxt

        target_name = tag_path[-1]
        for ch in list(current):
            if isinstance(ch.tag, str) and local_name(ch.tag) == target_name:
                return current, ch
        return None, None

    def _path_from_root_to_node(self, root, target):
        """Return local-name path list from root to target node, else None."""
        target_id = id(target)
        path = []

        def dfs(node):
            path.append(local_name(node.tag))
            if id(node) == target_id:
                return True
            for ch in list(node):
                if isinstance(ch.tag, str) and dfs(ch):
                    return True
            path.pop()
            return False

        return path[:] if dfs(root) else None

    def get_sample_sections(self, base_root, sample_root):
        sample_tag_name = local_name(sample_root.tag)
        base_tag_name = local_name(base_root.tag)

        if sample_tag_name != base_tag_name:
            _, existing = self.find_element_parent_by_tag(base_root, sample_tag_name)
            if existing is not None:
                return [sample_root]

            matching_children = [
                child
                for child in list(sample_root)
                if isinstance(child.tag, str)
                and self.find_element_parent_by_tag(base_root, local_name(child.tag))[1] is not None
            ]
            if matching_children:
                return matching_children

            return [sample_root]

        return [child for child in list(sample_root) if isinstance(child.tag, str)]

    def merge_sections(self, base_root, sample_root, sample_name):
        replaced = 0
        appended = 0
        skipped = 0

        sample_sections = self.get_sample_sections(base_root, sample_root)
        if not sample_sections:
            self.log(f"- {sample_name}: no sections found; skipped.")
            return replaced, appended, skipped

        for sample_section in sample_sections:
            tag_name = local_name(sample_section.tag)
            # Prefer exact path match (reliable when tags repeat in many places)
            section_path = self._path_from_root_to_node(sample_root, sample_section)
            parent, existing = (None, None)
            if section_path:
                parent, existing = self._find_parent_child_by_path(base_root, section_path)

            # Fallback to old behavior
            if existing is None:
                parent, existing = self.find_element_parent_by_tag(base_root, tag_name)

            incoming = copy.deepcopy(sample_section)
            if existing is not None:
                incoming.tail = existing.tail
                siblings = list(parent)
                index = siblings.index(existing)
                parent.remove(existing)
                parent.insert(index, incoming)
                replaced += 1
                if section_path:
                    self.log(f"  Replaced section: {'/'.join(section_path)}")
                else:
                    self.log(f"  Replaced section: {tag_name}")
            else:
                base_root.append(incoming)
                appended += 1
                self.log(f"  Appended new section: {tag_name}")

        return replaced, appended, skipped

    def run_merge(self, save=False):
        if not self.validate_inputs():
            return

        self.clear_log()
        try:
            base_tree = ET.parse(self.base_xml_path.get())
            base_root = base_tree.getroot()
        except Exception as ex:
            messagebox.showerror("XML error", f"Could not read base XML file.\n\n{ex}")
            return

        self.log(f"Base XML: {self.base_xml_path.get()}")
        self.log(f"Samples: {len(self.sample_paths)} file(s)")
        self.log("=")

        if self.remove_extension.get():
            removed_count = self.remove_extension_nodes(base_root)
            self.log(f"Removed Extension nodes from base: {removed_count}")
        else:
            self.log("Extension node removal: skipped")

        total_replaced = 0
        total_appended = 0

        for sample_path in self.sample_paths:
            self.log(f"\nProcessing sample: {sample_path}")
            try:
                sample_tree = ET.parse(sample_path)
                sample_root = sample_tree.getroot()
            except Exception as ex:
                self.log(f"  ERROR: Could not read sample XML: {ex}")
                continue

            if self.remove_extension.get():
                removed_count = self.remove_extension_nodes(sample_root)
                self.log(f"  Removed Extension nodes from sample: {removed_count}")

            replaced, appended, _ = self.merge_sections(base_root, sample_root, os.path.basename(sample_path))
            total_replaced += replaced
            total_appended += appended

        indent_xml(base_root)

        self.log("\n=")
        self.log(f"Total sections replaced: {total_replaced}")
        self.log(f"Total sections appended: {total_appended}")

        if save:
            try:
                ET.register_namespace('', self._detect_default_namespace(base_root.tag))
            except Exception:
                pass
            try:
                out_path = self.output_path.get()
                base_tree.write(out_path, encoding="utf-8", xml_declaration=True)
                self.log(f"\nSaved merged XML to: {out_path}")
                messagebox.showinfo("Done", f"Merged XML saved successfully.\n\n{out_path}")
            except Exception as ex:
                messagebox.showerror("Save error", f"Could not save output XML file.\n\n{ex}")

    def _detect_default_namespace(self, tag):
        if isinstance(tag, str) and tag.startswith("{") and "}" in tag:
            return tag[1:].split("}", 1)[0]
        return ""

    def preview_merge(self):
        self.run_merge(save=False)

    def merge_and_save(self):
        self.run_merge(save=True)


if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except Exception:
        pass
    app = XmlMergeApp(root)
    root.mainloop()
