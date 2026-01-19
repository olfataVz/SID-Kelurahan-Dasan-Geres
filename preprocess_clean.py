import pandas as pd
import numpy as np

INPUT_PATH = "Kelurahan-Dasan-Geres.csv"
OUTPUT_PATH = "Kelurahan-Dasan-Geres_FINAL.csv"


def clean_dusun(x):
    if pd.isna(x):
        return "TIDAK DIKETAHUI"
    x = str(x).strip().upper()
    x = x.replace("DASN GERES", "DASAN GERES")
    x = x.replace("CEMARE", "CEMARA")
    return x


def clean_status_kawin(x):
    if pd.isna(x):
        return "TIDAK DIKETAHUI"

    x = str(x).strip().upper()
    x = x.replace("`", "").replace("-", " ").strip()

    # typo umum
    x = x.replace("BELUM  KAWIN", "BELUM KAWIN")
    x = x.replace("BELUMKAWIN", "BELUM KAWIN")
    x = x.replace("BLUM KAWIN", "BELUM KAWIN")
    x = x.replace("BELEM KAWIN", "BELUM KAWIN")
    x = x.replace("BEKUM KAWIN", "BELUM KAWIN")
    x = x.replace("BWLUM KAWIN", "BELUM KAWIN")

    x = x.replace("KAWN", "KAWIN")
    x = x.replace("KWIN", "KAWIN")
    x = x.replace("KAWWIN", "KAWIN")
    x = x.replace("KAWIU", "KAWIN")
    x = x.replace("KAWI", "KAWIN")
    x = x.replace("KAIN", "KAWIN")
    x = x.replace("KAWAIN", "KAWIN")
    x = x.replace("KAWAN", "KAWIN")
    x = x.replace("KAWIN KAWIN", "KAWIN")

    # kategori final
    if "BELUM" in x:
        return "BELUM KAWIN"
    if "KAWIN" in x:
        return "KAWIN"
    if "CERAI HIDUP" in x:
        return "CERAI HIDUP"
    if "CERAI MATI" in x:
        return "CERAI MATI"
    if x in ["JANDA", "DUDA"]:
        return "JANDA/DUDA"
    if "CERAI" in x:
        return "CERAI HIDUP"
    if x in ["", "NAN", "NONE"]:
        return "TIDAK DIKETAHUI"

    return "LAINNYA"


def kelompok_umur(umur):
    if pd.isna(umur):
        return "Tidak diketahui"
    try:
        umur = int(umur)
    except:
        return "Tidak diketahui"

    if umur <= 5: return "0-5"
    if umur <= 12: return "6-12"
    if umur <= 17: return "13-17"
    if umur <= 25: return "18-25"
    if umur <= 40: return "26-40"
    if umur <= 60: return "41-60"
    return "60+"


def main():
    df = pd.read_csv(INPUT_PATH, low_memory=False)

    # ====== 1) Dusun bersih ======
    if "dusun" in df.columns:
        df["dusun_clean"] = df["dusun"].apply(clean_dusun)

    # ====== 2) Status kawin bersih ======
    if "status_kawin" in df.columns:
        df["status_kawin_clean"] = df["status_kawin"].apply(clean_status_kawin)

    # ====== 3) Jenis kelamin bersih ======
    if "sex" in df.columns:
        df["sex_clean"] = df["sex"].astype(str).str.strip().str.upper()
        df["sex_clean"] = df["sex_clean"].replace({
            "LAKI-LAKI": "L",
            "PEREMPUAN": "P"
        })

    # ====== 4) Tanggal lahir + umur ======
    if "tanggallahir" in df.columns:
        df["tanggallahir"] = pd.to_datetime(df["tanggallahir"], errors="coerce")

        today = pd.Timestamp.today()
        df["umur"] = (today - df["tanggallahir"]).dt.days // 365
        df["kelompok_umur"] = df["umur"].apply(kelompok_umur)

    # ====== 5) no_kk dibuat string biar rapi ======
    if "no_kk" in df.columns:
        df["no_kk"] = df["no_kk"].apply(lambda x: str(int(x)) if pd.notna(x) else np.nan)

    # simpan output
    df.to_csv(OUTPUT_PATH, index=False)
    print("✅ Selesai!")
    print("Output:", OUTPUT_PATH)
    print("Ukuran data:", df.shape)


if __name__ == "__main__":
    main()
