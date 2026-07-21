from app.database import SessionLocal, engine, Base
from app.models import Kecamatan, Desa

# Pastikan tabel dibuat jika belum ada
Base.metadata.create_all(bind=engine)

def seed_deli_serdang():
    db = SessionLocal()
    try:
        # Data 22 Kecamatan & Sampel Desa di Deli Serdang
        data_wilayah = {
            "Bangun Purba": ["Bangun Purba", "Bangun Purba Tengah", "Bander Meriah", "Damak Maliho"],
            "Batang Kual": ["Batang Kual", "Bintang Meriah", "Pematang Johar"],
            "Beringin": ["Beringin", "Araskabu", "Sidodadi Ramunia", "Emplasmen Kualanamu"],
            "Biru-Biru": ["Biru-Biru", "Candi Rejo", "Mbaruai", "Sidomulyo"],
            "Delitua": ["Delitua", "Delitua Barat", "Delitua Timur", "Kedai Durian"],
            "Galang": ["Galang Kota", "Galang Barat", "Namu Rambe", "Pulai Gambar"],
            "Gunung Meriah": ["Gunung Meriah", "Marjanji Pematang", "Ujung Meriah"],
            "Karang Baru": ["Karang Baru", "Cinta Rakyat", "Paya Gambar"],
            "Kutalimbaru": ["Kutalimbaru", "Lau Bakeri", "Namu Mirik", "Suka Makmur"],
            "Labuhan Deli": ["Helvetia", "Manunggal", "Pematang Johar", "Karang Gading"],
            "Lubuk Pakam": ["Lubuk Pakam I, II", "Lubuk Pakam III", "Tanjung Garbus", "Pekarangan"],
            "Namorambe": ["Namorambe", "Batu Penjem Jem", "Delitua", "Kuta Tengah"],
            "Pancur Batu": ["Pancur Batu", "Baru", "Durin Simbelang", "Tanjung Anom"],
            "Pantai Cermin": ["Pantai Cermin Kiri", "Pantai Cermin Kanan", "Kuala Lama"],
            "Pematang Johar": ["Pematang Johar", "Tanjung Selamat"],
            "Percut Sei Tuan": ["Percut", "Bandar Klippa", "Kenangan", "Sampali", "Tembung", "Tanjung Selamat"],
            "Sinembah Tanjung Muda Hilir": ["Talenken", "Sungkut", "Ujung Deleng"],
            "Sinembah Tanjung Muda Hulu": ["Tanjung Muda", "Kutambaru", "Tiga Juhar"],
            "Sunggal": ["Sunggal Kanan", "Helvetia", "Muliorejo", "Puji Mulyo", "Sei Semayang"],
            "Tanjung Morawa": ["Tanjung Morawa A", "Tanjung Morawa B", "Buntu Bedimbar", "Dalu X A", "Dalu X B"],
            "Tembung": ["Tembung Pasar", "Tembung Kota"],
            "Sibolangit": ["Sibolangit", "Bandar Baru", "Rempah", "Suka Maju"]
        }

        print("🌱 Memulai seeding data Kecamatan & Desa Deli Serdang...")

        for nama_kec, daftar_desa in data_wilayah.items():
            # Cek apakah kecamatan sudah ada
            kec = db.query(Kecamatan).filter(Kecamatan.nama_kecamatan == nama_kec).first()
            if not kec:
                kec = Kecamatan(nama_kecamatan=nama_kec)
                db.add(kec)
                db.commit()
                db.refresh(kec)
                print(f"  [+] Kecamatan ditambahkan: {nama_kec}")

            for nama_desa in daftar_desa:
                desa_exist = db.query(Desa).filter(Desa.id_kecamatan == kec.id, Desa.nama_desa == nama_desa).first()
                if not desa_exist:
                    desa = Desa(id_kecamatan=kec.id, nama_desa=nama_desa)
                    db.add(desa)
            
            db.commit()

        print("✅ Seeding Wilayah Deli Serdang Selesai!")

    except Exception as e:
        db.rollback()
        print(f"❌ Gagal Seeding Wilayah: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_deli_serdang()