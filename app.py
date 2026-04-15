from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import requests
import math
from model import predict_disaster, suggest_camp

app = Flask(__name__)

# ---------------- DB ----------------
def get_db():
    return sqlite3.connect("database.db")

# ---------------- GEO ----------------
def get_coords(location):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json"}
        headers = {"User-Agent": "relief-system"}

        res = requests.get(url, params=params, headers=headers, timeout=5)

        if res.status_code != 200:
            return None, None

        data = res.json()
        if not data:
            return None, None

        return float(data[0]['lat']), float(data[0]['lon'])
    except:
        return None, None

# ---------------- HOME ----------------
@app.route('/')
@app.route('/dashboard')
def dashboard():

    db = get_db()

    reports = db.execute("SELECT latitude, longitude, risk FROM reports").fetchall()
    camps = db.execute("SELECT name, latitude, longitude FROM camps").fetchall()

    report_data = []
    camp_data = []

    for r in reports:
        if r[0]:
            report_data.append({"lat": r[0], "lon": r[1], "risk": r[2]})

    for c in camps:
        if c[1]:
            camp_data.append({"name": c[0], "lat": c[1], "lon": c[2]})

    return render_template("dashboard.html",
                           report_data=report_data,
                           camp_data=camp_data)

# ---------------- LIVE DATA ----------------
@app.route('/live_data')
def live_data():
    db = get_db()
    reports = db.execute("SELECT latitude, longitude, risk FROM reports").fetchall()

    data = []
    for r in reports:
        if r[0]:
            data.append({"lat": r[0], "lon": r[1], "risk": r[2]})

    return jsonify(data)

# ---------------- REPORT ----------------
@app.route('/report', methods=['GET','POST'])
def report():
    if request.method == 'POST':

        location = request.form['location']
        rainfall = float(request.form['rainfall'])
        water = float(request.form['water_level'])

        risk = predict_disaster(rainfall, water)
        lat, lon = get_coords(location)

        db = get_db()
        db.execute("""
        INSERT INTO reports (location,rainfall,water_level,risk,latitude,longitude)
        VALUES (?,?,?,?,?,?)
        """,(location, rainfall, water, risk, lat, lon))

        db.commit()

        return redirect('/dashboard')

    return render_template('report.html')

# ---------------- CAMPS ----------------
@app.route('/camps')
def camps():
    db = get_db()
    camps = db.execute("SELECT * FROM camps").fetchall()
    return render_template('camps.html', camps=camps)

# ---------------- ADD CAMP ----------------
@app.route('/add_camp', methods=['GET','POST'])
def add_camp():
    if request.method == 'POST':

        name = request.form['name']
        location = request.form['location']
        capacity = int(request.form['capacity'])
        food = int(request.form['food'])
        water = int(request.form['water'])

        lat, lon = get_coords(location)

        db = get_db()
        db.execute("""
        INSERT INTO camps (name,location,capacity,occupied,food,water,latitude,longitude)
        VALUES (?,?,?,?,?,?,?,?)
        """,(name, location, capacity, 0, food, water, lat, lon))

        db.commit()

        return redirect('/camps')

    return render_template('add_camp.html')

# ---------------- ADD VICTIM ----------------
@app.route('/add_victim', methods=['GET','POST'])
def add_victim():

    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])

        db = get_db()
        camps = db.execute("SELECT * FROM camps").fetchall()

        best = suggest_camp(camps)

        if best:
            db.execute("INSERT INTO victims (name,age,camp_id) VALUES (?,?,?)",
                       (name, age, best[0]))

            db.execute("UPDATE camps SET occupied = occupied + 1 WHERE id=?",
                       (best[0],))

            db.commit()

        return redirect('/camps')

    return render_template('add_victim.html')

# ---------------- ROUTING ----------------
@app.route('/nearest_camp', methods=['POST'])
def nearest_camp():

    user_lat = float(request.form['lat'])
    user_lon = float(request.form['lon'])

    db = get_db()
    camps = db.execute("SELECT name, latitude, longitude FROM camps").fetchall()

    nearest = None
    min_dist = float('inf')

    for c in camps:
        if c[1]:
            dist = math.sqrt((user_lat - c[1])**2 + (user_lon - c[2])**2)

            if dist < min_dist:
                min_dist = dist
                nearest = {"name": c[0], "lat": c[1], "lon": c[2]}

    return jsonify(nearest)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    return redirect('/dashboard')

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)