/* Webinar 5: user-centered design + visualisasi data tanpa pustaka tambahan. */
'use strict';

const rupiah = angka => 'Rp' + Math.round(angka).toLocaleString('id-ID');
const bilangan = angka => angka.toLocaleString('id-ID');
const persen = angka => angka.toLocaleString('id-ID', {maximumFractionDigits: 2}) + '%';
const dom = id => document.getElementById(id);
let seluruhData = [];
let dataAktif = [];

function parseCSV(teks) {
  const baris = teks.trim().split(/\r?\n/);
  const header = baris.shift().split(',').map(s => s.trim());
  const wajib = ['tanggal', 'wilayah', 'kategori', 'transaksi', 'omzet', 'keluhan'];
  if (wajib.some(k => !header.includes(k))) throw new Error('Format kolom data tidak sesuai.');
  return baris.filter(Boolean).map(b => {
    const isi = b.split(',');
    const data = Object.fromEntries(header.map((kolom, i) => [kolom, (isi[i] || '').trim()]));
    ['transaksi', 'omzet', 'keluhan'].forEach(k => data[k] = Number(data[k]));
    if (['transaksi', 'omzet', 'keluhan'].some(k => !Number.isFinite(data[k]) || data[k] < 0)) throw new Error('Terdapat angka tidak valid pada CSV.');
    return data;
  });
}

function isiPilihan(id, nilai, label) {
  const select = dom(id);
  [...new Set(nilai)].sort().forEach(v => {
    const opt = document.createElement('option');
    opt.value = v;
    opt.textContent = label ? label(v) : v;
    select.append(opt);
  });
}

function jumlahkan(data) {
  return data.reduce((jumlah, baris) => {
    jumlah.transaksi += baris.transaksi;
    jumlah.omzet += baris.omzet;
    jumlah.keluhan += baris.keluhan;
    return jumlah;
  }, {transaksi: 0, omzet: 0, keluhan: 0});
}

function kelompokkan(data, properti) {
  const grup = new Map();
  for (const item of data) {
    const kunci = item[properti];
    if (!grup.has(kunci)) grup.set(kunci, []);
    grup.get(kunci).push(item);
  }
  return [...grup.entries()].map(([nama, daftar]) => ({nama, ...jumlahkan(daftar)}));
}

function svgElemen(nama, atribut = {}, teks = '') {
  const el = document.createElementNS('http://www.w3.org/2000/svg', nama);
  for (const [k, v] of Object.entries(atribut)) el.setAttribute(k, v);
  if (teks) el.textContent = teks;
  return el;
}

function buatGrafikTren(data) {
  const svg = dom('grafikTren');
  svg.replaceChildren();
  const titik = kelompokkan(data, 'tanggal').sort((a, b) => a.nama.localeCompare(b.nama));
  svg.setAttribute('aria-label', `Tren omzet ${titik.length} hari. Baca angka tepat di tabel harian.`);
  if (!titik.length) {
    svg.append(svgElemen('text', {x: 30, y: 120, fill: '#53647b'}, 'Tidak ada data pada pilihan ini.'));
    return;
  }
  const kiri = 75, atas = 25, kanan = 712, bawah = 211;
  const maksimum = Math.max(...titik.map(t => t.omzet), 1) * 1.12;
  for (let i = 0; i <= 4; i++) {
    const y = bawah - i * (bawah - atas) / 4;
    svg.append(svgElemen('line', {x1: kiri, x2: kanan, y1: y, y2: y, class: 'gridline'}));
    const nilai = Math.round((maksimum * i / 4) / 1000);
    svg.append(svgElemen('text', {x: kiri - 9, y: y + 4, 'text-anchor': 'end', class: 'axis'}, `${bilangan(nilai)} rb`));
  }
  const posisi = titik.map((t, i) => ({
    x: kiri + (titik.length === 1 ? (kanan - kiri) / 2 : (i * (kanan - kiri)) / (titik.length - 1)),
    y: bawah - (t.omzet / maksimum) * (bawah - atas), data: t
  }));
  const linePath = posisi.map((p, i) => `${i ? 'L' : 'M'}${p.x.toFixed(2)},${p.y.toFixed(2)}`).join(' ');
  const areaPath = `${linePath} L${posisi[posisi.length - 1].x},${bawah} L${posisi[0].x},${bawah} Z`;
  svg.append(svgElemen('path', {d: areaPath, class: 'area'}));
  svg.append(svgElemen('path', {d: linePath, class: 'line'}));
  if (posisi.length <= 14) for (const p of posisi) {
    svg.append(svgElemen('circle', {cx: p.x, cy: p.y, r: 4, fill: '#125cae'}));
  }
  const indeks = [...new Set([0, Math.floor((titik.length - 1) / 2), titik.length - 1])];
  for (const i of indeks) {
    const t = posisi[i];
    svg.append(svgElemen('text', {x: t.x, y: 235, 'text-anchor': 'middle', class: 'axis'}, `${t.data.nama.slice(8, 10)}/${t.data.nama.slice(5, 7)}`));
  }
}

function buatGrafikKategori(data) {
  const tempat = dom('grafikKategori');
  tempat.replaceChildren();
  const kategori = kelompokkan(data, 'kategori').sort((a, b) => b.omzet - a.omzet);
  if (!kategori.length) {
    tempat.textContent = 'Tidak ada data pada pilihan ini.';
    return;
  }
  const maksimal = Math.max(...kategori.map(k => k.omzet), 1);
  for (const item of kategori) {
    const bungkus = document.createElement('div');
    bungkus.className = 'bar-item';
    bungkus.setAttribute('tabindex', '0');
    bungkus.setAttribute('aria-label', `${item.nama}, omzet ${rupiah(item.omzet)}`);
    const info = document.createElement('div');
    info.className = 'bar-top';
    const nama = document.createElement('span');
    nama.textContent = item.nama;
    const angka = document.createElement('strong');
    angka.textContent = rupiah(item.omzet);
    info.append(nama, angka);
    const track = document.createElement('div');
    track.className = 'track';
    const fill = document.createElement('div');
    fill.className = 'fill';
    fill.style.width = `${(100 * item.omzet / maksimal).toFixed(2)}%`;
    track.append(fill);
    bungkus.append(info, track);
    tempat.append(bungkus);
  }
}

function buatTabel(data) {
  const tbody = dom('tabel-harian');
  tbody.replaceChildren();
  const harian = kelompokkan(data, 'tanggal').sort((a, b) => a.nama.localeCompare(b.nama));
  if (!harian.length) {
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 4;
    td.textContent = 'Tidak ada data yang cocok.';
    tr.append(td);
    tbody.append(tr);
    return;
  }
  for (const item of harian) {
    const tr = document.createElement('tr');
    const sel = [item.nama, bilangan(item.transaksi), rupiah(item.omzet), bilangan(item.keluhan)];
    sel.forEach((value, index) => {
      const td = document.createElement('td');
      td.textContent = value;
      if (index) td.className = 'number';
      tr.append(td);
    });
    tbody.append(tr);
  }
}

function perbarui() {
  const bulan = dom('bulan').value;
  const wilayah = dom('wilayah').value;
  const kategori = dom('kategori').value;
  dataAktif = seluruhData.filter(d =>
    (bulan === 'Semua' || d.tanggal.startsWith(bulan)) &&
    (wilayah === 'Semua' || d.wilayah === wilayah) &&
    (kategori === 'Semua' || d.kategori === kategori)
  );
  const hasil = jumlahkan(dataAktif);
  dom('omzet').textContent = rupiah(hasil.omzet);
  dom('transaksi').textContent = bilangan(hasil.transaksi);
  dom('keluhan').textContent = bilangan(hasil.keluhan);
  dom('rasio').textContent = persen(hasil.transaksi ? 100 * hasil.keluhan / hasil.transaksi : 0);
  dom('status').textContent = `Menampilkan ${bilangan(dataAktif.length)} baris data • Filter: ${bulan === 'Semua' ? 'semua periode' : bulan}, ${wilayah === 'Semua' ? 'semua wilayah' : wilayah}, ${kategori === 'Semua' ? 'semua kategori' : kategori}.`;
  buatGrafikTren(dataAktif);
  buatGrafikKategori(dataAktif);
  buatTabel(dataAktif);
}

function unduhCSV() {
  const kolom = ['tanggal', 'wilayah', 'kategori', 'transaksi', 'omzet', 'keluhan'];
  const baris = [kolom.join(','), ...dataAktif.map(d => kolom.map(k => d[k]).join(','))];
  const blob = new Blob(['\ufeff', baris.join('\r\n')], {type: 'text/csv;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'penjualan_hasil_filter.csv';
  document.body.append(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  dom('status').textContent = `${bilangan(dataAktif.length)} baris data telah disiapkan untuk diunduh sebagai CSV.`;
}

async function mulai() {
  try {
    const respon = await fetch('/data/penjualan.csv', {cache: 'no-store'});
    if (!respon.ok) throw new Error(`HTTP ${respon.status}`);
    seluruhData = parseCSV(await respon.text());
    isiPilihan('bulan', seluruhData.map(d => d.tanggal.slice(0, 7)), v => {
      const [th, bl] = v.split('-');
      const nama = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];
      return `${nama[Number(bl) - 1]} ${th}`;
    });
    isiPilihan('wilayah', seluruhData.map(d => d.wilayah));
    isiPilihan('kategori', seluruhData.map(d => d.kategori));
    ['bulan', 'wilayah', 'kategori'].forEach(id => dom(id).addEventListener('change', perbarui));
    dom('reset').addEventListener('click', () => {
      ['bulan', 'wilayah', 'kategori'].forEach(id => dom(id).value = 'Semua');
      perbarui();
      dom('bulan').focus();
    });
    dom('unduh').addEventListener('click', unduhCSV);
    perbarui();
  } catch (err) {
    dom('status').textContent = `Gagal membuka data (${err.message}). Jalankan "python server.py", lalu buka http://localhost:8000/ — jangan membuka HTML dengan klik ganda.`;
    dom('status').style.color = '#a52323';
  }
}

mulai();
