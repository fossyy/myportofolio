Name : Bagas Aulia Rezki

NPM : 2506656545

Class : PBP E
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
