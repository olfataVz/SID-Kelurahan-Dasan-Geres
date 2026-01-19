import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Dashboard SID - Kelurahan Dasan Geres",
    layout="wide"
)

DATA_PATH = "Kelurahan-Dasan-Geres_FINAL.csv"

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, low_memory=False)
    return df

df = load_data(DATA_PATH)

# =========================
# SIDEBAR FILTER
# =========================
st.sidebar.title("⚙️ Filter Data")

dusun_list = sorted(df["dusun_clean"].dropna().unique().tolist())
rt_list = sorted(df["rt"].dropna().unique().tolist())
sex_list = sorted(df["sex_clean"].dropna().unique().tolist())

dusun_pick = st.sidebar.multiselect("Pilih Dusun", dusun_list, default=dusun_list)
rt_pick = st.sidebar.multiselect("Pilih RT", rt_list, default=rt_list)
sex_pick = st.sidebar.multiselect("Pilih Jenis Kelamin", sex_list, default=sex_list)

filtered = df[
    (df["dusun_clean"].isin(dusun_pick)) &
    (df["rt"].isin(rt_pick)) &
    (df["sex_clean"].isin(sex_pick))
].copy()

st.sidebar.markdown("---")
st.sidebar.write("📌 Baris terfilter:", len(filtered))

# =========================
# HEADER
# =========================
st.title("📊 Dashboard Sistem Informasi Desa")
st.caption("Kelurahan Dasan Geres — Statistik Kependudukan dan Wilayah")

# =========================
# KPI SECTION
# =========================
total_penduduk = len(filtered)
total_dusun = filtered["dusun_clean"].nunique()
total_rt = filtered["rt"].nunique()

total_kk = filtered["no_kk"].nunique(dropna=True)
nik_terisi = filtered["nik"].notna().mean() * 100
tgl_terisi = filtered["tanggallahir"].notna().mean() * 100

laki = (filtered["sex_clean"] == "L").sum()
perempuan = (filtered["sex_clean"] == "P").sum()

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Penduduk", f"{total_penduduk:,}")
with col2:
    st.metric("Dusun", total_dusun)
with col3:
    st.metric("RT", total_rt)
with col4:
    st.metric("Jumlah KK", f"{total_kk:,}")
with col5:
    st.metric("NIK Terisi", f"{nik_terisi:.1f}%")
with col6:
    st.metric("Tgl Lahir Terisi", f"{tgl_terisi:.1f}%")

st.markdown("---")

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Overview",
    "📍 Wilayah",
    "👥 Demografi",
    "🎓 Pendidikan & Pekerjaan",
    "🔎 Cari Penduduk",
    "✅ Data Quality"
])

# =========================
# TAB 1: OVERVIEW
# =========================
with tab1:
    st.subheader("Ringkasan Kependudukan")

    c1, c2 = st.columns([1.3, 1])

    with c1:
        dusun_count = filtered["dusun_clean"].value_counts().reset_index()
        dusun_count.columns = ["Dusun", "Jumlah Penduduk"]

        fig = px.bar(
            dusun_count,
            x="Dusun",
            y="Jumlah Penduduk",
            title="Jumlah Penduduk per Dusun",
            text="Jumlah Penduduk"
        )
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        sex_count = filtered["sex_clean"].value_counts().reset_index()
        sex_count.columns = ["Jenis Kelamin", "Jumlah"]

        fig = px.pie(
            sex_count,
            names="Jenis Kelamin",
            values="Jumlah",
            title="Komposisi Jenis Kelamin",
            hole=0.45
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================
# TAB 2: WILAYAH
# =========================
with tab2:
    st.subheader("Analisis Wilayah (Dusun vs RT)")

    c1, c2 = st.columns([1.2, 1])

    with c1:
        rt_count = filtered.groupby(["dusun_clean", "rt"]).size().reset_index(name="Jumlah Penduduk")

        fig = px.bar(
            rt_count,
            x="rt",
            y="Jumlah Penduduk",
            color="dusun_clean",
            barmode="group",
            title="Jumlah Penduduk per RT (berdasarkan Dusun)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        pivot = filtered.pivot_table(
            index="dusun_clean",
            columns="rt",
            values="nama",
            aggfunc="count",
            fill_value=0
        )

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues", ax=ax)
        ax.set_title("Heatmap Jumlah Penduduk (Dusun vs RT)")
        ax.set_xlabel("RT")
        ax.set_ylabel("Dusun")
        st.pyplot(fig)

# =========================
# TAB 3: DEMOGRAFI
# =========================
with tab3:
    st.subheader("Demografi Penduduk")

    c1, c2, c3 = st.columns(3)

    with c1:
        order = ["0-5","6-12","13-17","18-25","26-40","41-60","60+","Tidak diketahui"]
        umur_count = filtered["kelompok_umur"].fillna("Tidak diketahui").value_counts().reset_index()
        umur_count.columns = ["Kelompok Umur", "Jumlah"]
        umur_count["Kelompok Umur"] = pd.Categorical(umur_count["Kelompok Umur"], categories=order, ordered=True)
        umur_count = umur_count.sort_values("Kelompok Umur")

        fig = px.bar(
            umur_count,
            x="Kelompok Umur",
            y="Jumlah",
            title="Distribusi Kelompok Umur",
            text="Jumlah"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        kawin_count = filtered["status_kawin_clean"].fillna("TIDAK DIKETAHUI").value_counts().reset_index()
        kawin_count.columns = ["Status Kawin", "Jumlah"]

        fig = px.bar(
            kawin_count,
            x="Status Kawin",
            y="Jumlah",
            title="Distribusi Status Kawin (Clean)",
            text="Jumlah"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        if "agama" in filtered.columns:
            agama_count = filtered["agama"].fillna("Tidak diketahui").value_counts().reset_index()
            agama_count.columns = ["Agama", "Jumlah"]

            fig = px.pie(
                agama_count,
                names="Agama",
                values="Jumlah",
                title="Komposisi Agama",
                hole=0.45
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Kolom 'agama' tidak ditemukan.")

# =========================
# TAB 4: PENDIDIKAN & PEKERJAAN
# =========================
with tab4:
    st.subheader("Pendidikan & Pekerjaan (Top 10)")

    c1, c2 = st.columns(2)

    with c1:
        if "pendidikan_kk" in filtered.columns:
            pendidikan_count = filtered["pendidikan_kk"].fillna("Tidak diketahui").value_counts().head(10).reset_index()
            pendidikan_count.columns = ["Pendidikan", "Jumlah"]

            fig = px.bar(
                pendidikan_count,
                x="Jumlah",
                y="Pendidikan",
                orientation="h",
                title="Top 10 Pendidikan",
                text="Jumlah"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Kolom 'pendidikan_kk' tidak ditemukan.")

    with c2:
        if "pekerjaan" in filtered.columns:
            pekerjaan_count = filtered["pekerjaan"].fillna("Tidak diketahui").value_counts().head(10).reset_index()
            pekerjaan_count.columns = ["Pekerjaan", "Jumlah"]

            fig = px.bar(
                pekerjaan_count,
                x="Jumlah",
                y="Pekerjaan",
                orientation="h",
                title="Top 10 Pekerjaan",
                text="Jumlah"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Kolom 'pekerjaan' tidak ditemukan.")

# =========================
# TAB 5: CARI PENDUDUK
# =========================
with tab5:
    st.subheader("Pencarian Data Penduduk")

    c1, c2 = st.columns([1, 1])
    with c1:
        search_name = st.text_input("Cari Nama (opsional)", "")
    with c2:
        search_nik = st.text_input("Cari NIK (opsional)", "")

    df_search = filtered.copy()

    if search_name.strip() != "":
        df_search = df_search[df_search["nama"].astype(str).str.contains(search_name, case=False, na=False)]

    if search_nik.strip() != "":
        df_search = df_search[df_search["nik"].astype(str).str.contains(search_nik, case=False, na=False)]

    show_cols = [
        "nama", "nik", "sex_clean", "dusun_clean", "rt",
        "status_kawin_clean", "tanggallahir", "umur",
        "agama", "pendidikan_kk", "pekerjaan"
    ]
    show_cols = [c for c in show_cols if c in df_search.columns]

    st.dataframe(df_search[show_cols], use_container_width=True, height=420)

    csv = df_search[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Hasil Filter (CSV)",
        data=csv,
        file_name="hasil_filter_penduduk.csv",
        mime="text/csv"
    )

# =========================
# TAB 6: DATA QUALITY
# =========================
with tab6:
    st.subheader("Kualitas Data (Missing Value)")

    missing = filtered.isna().mean().sort_values(ascending=False) * 100
    missing_df = missing.reset_index()
    missing_df.columns = ["Kolom", "Missing (%)"]

    c1, c2 = st.columns([1.2, 1])

    with c1:
        fig = px.bar(
            missing_df.head(20),
            x="Missing (%)",
            y="Kolom",
            orientation="h",
            title="Top 20 Kolom dengan Missing Value Terbanyak",
            text="Missing (%)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        kosong_total = missing_df[missing_df["Missing (%)"] == 100]
        st.write("📌 Kolom Kosong Total (100% missing):")
        st.dataframe(kosong_total, use_container_width=True, height=320)

st.markdown("---")
st.caption("📌 Dashboard ini dibuat dari dataset final hasil clean untuk kebutuhan Sistem Informasi Desa.")
