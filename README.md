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

### Minggu 5 - Pengelolaan Konten dan API (16–20 September 2026)

- Menambahkan fitur penghapusan data dan pembuatan project melalui form yang dilindungi autentikasi (`937ce96`).
- Menambahkan kontrol pembuatan dan penghapusan experience (`79ada4d`).
- Menambahkan kontrol pembuatan dan penghapusan skills (`9e37c84`).
- Menambahkan kontrol pembuatan dan penghapusan education (`f414c14`).
- Menambahkan endpoint GET untuk mengambil seluruh data experience, skills, dan education dalam format JSON (`b2ec191`).
- Mempertahankan API projects yang sudah ada dan menambahkan route `/api/experience`, `/api/skills`, serta `/api/education` untuk melengkapi akses data tiap bagian portofolio.

## AI disclosure

Saya menggunakan AI hanya pada Tugas Individu 1 dan Tugas Individu 2. Saya sendiri sebenarnya sudah mempunyai website portofolio di [fossy.my.id](https://fossy.my.id) dan mengambil sebagian besar desain dari sana. Pada website tersebut saya menggunakan Tailwind CSS, sedangkan pada tugas ini saya diminta menggunakan vanilla CSS, sehingga AI saya gunakan untuk membantu mengonversi beberapa syntax Tailwind CSS ke vanilla CSS. Saya memahami keterbatasan AI dalam proses critical thinking, jadi saya tidak menyerahkan seluruh codebase kepada AI dan tetap melakukan cherry pick dalam memilah output yang digunakan.

Untuk Tugas Individu 3, saya tidak menggunakan AI. Seluruh implementasi pada tugas tersebut, termasuk form, pengelolaan konten, fitur API, serta dokumentasinya, dikerjakan secara mandiri.

Pada Tugas Individu 1 dan 2, saya menggunakan AI harness (opencode) dengan model Qwen 3.7. History chat tersimpan pada perangkat saya dan tidak dapat saya bagikan. Sebagai transparansi, berikut contoh prompt yang saya gunakan:

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

## Refleksi Tutorial 3 dan Tugas Individu 3

1. **Penggunaan ModelForm dan Perlindungan CSRF**

   Saya menggunakan `ModelForm` karena form tersebut dapat dibuat langsung berdasarkan model Django. Field, tipe input, validasi dasar, dan proses penyimpanan ke database dapat dikelola oleh Django tanpa harus menulis HTML form serta logika validasinya satu per satu. Dengan begitu, form untuk project, experience, skills, dan education tetap konsisten dan lebih mudah dipelihara. Saya masih dapat menyesuaikan label, placeholder, dan widget melalui `Meta` pada masing-masing form.

   Tag `{% csrf_token %}` wajib ditambahkan pada form yang mengirimkan data ke server, terutama request `POST`. Token ini membantu Django memastikan bahwa request benar-benar berasal dari halaman aplikasi sendiri, bukan dari situs lain yang mencoba mengirimkan request menggunakan sesi pengguna. Tanpa token yang valid, Django akan menolak request tersebut untuk mencegah serangan Cross-Site Request Forgery (CSRF).

2. **JSON dibandingkan XML**

   JSON lebih sering digunakan dalam pengembangan aplikasi web modern karena sintaksnya lebih ringkas, mudah dibaca, dan bentuknya dekat dengan struktur object dan array pada JavaScript. JSON juga dapat diproses oleh banyak bahasa pemrograman serta biasanya menghasilkan ukuran data yang lebih kecil dibandingkan XML. XML tetap berguna untuk kebutuhan tertentu, tetapi untuk komunikasi antara frontend dan backend, JSON umumnya lebih sederhana dan efisien.

3. **Alur View yang Mengembalikan Data JSON**

   Ketika pengguna atau client membuka endpoint seperti `/api/experience`, Django mencocokkan URL tersebut melalui `main/urls.py` lalu memanggil `experience_api` pada `main/views.py`. View mengambil seluruh object `Experience` dari database menggunakan `Experience.objects.all()`. Object tersebut kemudian diserialisasi dengan `serializers.serialize("json", ...)` dan dikembalikan melalui `HttpResponse` dengan `content_type="application/json"`.

   Serialisasi diperlukan karena object model dan QuerySet Django bukan data JSON secara langsung. Proses ini mengubah data model menjadi representasi yang dapat dikirim melalui HTTP, termasuk primary key, nama model, dan nilai field dalam bentuk JSON. Client kemudian dapat membaca response tersebut untuk menampilkan atau memproses data tanpa menerima object Python yang hanya dapat digunakan di sisi server.
