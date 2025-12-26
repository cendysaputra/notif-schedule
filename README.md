# Notif Schedule - Automated Project Notification System

Sistem notifikasi email otomatis untuk memantau jadwal proyek dan mengirimkan pengingat harian tentang event yang akan datang.

## Fitur

✅ Notifikasi email otomatis tiap hari jam 09:00 WIB
✅ Deteksi event buat hari ini dan besok
✅ Kategoris notifikasi: "HARI INI" dan "BESOK"
✅ Support multi-proyek
✅ Integrasi GitHub Actions untuk otomasi
✅ Format jadwal simple berbasis text file

## Struktur Folder

notif-schedule/
├── .github/
│ └── workflows/
│ └── daily-notif.yml # GitHub Actions workflow
├── email-notif.py # Script utama notifikasi
├── jadwal_proyek.txt # Database jadwal proyek
├── .gitignore # File ignore
└── README.md # Dokumentasi

## Cara Kerja

1. GitHub Actions jalankan workflow tiap hari jam 02:00 UTC (09:00 WIB)
2. email-notif.py mbaca file `jadwal_proyek.txt`
3. Script periksa tanggal yang cocok dengan hari ini dan besok
4. Email kirim otomatis ke alamat yang ditentukan
5. Notifikasi dikategorikan: HARI INI dan BESOK

## Setup GitHub Actions

### 1. Setup Repository Secrets

Buka repository GitHub → Settings → Secrets and variables → Actions → New repository secret

Tambahkan 3 secrets berikut:
| `SENDER_EMAIL` | Email Gmail pengirim | `your-email@gmail.com` |
| `SENDER_PASSWORD` | App Password Gmail | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL` | Email penerima notifikasi | `recipient@gmail.com` |

### 2. Cara Mendapatkan Gmail App Password

1. Buka: https://myaccount.google.com/apppasswords
2. Login pakai akun Gmail
3. Pilih App → Other (Custom name) → ketik "Notif Schedule"
4. Klik Generate
5. Copy password 16 karakter yang ada
6. Paste ke secret `SENDER_PASSWORD`

Catatan: Pastikan 2-Factor Authentication sudah aktif di akun Gmail.

### 3. Aktifkan GitHub Actions

1. Push repository ke GitHub
2. Buka tab Actions
3. Workflow akan otomatis jalan tiap hari jam 09:00 WIB
4. Atau klik Run workflow buat test manual

## Format File jadwal_proyek.txt

File `jadwal_proyek.txt` pakai format sederhana:

Nama Perusahaan 1
Hari, DD MMM YYYY - Deskripsi kegiatan
Hari, DD MMM YYYY - Deskripsi kegiatan

Nama Perusahaan 2
Hari, DD MMM YYYY - Deskripsi kegiatan

### Aturan Format:

- Baris pertama = Nama perusahaan/klien (tidak ada format tanggal)
- Baris berikutnya = Format: `Hari, DD MMM YYYY - Deskripsi`
- Baris kosong = Pemisah antar proyek
- Format bulan: Jan, Feb, Mar, Apr, Mei, Jun, Jul, Agu, Sep, Okt, Nov, Des

## Contoh Email Notifikasi

Subject: Notifikasi Jadwal Proyek - [Tanggal Hari Ini]

JADWAL HARI INI (Kamis, 24 Okt 2024):
• Nama Perusahaan 1 - Pengumpulan Materi

JADWAL BESOK (Jumat, 25 Okt 2024):
• Nama Perusahaan 2 - Pengerjaan Design

Notifikasi dikirim pada: 24-10-2024 09:00:15 WIB

## Kustomisasi

### Ubah Jadwal Notifikasi

Edit file `.github/workflows/daily-notif.yml`:

```yaml
on:
  schedule:
    # Ubah waktu di sini
    - cron: "0 2 * * *" # 02:00 UTC = 09:00 WIB
```

### Tambah Penerima Email

Edit GitHub Secret `RECIPIENT_EMAIL` atau file lokal `email_config.json`:

```json
{
  "recipient_emails": ["email1@gmail.com", "email2@gmail.com", "email3@gmail.com"]
}
```

## Lisensi :

Project ini dibuat untuk keperluan internal manajemen proyek
