from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'rahasia'
app.config['DATABASE'] = 'instance/data.db'

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        # Tabel Materi Sejarah
        db.execute('''
            CREATE TABLE IF NOT EXISTS materi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                periode TEXT NOT NULL,
                isi TEXT NOT NULL
            )
        ''')
        # Tabel Kuis
        db.execute('''
            CREATE TABLE IF NOT EXISTS kuis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pertanyaan TEXT NOT NULL,
                jawaban TEXT NOT NULL,
                materi_id INTEGER,
                FOREIGN KEY (materi_id) REFERENCES materi(id)
            )
        ''')
        db.commit()

@app.route('/')
def beranda():
    return render_template('beranda.html')

@app.route('/materi')
def materi():
    db = get_db()
    materi_list = db.execute('SELECT * FROM materi').fetchall()
    return render_template('materi.html', materi=materi_list)

@app.route('/tambah-materi', methods=['GET', 'POST'])
def tambah_materi():
    if request.method == 'POST':
        judul = request.form['judul']
        periode = request.form['periode']
        isi = request.form['isi']
        
        db = get_db()
        db.execute('INSERT INTO materi (judul, periode, isi) VALUES (?, ?, ?)',
                  (judul, periode, isi))
        db.commit()
        flash('Materi berhasil ditambahkan!', 'success')
        return redirect(url_for('materi'))
    
    return render_template('tambah_materi.html')

@app.route('/kuis/<int:id>', methods=['GET', 'POST'])
def kuis(id):
    db = get_db()
    soal = db.execute('SELECT * FROM kuis WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        jawaban_user = request.form['jawaban'].lower()
        if jawaban_user == soal['jawaban'].lower():
            flash('Jawaban benar!', 'success')
        else:
            flash('Jawaban salah!', 'danger')
        return redirect(url_for('kuis', id=id))
    
    return render_template('kuis.html', soal=soal)

@app.route('/selesai/<int:materi_id>')
def selesai(materi_id):
    db = get_db()
    materi = db.execute('SELECT judul FROM materi WHERE id = ?', (materi_id,)).fetchone()
    return render_template('selesai.html', judul=materi['judul'])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)