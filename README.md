# VCF Contacts Editor (Windows)

یک برنامه دسکتاپ ساده با Python/Tkinter برای ویندوز که:

- فایل‌های `.vcf` را باز می‌کند.
- مخاطبین را به‌صورت **جدول** نمایش می‌دهد.
- امکان **ویرایش مستقیم سلول‌ها** (با دابل‌کلیک) را می‌دهد.
- امکان **انتخاب چند مخاطب** را دارد.
- با دکمه **Copy Selected** مخاطبین انتخابی را به‌صورت TSV در کلیپ‌بورد کپی می‌کند.
- امکان ذخیره مجدد در فرمت `.vcf` را دارد.

## اجرا

```bash
python vcf_contacts_editor.py
```

## ساخت فایل اجرایی ویندوز (اختیاری)

1. نصب PyInstaller:

```bash
pip install pyinstaller
```

2. ساخت exe:

```bash
pyinstaller --noconfirm --onefile --windowed --name VCF_Contacts_Editor vcf_contacts_editor.py
```

فایل خروجی در مسیر زیر ساخته می‌شود:

- `dist/VCF_Contacts_Editor.exe`

## راهنمای استفاده

1. روی **Open VCF** بزنید و فایل `.vcf` را انتخاب کنید.
2. برای ویرایش، روی هر سلول دابل‌کلیک کنید.
3. برای انتخاب چند سطر از `Ctrl` یا `Shift` استفاده کنید.
4. روی **Copy Selected** بزنید تا اطلاعات مخاطبین انتخابی وارد کلیپ‌بورد شود.
5. روی **Save VCF** بزنید تا خروجی فایل جدید ذخیره شود.
