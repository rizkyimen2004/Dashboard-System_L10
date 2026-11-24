"""WIREQ - Wire Quality Monitoring System | PT Surabaya Wire | Steel Wire Nail L10.  Jalankan: streamlit run streamlit_app.py"""
import math, re
import numpy as np, pandas as pd, plotly.graph_objects as go, streamlit as st
from scipy.stats import norm, chi2

st.set_page_config(page_title="WIREQ · Wire Quality Monitoring System", page_icon="🔩", layout="wide")
NAVY, AMBER, RED, GREEN, BLUE = "#0C4A6E", "#F59E0B", "#EF4444", "#10B981", "#0EA5E9"
st.markdown("""<style>
.stApp{background:#F0F9FF}.block-container{padding-top:1.4rem;max-width:1280px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#E0F2FE,#BAE6FD)}[data-testid="stSidebar"] *{color:#0C4A6E}
.hero{background:linear-gradient(135deg,#0284C7 0%,#0EA5E9 55%,#22D3EE 100%);border-radius:14px;padding:46px 50px;color:#fff;position:relative;overflow:hidden}
.hero:before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(115deg,rgba(255,255,255,.05) 0 2px,transparent 2px 24px)}
.hero>*{position:relative}.hero h1{text-shadow:0 2px 10px rgba(3,105,161,.35);font-size:56px;letter-spacing:8px;margin:0;color:#fff}
.hero .sub{letter-spacing:3px;font-size:13px;color:#FEF3C7;margin-top:2px}.hero .tag{font-size:21px;margin-top:18px;font-weight:600}
.hero p{max-width:720px;color:#D5E1EC;margin-top:10px}.pill{display:inline-block;border:1px solid rgba(255,255,255,.45);border-radius:20px;padding:3px 14px;font-size:12px;letter-spacing:1px}
.sec{border-left:5px solid #F59E0B;padding-left:12px;margin:28px 0 12px;font-size:21px;font-weight:700;color:#0C4A6E}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}
.card{background:#fff;border:1px solid #BAE6FD;border-radius:12px;padding:15px 18px;box-shadow:0 1px 3px rgba(11,42,67,.06)}
.card h4{margin:0 0 5px;color:#0C4A6E;font-size:15px}.card p{margin:0;color:#4A5B6B;font-size:13.5px;line-height:1.5}
.step .no{display:inline-block;background:#0C4A6E;color:#fff;border-radius:6px;padding:2px 9px;font-size:12px;font-weight:700;letter-spacing:1px;margin-bottom:8px}
.kpi{background:#fff;border:1px solid #BAE6FD;border-top:4px solid #0EA5E9;border-radius:12px;padding:14px 18px}
.kpi .l{font-size:12px;color:#6B7B8A;letter-spacing:.6px;text-transform:uppercase}.kpi .v{font-size:27px;font-weight:700;color:#0C4A6E;margin-top:2px}.kpi .s{font-size:12px;color:#6B7B8A}
.box{border-left:5px solid;border-radius:6px;padding:10px 14px;margin:6px 0;background:#fff;border-top:1px solid #BAE6FD;border-right:1px solid #BAE6FD;border-bottom:1px solid #BAE6FD;color:#1C2733}
</style>""", unsafe_allow_html=True)

FAKTOR = 4926 / 30; CAT = ["KTC", "K-", "UC", "BC"]
AB = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
MON = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
MI = dict(jan=0, feb=1, mar=2, apr=3, mei=4, may=4, jun=5, jul=6, agu=7, aug=7, sep=8, okt=9, oct=9, nov=10, des=11, dec=11)
DEMO = [["Jan 2024",1,1142605,1806,0,1205,0],["Feb 2024",1,882406,1221,419,0,0],["Mar 2024",1,882329,677,0,0,0],["Apr 2024",1,598873,0,0,0,547],["Mei 2024",1,926591,3100,0,584,0],["Jun 2024",1,866858,622,0,789,0],["Jul 2024",1,1055019,0,670,688,0],["Agu 2024",1,1017862,568,0,1848,626],["Sep 2024",1,909643,1379,1128,598,0],["Okt 2024",1,1135519,636,0,1924,694],["Nov 2024",1,978176,0,1158,637,0],["Des 2024",1,876531,620,610,0,0],["Jan 2025",1,949057,1197,578,0,0],["Feb 2025",1,950099,0,0,1105,0],["Mar 2025",1,997630,0,0,0,536],["Apr 2025",1,772453,0,0,566,679],["Mei 2025",1,952963,0,0,1064,621],["Jun 2025",1,849628,0,0,0,1195],["Jul 2025",1,1168833,1800,647,511,0],["Agu 2025",1,1043728,2537,607,598,0],["Sep 2025",1,998330,1071,0,1294,0],["Nov 2025",2,1031962,596,0,1861,0],["Des 2025",2,784868,0,0,1170,0],["Jan 2026",2,259036,1839,623,559,0],["Feb 2026",2,244298,0,0,1270,0],["Mar 2026",2,227898,595,1185,0,0],["Apr 2026",2,310140,0,0,0,606],["Mei 2026",2,244093,2433,0,1178,0],["Jun 2026",2,248199,1680,1143,1651,0]]
PAGES = ["1 · User Guide", "2 · Quality Control Analysis"]

def fm(v, d=0): return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
def H(x): st.markdown(x, unsafe_allow_html=True)
def sec(t): H(f'<div class="sec">{t}</div>')
def card(t, p, cls=""): return f'<div class="card {cls}"><h4>{t}</h4><p>{p}</p></div>'
def box(t, color): H(f'<div class="box" style="border-left-color:{color}">{re.sub(r"[*][*](.+?)[*][*]", r"<b>\1</b>", t)}</div>')
def kpi(l, v, s="", c=BLUE): return f'<div class="kpi" style="border-top-color:{c}"><div class="l">{l}</div><div class="v">{v}</div><div class="s">{s}&nbsp;</div></div>'

def pn(v):
    if pd.isna(v): return None
    if hasattr(v, "month") and hasattr(v, "year"): return f"{AB[v.month - 1]} {v.year}"
    s = str(v).strip().lower(); m = re.match(r"(\d{4})-(\d{1,2})", s)
    if m and 1 <= int(m[2]) <= 12: return f"{AB[int(m[2]) - 1]} {m[1]}"
    m = re.search(r"([a-z]{3})[a-z]*\.?\s*[-/]?\s*'?(\d{4})", s)
    return f"{AB[MI[m[1]]]} {m[2]}" if m and m[1] in MI else None

def normalize(raw):
    err, warn = [], []
    def key(pat, srch=False):
        f = re.search if srch else re.match
        return next((c for c in raw.columns if f(pat, re.sub(r"[\s_]", "", str(c).lower()))), None)
    cp, cs, cn, cd, cf = key(r"(periode|tanggal|date|bulan|period)"), key(r"(subgroup|subgrup|nosub|nomor)"), key(r"(produksi|sampel|ukuran|n$)"), key(r"(cacat|defect)", True), key(r"(fase|phase)")
    ck = {c: key(p) for c, p in zip(CAT, [r"ktc", r"k[-−–]", r"uc", r"bc"])}
    if cp is None: err.append("Kolom periode/tanggal tidak ditemukan (contoh nama kolom: Periode, Tanggal).")
    if cn is None: err.append("Kolom jumlah produksi/ukuran sampel tidak ditemukan (contoh: Produksi, Sampel).")
    if cd is None and not all(ck.values()): err.append("Kolom jumlah cacat tidak ditemukan (contoh: Cacat, atau kolom KTC, K-, UC, BC).")
    if err: return None, err, warn
    df = pd.DataFrame({"Periode": raw[cp].map(pn), "n": pd.to_numeric(raw[cn], errors="coerce")})
    df["Subgroup"] = pd.to_numeric(raw[cs], errors="coerce") if cs else np.nan
    for c in CAT: df[c] = pd.to_numeric(raw[ck[c]], errors="coerce") if ck[c] else np.nan
    cat_sum = df[CAT].sum(axis=1, min_count=1)
    df["d"] = pd.to_numeric(raw[cd], errors="coerce").fillna(cat_sum) if cd else cat_sum
    df["Fase"] = raw[cf].map(lambda v: 2 if re.search(r"2|ii", str(v), re.I) else 1) if cf else np.nan
    bad = df.Periode.isna() | ~(df.n > 0) | df.d.isna()
    if bad.any(): warn.append(f"{int(bad.sum())} baris dilewati (periode tidak terbaca, produksi ≤ 0, atau cacat kosong).")
    df = df[~bad]; wrong = (df.d > df.n) | (df.d < 0)
    if wrong.any(): warn.append(f"{int(wrong.sum())} baris dilewati (cacat negatif atau lebih besar dari produksi).")
    df = df[~wrong]
    if len(df) < 6: return None, [f"Data valid hanya {len(df)} subgroup; minimal 6 diperlukan."], warn
    df["y"] = df.Periode.str[4:].astype(int); df["m"] = df.Periode.str[:3].map(AB.index)
    df["Subgroup"] = df.Subgroup.fillna(df.groupby("Periode").cumcount() + 1)
    df = df.sort_values(["y", "m", "Subgroup"]).reset_index(drop=True)
    df["Label"] = np.where(df.duplicated("Periode", keep=False), df.Periode + " #" + df.Subgroup.astype(int).astype(str), df.Periode)
    return df, err, warn

def pchart(df, mode, revise):
    p = (df.d / df.n).to_numpy(); N = df.N.to_numpy(); D = df.D.to_numpy()
    base = np.where(df.Fase == 1)[0] if df.Fase.notna().any() else np.arange(len(df))
    if df[CAT].notna().all().all() and df[CAT].sum().sum() > 0:
        pb = np.sort(np.maximum(df.loc[base, CAT].div(df.loc[base, "n"], axis=0).mean().to_numpy(), 1e-12)); nC = int(math.ceil(max(5 / pb[1], 1 / pb[0])))
    else: nC = int(math.ceil(5 / max(p[base].mean(), 1e-9)))
    nof = np.full(len(df), float(nC)) if mode == "fixed" else N
    idx = base.copy(); rem = []; ok = True
    for _ in range(11):
        pbar = D[idx].sum() / N[idx].sum(); ooc = np.abs(p[idx] - pbar) > 3 * np.sqrt(pbar * (1 - pbar) / nof[idx]); ok = not ooc.any()
        if ok or not revise or len(idx) - ooc.sum() < 5: break
        rem += list(df.Label[idx[ooc]]); idx = idx[~ooc]
    w = 3 * np.sqrt(pbar * (1 - pbar) / nof)
    return dict(pbar=pbar, ucl=pbar + w, lcl=np.maximum(0, pbar - w), p=p, rem=rem, ok=ok, nC=nC, used=len(idx), nbase=len(base), nof=nof, base=base)

def find_runs(p, cl, lab, n=7):
    s_ = np.sign(p - cl); out = []; i = 0
    while i < len(p):
        j = i
        while j + 1 < len(p) and s_[j + 1] == s_[i]: j += 1
        if s_[i] != 0 and j - i + 1 >= n: out.append(f"{j - i + 1} titik berturut-turut {'di atas' if s_[i] > 0 else 'di bawah'} CL ({lab[i]} – {lab[j]})")
        i = j + 1
    return out

def find_trends(p, lab, n=6):
    d_ = np.sign(np.diff(p)); out = []; i = 0
    while i < len(d_):
        j = i
        while j + 1 < len(d_) and d_[j + 1] == d_[i]: j += 1
        if d_[i] != 0 and j - i + 1 >= n - 1: out.append(f"tren {'naik' if d_[i] > 0 else 'turun'} {j - i + 2} titik ({lab[i]} – {lab[j + 1]})")
        i = j + 1
    return out

def capcat(x): return "Capable" if x >= 1.33 else "Marginal" if x >= 1 else "Not Capable"

# ================================================================= sidebar
st.session_state.setdefault("page", PAGES[0])
H('<div style="font-size:30px;font-weight:800;letter-spacing:6px;color:#0369A1">WIREQ</div><div style="font-size:11px;letter-spacing:2px;color:#D97706;margin-bottom:14px">WIRE QUALITY MONITORING SYSTEM</div>')
page = st.sidebar.radio("Navigasi", PAGES, key="page"); st.sidebar.caption("PT Surabaya Wire · Steel Wire Nail L10")

# ================================================================= PAGE 1
if page == PAGES[0]:
    H('<div class="hero"><span class="pill">STEEL WIRE NAIL · L10</span><h1>WIREQ</h1><div class="sub">WIRE QUALITY MONITORING SYSTEM</div>'
      '<div class="tag">Monitor Quality. Control Process. Improve Performance.</div>'
      '<p>Sistem monitoring kualitas produksi paku kawat baja L10 di PT Surabaya Wire. Unggah data produksi, analisis kestabilan proses dengan Statistical Process Control, lalu tandai penyimpangan yang perlu ditindaklanjuti.</p></div>')
    sec("About the Dashboard")
    H('<div class="grid">' + "".join(card(t, p) for t, p in [("Memantau Kualitas", "Melihat jumlah produksi, cacat, dan produk baik tiap periode."), ("Analisis Proporsi Cacat", "Menghitung proporsi cacat tiap subgroup."), ("Kestabilan Proses", "Mengevaluasi apakah proses berada dalam batas kendali statistik."), ("Penelusuran Penyimpangan", "Menandai subgroup di luar batas kendali untuk ditindaklanjuti bersama QC."), ("Dukungan Keputusan", "Memberi dasar data untuk tindak lanjut pengendalian kualitas.")]) + "</div>")
    sec("Understanding the Analysis")
    a, b = st.columns([1.05, 1])
    with a:
        H('<div class="grid" style="grid-template-columns:1fr 1fr">' + "".join(card(t, p) for t, p in [
            ("Statistical Process Control", "Metode statistik untuk membedakan variasi wajar proses dari penyimpangan yang perlu diselidiki."),
            ("P-Chart", "Peta kendali untuk proporsi cacat: pᵢ = dᵢ / nᵢ. Batas kendali menyesuaikan ukuran sampel."),
            ("Central Line (CL)", "Rata-rata proporsi cacat proses: p̄ = total cacat / total produksi."),
            ("Upper Control Limit", "UCL = p̄ + 3√[p̄(1−p̄)/n]. Titik di atasnya menandakan pemburukan."),
            ("Lower Control Limit", "LCL = max(0, p̄ − 3√[p̄(1−p̄)/n]). Titik di bawahnya perlu ditelusuri, meski tampak baik."),
            ("Out of Control", "Titik di luar UCL/LCL: ada kemungkinan penyebab khusus yang mengubah proses.")]) + "</div>")
    with b:
        xs = list(range(1, 15)); ys = [20, 22, 19, 21, 18, 23, 20, 34, 21, 19, 22, 20, 6, 21]; out = [y > 33 or y < 9 for y in ys]
        f = go.Figure()
        for n, v, c, dsh in [("UCL", 33, RED, "dash"), ("CL", 21, GREEN, "solid"), ("LCL", 9, RED, "dash")]: f.add_trace(go.Scatter(x=[1, 14], y=[v, v], mode="lines", name=n, line=dict(color=c, dash=dsh)))
        f.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", name="Proporsi cacat", line=dict(color=BLUE, width=1.5), marker=dict(size=9, color=[RED if o else BLUE for o in out], symbol=["diamond" if o else "circle" for o in out])))
        f.add_annotation(x=8, y=34, text="Di luar batas", ax=40, ay=-25, arrowcolor=RED, font=dict(color=RED)); f.add_annotation(x=5, y=18, text="Di dalam batas", ax=0, ay=40, arrowcolor=BLUE, font=dict(color=BLUE))
        f.update_layout(title="Ilustrasi cara membaca P-Chart (data contoh)", height=360, margin=dict(l=40, r=10, t=50, b=30), legend=dict(orientation="h", y=-0.12), yaxis_title="% cacat", template="plotly_white")
        st.plotly_chart(f, width="stretch")
    sec("How to Use WIREQ")
    H('<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(180px,1fr))">' + "".join(card(f'<span class="no">STEP {i:02d}</span><br>{t}', p, "step") for i, (t, p) in enumerate([
        ("Upload Data", "Unggah file Excel atau CSV berisi data produksi (atau pakai data contoh/input manual)."), ("Select Period", "Pilih bulan dan tahun yang akan dianalisis."),
        ("Generate Analysis", "Sistem menghitung proporsi cacat dan batas kendali otomatis."), ("Evaluate Process", "Baca P-Chart: apakah proses terkendali atau tidak."),
        ("Follow Up", "Jika tidak terkendali, tindak lanjuti subgroup yang ditandai bersama QC dan lapangan.")], 1)) + "</div>")
    st.write(""); st.button("START ANALYSIS", type="primary", on_click=lambda: st.session_state.update(page=PAGES[1]))
    st.stop()

# ================================================================= PAGE 2
H('<div style="font-size:28px;font-weight:800;color:#0C4A6E;letter-spacing:1px">Quality Control Analysis</div><div style="color:#6B7B8A;margin-bottom:6px">WIREQ · Steel Wire Nail L10 · PT Surabaya Wire</div>')
sec("A. Data Management")
src = st.radio("Sumber data", ["Dataset contoh (data notebook L10)", "Upload Excel / CSV", "Input manual"], horizontal=True)
unit = st.radio("Satuan data produksi & cacat", ["kg (dikonversi 164,2 biji/kg)", "biji / unit"], horizontal=True, index=0 if src.startswith("Dataset") else 1, key="u" + src)
raw = None
if src.startswith("Dataset"):
    raw = pd.DataFrame(DEMO, columns=["Periode", "Fase", "Produksi"] + CAT); raw["Subgroup"] = range(1, len(raw) + 1); raw["Cacat"] = raw[CAT].sum(axis=1)
elif src.startswith("Upload"):
    up = st.file_uploader("File data (.xlsx / .csv)", type=["xlsx", "xls", "csv"])
    st.caption("Kolom minimal: Periode/Tanggal, Subgroup (opsional), Produksi (ukuran sampel), Cacat. Opsional: KTC, K-, UC, BC, Fase (1/2).")
    if up is not None:
        try: raw = pd.read_csv(up) if up.name.lower().endswith(".csv") else pd.read_excel(up)
        except Exception as e: st.error(f"File tidak dapat dibaca: {e}")
else:
    tpl = pd.DataFrame({"Periode": pd.Series([None] * 8, dtype="object"), "Subgroup": pd.Series([None] * 8, dtype="float"), "Produksi": pd.Series([None] * 8, dtype="float"), "Cacat": pd.Series([None] * 8, dtype="float"),
                        **{c: pd.Series([None] * 8, dtype="float") for c in CAT}})
    st.caption("Isi tabel (contoh periode: Jan 2024). Kolom Cacat boleh kosong jika KTC, K-, UC, BC diisi. Tambah baris dengan baris kosong paling bawah. Minimal 6 subgroup.")
    raw = st.data_editor(tpl, num_rows="dynamic", width="stretch", key="manual")
if raw is None:
    st.info("Pilih atau unggah data untuk memulai analisis."); st.stop()
df, errs, warns = normalize(raw)
for w in warns: st.warning(w)
if errs:
    for e in errs: st.error(e)
    st.stop()
f = FAKTOR if unit.startswith("kg") else 1.0
df["N"] = df.n * f; df["D"] = df.d * f
uni = "kg" if unit.startswith("kg") else "unit"
st.success(f"Struktur data valid: {len(df)} subgroup · {df.Periode.nunique()} periode" + (" · kolom Fase terbaca" if df.Fase.notna().any() else " · tanpa kolom Fase (seluruh data jadi baseline)") + (" · kategori cacat tersedia" if df[CAT].notna().all().all() else ""))
with st.expander("Preview data (10 baris pertama)"): st.dataframe(df[["Periode", "Subgroup", "n", "d"] + CAT + (["Fase"] if df.Fase.notna().any() else [])].head(10), hide_index=True, width="stretch")

sec("B. Filter Analysis")
c = st.columns(4); years = sorted(df.y.unique())
yr = c[0].selectbox("Tahun produksi", years, index=years.index(2024) if 2024 in years else 0)
mo = c[1].selectbox("Bulan produksi", range(12), format_func=lambda i: MON[i])
mode = c[2].selectbox("Ukuran sampel batas kendali", ["fixed", "actual"], format_func=lambda x: "Tetap (Cochran, sesuai Bab 2)" if x == "fixed" else "Aktual per subgroup (nᵢ)")
rng = c[3].selectbox("Rentang grafik", ["Seluruh periode", "Tahun terpilih"])
revise = st.checkbox("Revisi batas kendali iteratif (titik di luar batas pada baseline dikeluarkan lalu batas dihitung ulang)", value=True)
P = pchart(df, mode, revise)
df["p"] = P["p"] * 100; df["CL"] = P["pbar"] * 100; df["UCL"] = P["ucl"] * 100; df["LCL"] = P["lcl"] * 100
df["Status"] = np.where(P["p"] > P["ucl"], "OOC ▲ di atas UCL", np.where(P["p"] < P["lcl"], "OOC ▼ di bawah LCL", "Terkendali"))
sm = df[(df.y == yr) & (df.m == mo)]; period = f"{AB[mo]} {yr}"
if mode == "actual" and (df.Status != "Terkendali").mean() > .6:
    st.warning("Pada mode nᵢ aktual, ukuran sampel sangat besar sehingga batas kendali sangat sempit dan hampir semua titik tampak di luar batas (overdispersi). Gunakan mode Tetap (Cochran) bila itu metode yang dipakai pada analisis.")

sec(f"C. Production Overview — {MON[mo]} {yr}")
if len(sm):
    T, Dd = sm.n.sum(), sm.d.sum()
    H('<div class="grid">' + kpi("Total Production", f"{fm(T)} {uni if uni == 'kg' else ''}") + kpi("Total Defect", f"{fm(Dd)} {uni if uni == 'kg' else ''}", c=RED) + kpi("Good Products", f"{fm(T - Dd)} {uni if uni == 'kg' else ''}", c=GREEN) + kpi("Defect Percentage", f"{fm(Dd / T * 100, 3)} %", f"CL proses {fm(P['pbar'] * 100, 3)} %", AMBER) + "</div>")
else: st.warning(f"Tidak ada data untuk {MON[mo]} {yr}.")

sec("D. Statistical Process Control — P-Chart")
st.caption(f"pᵢ = dᵢ/nᵢ · CL = p̄ = {fm(P['pbar'] * 100, 4)}% · UCL = p̄ + 3√[p̄(1−p̄)/nᵢ] · LCL = max(0, p̄ − 3√[p̄(1−p̄)/nᵢ]) · "
           + (f"n tetap Cochran = {fm(P['nC'])}" if mode == "fixed" else "nᵢ aktual (biji)") + f" · baseline {P['used']} dari {P['nbase']} subgroup" + (f" (dikeluarkan: {', '.join(P['rem'])})" if P["rem"] else "") + ("" if P["ok"] else " · belum konvergen"))
v = df if rng == "Seluruh periode" else df[df.y == yr]
fig = go.Figure()
for n, col, dsh in [("UCL", RED, "dash"), ("CL", GREEN, "solid"), ("LCL", RED, "dash")]: fig.add_trace(go.Scatter(x=v.Label, y=v[n], name=n, mode="lines", line=dict(color=col, dash=dsh, width=1.5), hoverinfo="skip"))
oc = v.Status != "Terkendali"
fig.add_trace(go.Scatter(x=v.Label, y=v.p, name="pᵢ (% cacat)", mode="lines+markers", line=dict(color=BLUE, width=1, dash="dot"), marker=dict(size=9, color=np.where(oc, "#E53935", BLUE), symbol=np.where(oc, "diamond", "circle")),
    customdata=np.c_[v.n, v.d, v.UCL, v.LCL, v.Status], hovertemplate="%{x}<br>pᵢ = %{y:.4f}%<br>nᵢ = %{customdata[0]:,.0f} · dᵢ = %{customdata[1]:,.0f}<br>UCL = %{customdata[2]:.4f}% · LCL = %{customdata[3]:.4f}%<br>%{customdata[4]}<extra></extra>"))
if len(sm): s2 = sm[sm.index.isin(v.index)]; fig.add_trace(go.Scatter(x=s2.Label, y=s2.p, name="Periode terpilih", mode="markers", hoverinfo="skip", marker=dict(size=19, symbol="circle-open", color=AMBER, line=dict(width=3))))
fig.update_layout(height=430, template="plotly_white", margin=dict(l=60, r=20, t=20, b=60), xaxis=dict(type="category", tickangle=-60), yaxis=dict(title="Proporsi cacat (%)"), legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig, width="stretch")
tb = v[["Label", "n", "d", "p", "LCL", "CL", "UCL", "Status"]].rename(columns={"Label": "Subgroup", "n": f"Produksi ({uni})", "d": f"Cacat ({uni})", "p": "pᵢ (%)"})
st.dataframe(tb.style.apply(lambda r: ["background-color:#FFF4D6;color:#000" if r.Subgroup in set(sm.Label) else ""] * len(r), axis=1).format({tb.columns[1]: "{:,.0f}", tb.columns[2]: "{:,.0f}", "pᵢ (%)": "{:.4f}", "LCL": "{:.4f}", "CL": "{:.4f}", "UCL": "{:.4f}"}), hide_index=True, width="stretch", height=300)
st.download_button("⬇ Unduh hasil perhitungan P-Chart (CSV)", tb.to_csv(index=False).encode("utf-8"), "wireq_hasil_pchart.csv", "text/csv")

sec("E. Advanced Analysis")
has_cat = bool(df[CAT].notna().all().all() and df[CAT].sum().sum() > 0)
runs_ = find_runs(P["p"], P["pbar"], df.Label.to_list()); trend_ = find_trends(P["p"], df.Label.to_list())
phs = {int(k): g.d.sum() / g.n.sum() * 100 for k, g in df.groupby("Fase")} if df.Fase.notna().any() else {}
BART = None
if has_cat:
    Pm = df.loc[P["base"], CAT].div(df.loc[P["base"], "n"], axis=0).to_numpy()
    if len(Pm) > 5 and np.all(Pm.std(axis=0) > 0):
        R = np.corrcoef(Pm, rowvar=False); dR = float(np.linalg.det(R)); n_, k_ = Pm.shape
        if dR > 0: chi = -((n_ - 1) - (2 * k_ + 5) / 6) * math.log(dR); fr = k_ * (k_ - 1) // 2; BART = dict(R=R, det=dR, chi=chi, df=fr, tab=chi2.ppf(.95, fr), p=chi2.sf(chi, fr), n=n_)
CAPR = None
t1, t2, t3, t4, t5 = st.tabs(["Indikator Lanjutan", "Pareto & Tren Cacat", "Pola Proses (Run Rules)", "Uji Bartlett", "Process Capability"])
with t1:
    if len(sm):
        z_ = ((P["p"][sm.index] - P["pbar"]) / np.sqrt(P["pbar"] * (1 - P["pbar"]) / P["nof"][sm.index])).mean()
        dpo = sm.D.sum() / (sm.N.sum() * 4); sg_ = norm.ppf(1 - dpo) + 1.5 if dpo > 0 else float("nan")
        H('<div class="grid">' + kpi("DPMO", fm(dpo * 1e6), "k = 4 jenis cacat") + kpi("Level Sigma", fm(sg_, 2), "sigma + 1,5 shift", "#10B981") + kpi("Jarak dari CL", f"{z_:+.2f} σ", "pᵢ terhadap p̄", "#F59E0B") + kpi("Rasio terhadap CL", f"{fm(sm.d.sum() / sm.n.sum() / P['pbar'], 2)} ×", "cacat periode ÷ CL", "#EF4444") + "</div>")
    if len(phs) == 2: st.dataframe(pd.DataFrame({"Fase": ["I (baseline)", "II (monitoring)"], "Cacat gabungan (%)": [phs[1], phs[2]]}).style.format({"Cacat gabungan (%)": "{:.4f}"}), hide_index=True)
    if len(phs) == 2: st.caption(f"Cacat Fase II adalah {fm(phs[2] / phs[1], 2)}× Fase I.")
with t2:
    if not has_cat: st.info("Kolom kategori cacat (KTC, K-, UC, BC) diperlukan untuk Pareto dan tren.")
    else:
        pc = st.columns(2)
        for col_, ttl, dd in [(pc[0], f"Pareto — {period}", sm), (pc[1], "Pareto — seluruh periode", df)]:
            tot = dd[CAT].sum().sort_values(ascending=False)
            if tot.sum() <= 0: col_.info("Tidak ada cacat pada data ini."); continue
            pf = go.Figure(go.Bar(x=tot.index, y=tot.values, marker_color=BLUE, name="Cacat")); pf.add_trace(go.Scatter(x=tot.index, y=(tot.cumsum() / tot.sum() * 100).values, yaxis="y2", mode="lines+markers", line=dict(color=AMBER), name="Kumulatif %"))
            pf.update_layout(title=ttl, height=320, template="plotly_white", margin=dict(l=40, r=40, t=50, b=30), yaxis2=dict(overlaying="y", side="right", range=[0, 105]), legend=dict(orientation="h", y=-0.15)); col_.plotly_chart(pf, width="stretch")
        tr = go.Figure([go.Bar(x=v.Label, y=v[c], name=c) for c in CAT]); tr.update_layout(barmode="stack", title="Tren cacat per kategori", height=340, template="plotly_white", margin=dict(l=40, r=10, t=50, b=60), xaxis=dict(type="category", tickangle=-60)); st.plotly_chart(tr, width="stretch")
with t3:
    st.caption("Aturan tambahan terhadap CL: ≥ 7 titik berturut-turut di satu sisi CL, atau tren naik/turun ≥ 6 titik, dapat menandakan pergeseran proses meski titik masih di dalam batas.")
    if runs_ or trend_:
        for t in runs_ + trend_: box("**Pola terdeteksi:** " + t, AMBER)
    else: box("**Tidak ada pola** run/tren yang terdeteksi.", GREEN)
with t4:
    if BART is None: st.info("Uji Bartlett memerlukan kolom KTC, K-, UC, BC dengan variasi yang cukup (minimal 6 subgroup baseline).")
    else:
        H('<div class="grid">' + kpi("|R|", fm(BART["det"], 6)) + kpi("χ² hitung", fm(BART["chi"], 3), f"db = {BART['df']} · n = {BART['n']}", "#F59E0B") + kpi("χ² tabel (5%)", fm(BART["tab"], 3), "", "#10B981") + kpi("p-value", fm(BART["p"], 4), "", "#EF4444") + "</div>")
        box(("**H0 tidak ditolak:** tidak ada korelasi signifikan antar kategori cacat; asumsi independensi dapat diterima" + (", dengan catatan p mendekati batas 0,05." if BART["p"] < .1 else ".")) if BART["chi"] < BART["tab"] else "**H0 ditolak:** ada korelasi signifikan antar kategori cacat; asumsi independensi dilanggar.", AMBER)
        hm = go.Figure(go.Heatmap(z=BART["R"], x=CAT, y=CAT, zmin=-1, zmax=1, colorscale="RdBu", text=np.round(BART["R"], 2), texttemplate="%{text}")); hm.update_layout(title="Matriks korelasi antar kategori (baseline)", height=340, margin=dict(l=40, r=10, t=50, b=30)); st.plotly_chart(hm, width="stretch")
with t5:
    st.caption("Cp/Cpk memerlukan data ukur karakteristik kualitas individual (mis. diameter) serta USL/LSL. Tidak dapat dihitung dari jumlah atau persentase cacat.")
    cc = st.columns([1, 1, 2]); usl = cc[0].number_input("USL", value=None, format="%.4f", placeholder="isi USL"); lsl = cc[1].number_input("LSL", value=None, format="%.4f", placeholder="isi LSL")
    mf = cc[2].file_uploader("Data ukur (kolom Periode, Nilai)", type=["xlsx", "xls", "csv"], key="meas"); why = []; vals = np.array([])
    if mf is None: why.append("Data ukur individual belum diunggah.")
    if usl is None or lsl is None: why.append("USL dan LSL belum diisi.")
    elif usl <= lsl: why.append("USL harus lebih besar dari LSL.")
    if mf is not None:
        try:
            mm = (pd.read_csv(mf) if mf.name.lower().endswith(".csv") else pd.read_excel(mf)).iloc[:, :2]; mm.columns = ["Periode", "Nilai"]; mm["Periode"] = mm.Periode.map(pn)
            vals = pd.to_numeric(mm.loc[mm.Periode == period, "Nilai"].astype(str).str.replace(",", "."), errors="coerce").dropna().to_numpy(float)
            if len(vals) < 2: why.append(f"Data ukur untuk {period} kurang dari 2 nilai.")
        except Exception as e: why.append(f"Data ukur tidak terbaca: {e}")
    if not why and not vals.std(ddof=1) > 0: why.append("Standar deviasi data ukur = 0.")
    if why:
        H('<div class="grid">' + kpi("Cp", "Not Available", "", "#64748B") + kpi("Cpk", "Not Available", "", "#64748B") + "</div>"); box("**Not Available.** " + " ".join(why), "#64748B")
    else:
        mu, sd = vals.mean(), vals.std(ddof=1); cp_ = (usl - lsl) / (6 * sd); cpk_ = min((usl - mu) / (3 * sd), (mu - lsl) / (3 * sd)); CAPR = dict(cp=cp_, cpk=cpk_)
        H('<div class="grid">' + kpi("Cp", fm(cp_, 3), capcat(cp_)) + kpi("Cpk", fm(cpk_, 3), capcat(cpk_), "#10B981") + kpi("USL", fm(usl, 3), "", "#F59E0B") + kpi("LSL", fm(lsl, 3), "", "#F59E0B") + "</div>")
        hh = go.Figure(go.Histogram(x=vals, marker_color=BLUE)); [hh.add_vline(x=x, line=dict(color=c, dash="dash"), annotation_text=t) for x, t, c in [(lsl, "LSL", RED), (usl, "USL", RED), (mu, "μ", GREEN)]]
        hh.update_layout(height=320, template="plotly_white", margin=dict(l=40, r=10, t=20, b=30)); st.plotly_chart(hh, width="stretch"); st.caption(f"n = {len(vals)} · μ = {fm(mu, 4)} · σ = {fm(sd, 4)}. Kategori: ≥ 1,33 Capable; 1,00–1,33 Marginal; < 1,00 Not Capable." + (" n < 30: estimasi kurang andal." if len(vals) < 30 else ""))

sec("F. Process Evaluation")
if len(sm):
    bad = sm[sm.Status != "Terkendali"]
    if bad.empty: box("**Process Stability:** Terkendali (in control). Semua titik pada periode ini berada di antara LCL dan UCL.", GREEN)
    else: box("**Process Stability:** Tidak terkendali. " + ", ".join(f"{r.Label}: {r.Status}" for r in bad.itertuples()) + ". Tindak lanjuti bersama QC.", RED)
n2 = df[df.Fase == 2] if df.Fase.notna().any() else df.iloc[0:0]
if len(n2): st.caption(f"Fase II: {(n2.Status != 'Terkendali').sum()} dari {len(n2)} subgroup di luar batas kendali. Seluruh periode: {(df.Status != 'Terkendali').sum()} dari {len(df)}.")
else: st.caption(f"Seluruh periode: {(df.Status != 'Terkendali').sum()} dari {len(df)} subgroup di luar batas kendali.")
box("**Process Capability:** " + ("Not Available. Cp/Cpk belum dapat dihitung (lihat tab Process Capability). Proses yang terkendali belum tentu capable." if CAPR is None else f"{capcat(CAPR['cpk'])} (Cpk = {fm(CAPR['cpk'], 3)}, Cp = {fm(CAPR['cp'], 3)})."), "#64748B" if CAPR is None else GREEN)

sec("G. Analysis Summary")
if not len(sm): st.info("Pilih periode yang memiliki data untuk melihat ringkasan.")
else:
    bad = sm[sm.Status != "Terkendali"]; T_, D_ = sm.n.sum(), sm.d.sum(); pp = D_ / T_ * 100
    L = [f"**Kondisi produksi {MON[mo]} {yr}:** produksi {fm(T_)} {uni}, cacat {fm(D_)} {uni} (**{fm(pp, 3)}%**), yaitu {fm(pp / (P['pbar'] * 100), 2)}× CL proses ({fm(P['pbar'] * 100, 3)}%)."]
    if has_cat and sm[CAT].sum().sum() > 0: tot = sm[CAT].sum().sort_values(ascending=False); L.append(f"**Kategori cacat:** terbesar **{tot.index[0]}** ({fm(tot.iloc[0] / tot.sum() * 100, 1)}% dari cacat periode ini), diikuti {tot.index[1]}.")
    L.append("**Stabilitas:** " + ("terkendali, semua titik periode ini berada dalam batas kendali." if bad.empty else f"**tidak terkendali** ({len(bad)} subgroup di luar batas: {', '.join(bad.Label)}); perlu ditindaklanjuti bersama QC."))
    if runs_ or trend_: L.append("**Pola proses:** " + "; ".join(runs_ + trend_) + ".")
    if len(phs) == 2: L.append(f"**Perbandingan fase:** cacat Fase I {fm(phs[1], 3)}% menjadi Fase II {fm(phs[2], 3)}% ({fm(phs[2] / phs[1], 2)}×).")
    if BART: dec = ("H0 tidak ditolak, asumsi independensi dapat diterima" + (" dengan catatan p mendekati batas." if BART["p"] < .1 else ".")) if BART["chi"] < BART["tab"] else "H0 ditolak: ada korelasi antar kategori cacat, tafsirkan batas kendali dengan hati-hati."; L.append(f"**Uji Bartlett:** χ² = {fm(BART['chi'], 3)} vs tabel {fm(BART['tab'], 3)} (p = {fm(BART['p'], 4)}); {dec}")
    L.append("**Kapabilitas:** " + ("Not Available (data ukur dan USL/LSL belum tersedia); stabilitas tidak otomatis berarti capable." if CAPR is None else f"Cp = {fm(CAPR['cp'], 3)}, Cpk = {fm(CAPR['cpk'], 3)} ({capcat(CAPR['cpk'])})."))
    L.append("**Tindak lanjut:** " + ("pertahankan kondisi proses dan lanjutkan monitoring." if bad.empty else "konfirmasi penyebab bersama QC berdasarkan kondisi lapangan, tetapkan tindakan korektif, lalu pantau apakah titik kembali ke dalam batas."))
    box("<br>".join("• " + l for l in L), "#0C4A6E")
