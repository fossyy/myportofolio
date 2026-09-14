Name : Bagas Aulia Rezki

NPM : 2506656545

Class : PBP E

## Deskripsi
Personal website untuk tugas PBP yang terinspirasi dari website portofolio [mas fossy](https://fossy.my.id)

## Cara Menjalankan Proyek

Pastikan Python dan `pip` sudah terpasang, lalu jalankan perintah berikut dari direktori utama proyek:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Untuk Windows, aktifkan virtual environment dengan:

```powershell
venv\Scripts\activate
```

Setelah server berjalan, buka [http://127.0.0.1:8000](http://127.0.0.1:8000) pada browser.

## Mengelola Konten melalui Admin page

Setelah mengaktifkan virtual environment, terapkan migrasi dan buat akun admin:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Buka [Django admin](http://127.0.0.1:8000/admin/) dan masuk menggunakan akun tersebut. Pilih **Projects**, lalu **Add project** untuk mengisi judul dan deskripsi. Source URL dan live URL bersifat opsional; tautan yang kosong tidak ditampilkan. Simpan untuk menampilkan data pada [halaman projects](http://127.0.0.1:8000/projects/). Data dapat diedit atau dihapus melalui admin.

Experience juga dikelola melalui admin dan ditampilkan pada [halaman experience](http://127.0.0.1:8000/experience/).

Technical skills dikelola melalui **Skills** di admin: isi nama, kategori, dan position untuk urutan dalam kategori. Halaman [skills](http://127.0.0.1:8000/skills/) mengelompokkan entri menurut kategori dan dimulai tanpa data contoh.

Education dikelola melalui **Education** di admin: isi kualifikasi, institusi, tahun mulai, dan tahun selesai (kosong untuk pendidikan yang masih berlangsung). Halaman [education](http://127.0.0.1:8000/education/) menampilkan pendidikan terbaru lebih dahulu dan dimulai tanpa data contoh.

Tombol di bawah bio mengikuti nomor bagian: 01 Skills, 02 Experience, 03 Projects, 04 Education, dan 05 Contact. Contact tetap berada di halaman utama.

## Menjalankan testing

Dengan virtual environment aktif, jalankan:

```bash
python manage.py makemigrations --check --dry-run
python manage.py check
python manage.py test
```

## Dokumentasi Progres Mingguan

### Minggu 1 - Inisialisasi Proyek (31 Agustus 2026)

- Membuat dokumentasi awal proyek (`d258cf6`).
- Menginisialisasi proyek Django beserta konfigurasi, dependency, dan entry point aplikasi (`e53099b`).
- Membuat template awal portofolio, view, URL, dan stylesheet utama (`f8fe2c0`).
- Memperbaiki konfigurasi static files agar aset CSS dapat diakses oleh aplikasi (`66242c2`).

### Minggu 2 - Implementasi Tampilan Portofolio (2–6 September 2026)

- Mengembangkan fondasi visual, layout responsif, navbar, hero, serta menambahkan foto profil (`0a29b9f`).
- Menambahkan bagian skills, experience, dan projects sebagai showcase utama (`bafe94e`).
- Menambahkan bagian contact beserta informasi kontak yang dapat diklik (`d92fcd5`).
- Menambahkan footer dan menyelesaikan struktur utama halaman portofolio (`3cb6355`).

### Minggu 3 - Education dan Refactor Komponen (7 September 2026)

- Menambahkan bagian education ke halaman portofolio (`4c227ac`).
- Membuat base template dan memecah navbar, hero, skills, experience, projects, education, contact, serta footer menjadi komponen template terpisah (`cc4b8e9`–`1f6c71e`).
- Menghapus tautan navigasi campus yang sudah tidak digunakan (`d3b0e47`).
- Menormalkan nomor bagian agar berurutan dari `01` sampai `05` (`d96d24f`).

### Minggu 4 - Portofolio Dinamis dan Pengelolaan Admin (9–13 September 2026)

- Menambahkan aplikasi main, model Experience, migrasi, dan halaman experience berbasis database (`b5c3541`).
- Menghapus seeding otomatis agar konten dikelola melalui admin (`27ac989`).
- Menambahkan model Project, migrasi, dan registrasi admin, serta halaman projects terpisah dengan kondisi kosong (`8f213e3`, `c26bb85`).
- Menambahkan pengujian halaman projects dan dokumentasi pengelolaan konten melalui admin (`dbff316`).
- Memindahkan technical skills dan education ke halaman terpisah, masing-masing dengan model, migrasi, admin, dan pengujian (`252f07f`, `e64a90e`).
- Menambahkan tombol navigasi bernomor `01`–`05` di bawah bio, menghapus "scroll to inspect", dan mempertahankan contact di halaman utama (`39916c9`).

## AI disclosure

Saya menggunakan AI Pada proses pembuatan website portofolio ini, saya sendiri sebenarnya sudah mempunyai website portofolio di [fossy.my.id](https://fossy.my.id) dan saya mengambil sebagian besar design saya dari sana, dan pada website tersebut saya menggunakan tailwindcss sedangkan pada tugas kali ini saya di minta untuk menggunakan vanilla css, jadi saya menggunakan AI untuk mengkonversi beberapa syntax tailwindcss ke vanila css, saya paham ketidak sempurnaan AI pada proses critical thinking jadi saya tidak semana-mena memberikan codebase ini ke AI, Saya melakukan proses cherry pick dalam memilah output dari AI.

Saya sendiri menggunakan ai harness (opencode) dengan model Qwen 3.7 dalam pengembangan ini sehingga history chat di simpan pada perangkat saya dan tidak bisa saya share, untuk transparasi berikut contoh prompt yang saya gunakan

```
*User* : Berikan saya ekuivalen dari class Tailwind CSS berikut dalam vanilla CSS: relative scroll-mt-24 overflow-hidden border-x border-b border-outline px-5 py-24 md:scroll-mt-12 md:px-12

*AI* : 
 .section {
      position: relative;
      scroll-margin-top: 6rem;
      overflow: hidden;
      padding: 6rem 1.25rem;
      border-right: 1px solid #bfb8ac;
      border-bottom: 1px solid #bfb8ac;
      border-left: 1px solid #bfb8ac;
  }

  @media (min-width: 768px) {
      .section {
          scroll-margin-top: 3rem;
          padding-right: 3rem;
          padding-left: 3rem;
      }
  }

  Kemudian class HTML-nya menjadi:

  <section class="section">
      ...
  </section>
```

## Refleksi Tutorial 1 dan Tugas Individu 1

1. **Semantic HTML5**

   Saya menggunakan elemen seperti `<section>`, `<article>`, `<nav>`, `<main>`, dan `<footer>`. Elemen tersebut membuat struktur halaman lebih jelas, mudah di maintain, dan lebih ramah bagi aksesibilitas serta search engine.

2. **CSS Responsif**

   Tantangan utamanya adalah menjaga navbar, teks, card component, dan susunan dua kolom agar tidak overlap di layar kecil. Saya menggunakan media query, flexbox, dan grid, lalu memprioritaskan konten utama dengan mengubah layout menjadi satu kolom pada perangkat mobile.

3. **Keterbatasan Web Statis**

   Konten masih harus diperbarui langsung melalui kode dan belum memiliki interaksi atau pengelolaan data. Pada iterasi berikutnya, saya ingin menambahkan data api call, admin panel, dan formulir kontak yang tersimpan di database.

## Refleksi Tutorial 2 dan Tugas Individu 2

1. **Alur Request dan Tampilan Data**

   Ketika pengguna membuka `/projects/`, `portofolio/urls.py` meneruskan pencocokan URL ke `main/urls.py`, yang memanggil view `show_projects`. View mengambil data database melalui model `Project`, yang mendefinisikan struktur data, lalu memasukkannya ke context. Template menampilkan objek dengan perulangan atau pesan jika kosong. Django mengirimkan hasil HTML untuk ditampilkan browser.

2. **Penyimpanan Data melalui Model**

   Saya menggunakan model agar data terpisah dari view dan bisa dikelola melalui admin panel tanpa mengedit HTML secara langsung. Pemeliharaan lebih mudah karena perubahan konten tidak memerlukan perubahan template. Data yang sama juga dapat digunakan untuk pengembangan fitur pencarian, filter, atau API.

3. **Makemigrations dan Migrate**

   `makemigrations` membuat berkas migrasi dari perubahan struktur model, sedangkan `migrate` menerapkannya ke database. Contohnya, setelah menambahkan field `repository_url = models.URLField(blank=True)` pada model `Skill`, saya menjalankan `python manage.py makemigrations main` lalu `python manage.py migrate` agar kolom baru tersedia di database.
