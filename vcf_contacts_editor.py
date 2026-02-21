import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


COLUMNS = ["Full Name", "First Name", "Last Name", "Phone", "Email", "Organization"]


class ContactEditorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("VCF Contacts Editor")
        self.root.geometry("1100x650")

        self.contacts: list[dict[str, str]] = []
        self.current_file: Path | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(self.root, padding=10)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="Open VCF", command=self.open_vcf).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Save VCF", command=self.save_vcf).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Copy Selected", command=self.copy_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Add Row", command=self.add_row).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=4)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(toolbar, textvariable=self.status_var).pack(side=tk.RIGHT)

        table_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            table_frame,
            columns=COLUMNS,
            show="headings",
            selectmode="extended",
        )

        for col in COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160, anchor=tk.W)

        self.tree.bind("<Double-1>", self.on_double_click)

        y_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        hint = (
            "Tips: Double-click a cell to edit. Use Ctrl/Shift for multi-select, then click Copy Selected "
            "to send selected rows to clipboard."
        )
        ttk.Label(self.root, text=hint, padding=(10, 0, 10, 10)).pack(fill=tk.X)

    def open_vcf(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select VCF File",
            filetypes=[("VCF files", "*.vcf"), ("All files", "*.*")],
        )
        if not file_path:
            return

        path = Path(file_path)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            contacts = parse_vcf(text)
        except Exception as exc:
            messagebox.showerror("Error", f"Cannot read file:\n{exc}")
            return

        self.contacts = contacts
        self.current_file = path
        self.refresh_table()
        self.status_var.set(f"Loaded {len(self.contacts)} contacts from {path.name}")

    def save_vcf(self) -> None:
        if not self.contacts:
            messagebox.showwarning("Warning", "No contacts to save.")
            return

        default_name = self.current_file.name if self.current_file else "contacts.vcf"
        file_path = filedialog.asksaveasfilename(
            title="Save VCF",
            defaultextension=".vcf",
            initialfile=default_name,
            filetypes=[("VCF files", "*.vcf"), ("All files", "*.*")],
        )
        if not file_path:
            return

        self.sync_from_table()
        output = to_vcf(self.contacts)
        Path(file_path).write_text(output, encoding="utf-8")
        self.status_var.set(f"Saved {len(self.contacts)} contacts to {Path(file_path).name}")

    def refresh_table(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for idx, c in enumerate(self.contacts):
            values = [
                c.get("full_name", ""),
                c.get("first_name", ""),
                c.get("last_name", ""),
                c.get("phone", ""),
                c.get("email", ""),
                c.get("organization", ""),
            ]
            self.tree.insert("", tk.END, iid=str(idx), values=values)

    def sync_from_table(self) -> None:
        new_contacts: list[dict[str, str]] = []
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            new_contacts.append(
                {
                    "full_name": values[0],
                    "first_name": values[1],
                    "last_name": values[2],
                    "phone": values[3],
                    "email": values[4],
                    "organization": values[5],
                }
            )
        self.contacts = new_contacts

    def on_double_click(self, event: tk.Event) -> None:
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        item_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not item_id or not col_id:
            return

        col_index = int(col_id.replace("#", "")) - 1
        x, y, width, height = self.tree.bbox(item_id, col_id)
        old_values = list(self.tree.item(item_id, "values"))

        editor = ttk.Entry(self.tree)
        editor.place(x=x, y=y, width=width, height=height)
        editor.insert(0, old_values[col_index])
        editor.focus()

        def save_edit(_: tk.Event | None = None) -> None:
            old_values[col_index] = editor.get()
            self.tree.item(item_id, values=old_values)
            editor.destroy()
            self.status_var.set("Cell updated")

        editor.bind("<Return>", save_edit)
        editor.bind("<FocusOut>", save_edit)
        editor.bind("<Escape>", lambda _: editor.destroy())

    def add_row(self) -> None:
        item_id = self.tree.insert("", tk.END, values=["", "", "", "", "", ""])
        self.tree.selection_set(item_id)
        self.status_var.set("New row added")

    def delete_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        for item in selected:
            self.tree.delete(item)
        self.status_var.set(f"Deleted {len(selected)} row(s)")

    def copy_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select one or more contacts first.")
            return

        rows = [self.tree.item(item, "values") for item in selected]

        # TSV format makes paste into Excel/Sheets convenient.
        output_lines = ["\t".join(COLUMNS)]
        output_lines.extend("\t".join(map(str, row)) for row in rows)
        output = "\n".join(output_lines)

        self.root.clipboard_clear()
        self.root.clipboard_append(output)
        self.root.update()

        self.status_var.set(f"Copied {len(rows)} contact(s) to clipboard")


def parse_vcf(content: str) -> list[dict[str, str]]:
    unfolded = []
    for line in content.splitlines():
        if line.startswith((" ", "\t")) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)

    contacts: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw in unfolded:
        line = raw.strip()
        if line.upper() == "BEGIN:VCARD":
            current = {
                "full_name": "",
                "first_name": "",
                "last_name": "",
                "phone": "",
                "email": "",
                "organization": "",
            }
        elif line.upper() == "END:VCARD":
            if current is not None:
                contacts.append(current)
            current = None
        elif current is not None and ":" in line:
            key, value = line.split(":", 1)
            key_upper = key.upper()
            if key_upper.startswith("FN"):
                current["full_name"] = value
            elif key_upper.startswith("N"):
                parts = value.split(";")
                current["last_name"] = parts[0] if len(parts) > 0 else ""
                current["first_name"] = parts[1] if len(parts) > 1 else ""
            elif key_upper.startswith("TEL") and not current["phone"]:
                current["phone"] = value
            elif key_upper.startswith("EMAIL") and not current["email"]:
                current["email"] = value
            elif key_upper.startswith("ORG"):
                current["organization"] = value

    return contacts


def to_vcf(contacts: list[dict[str, str]]) -> str:
    lines: list[str] = []
    for contact in contacts:
        full_name = contact.get("full_name", "").strip()
        first_name = contact.get("first_name", "").strip()
        last_name = contact.get("last_name", "").strip()
        phone = contact.get("phone", "").strip()
        email = contact.get("email", "").strip()
        organization = contact.get("organization", "").strip()

        if not full_name:
            full_name = f"{first_name} {last_name}".strip()

        lines.extend([
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"N:{last_name};{first_name};;;",
            f"FN:{full_name}",
        ])

        if phone:
            lines.append(f"TEL;TYPE=CELL:{phone}")
        if email:
            lines.append(f"EMAIL:{email}")
        if organization:
            lines.append(f"ORG:{organization}")

        lines.append("END:VCARD")

    return "\n".join(lines) + "\n"


def main() -> None:
    root = tk.Tk()
    app = ContactEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
