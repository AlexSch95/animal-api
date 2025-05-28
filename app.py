# importiere Flask von dem Modul flask
from flask import Flask, jsonify, request
# importiere Swagger vom flasgger Modul
from flasgger import Swagger
# importiere das sqlite3 Modul, das ist integriert in Python
import sqlite3

# initialisiere ein app-Objekt von der Klasse Flask
app = Flask(__name__)
# initialisiere ein swagger-Objekt von der Klasse Swagger, übergebe dabei das app-Objekt
swagger = Swagger(app)

# Lege Konstante an, der den Pfad zu Datenbank-Datei beschreibt
#DATABASE_URL = "http://127.0.0.1:5432" # später wird für unsere Postgres
DATABASE = "./animals.db" # hier liegt dann unsere DB-Datei 

# Datenbank-Hilfsfunktionen
## Funktion, um sich mit der Datenbank zu verbinden
def get_db_connection():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row # super praktische Einstellung, damit wir Ergebnisse von SQL-Befehlen im richtigen Datenformat (Dictionary bzw. JSON-Format) zurückbekommen
    return con

## Funktion, um die Datenbank zu initialisieren
# Seeding-Skript für die Datenbank
def init_db():
    # Initialisieren der DB
    con = get_db_connection() # rufe Hilfsfunktion auf
    cur = con.cursor()
    cur.execute('''
                CREATE TABLE IF NOT EXISTS Animals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    genus TEXT    
                )
                ''')
    # Überprüfe, ob Zeilen, also Datensätze in der Animals-Tabelle drin sind
    # cur.execute('SELECT COUNT(*) FROM Animals')
    # count = cur.fetchone()[0]
    count = cur.execute('SELECT COUNT(*) FROM Animals').fetchone()[0]
    if count == 0:
        data = [
            ('dog', 3, 'mammals'),
            ('cat', 2, 'mammals'),
            ('elephant', 20, 'mammals'),
            ('bird', 5, 'birds')
        ]
        cur.executemany('INSERT INTO Animals (name, age, genus) VALUES (?,?,?)', data) # das geht er jeweils für jeden Eintrag der data durch
        con.commit()
    con.close()

## Test-Route für Startseite
@app.route("/")
def home():
    return "Hallo, das eine Tier-Api"

## GET-Route implementieren, d.h. Daten abrufen bzw. alle Tiere anzeigen
@app.route("/api/animals", methods=['GET'])
def show_animals():
    """
    Liste aller Tiere
    ---
    responses:
        200:
            description: JSON-Liste aller Tiere
            examples:
                application/json:
                    - id: 1
                      name: Dog
                      age: 3
                      genus: mammals
                    - id: 2
                      name: Cat
                      age: 2
                      genus: mammals
    """
    # # Daten abrufen von der DB
    # return jsonify(animals), 200
    con = get_db_connection() # Verbindung mit der DB
    cur = con.cursor()
    animals = cur.execute('SELECT * FROM Animals').fetchall()
    con.close()
    return jsonify([dict(animal) for animal in animals]), 200

## POST-Route implementieren, d.h. neue Tier hinzufügen
@app.route("/api/animals", methods=['POST'])
def add_animal():
    """
    Neues Tier hinzufügen
    ---
    consumes:
        - application/json
    parameters:
        - in: body
          name: tier
          required: true
          schema:
            type: object
            properties:
                name:
                    type: string
                    example: Elephant
                age:
                    type: integer
                    example: 10
                genus:
                    type: string
                    example: mammals
    responses:
        201:
            description: Tier wurde erfolgreich hinzugefügt
        400:
            description: Keine oder fehlerhafte Daten übertragen
    """
    new_animal = request.get_json() # {"name": "turtle", "age:": 100, "genus": "reptile"}
    if not new_animal or 'name' not in new_animal:
        return jsonify({"message": "Keine oder fehlerhafte Daten übertragen"}), 400
    con = get_db_connection()
    cur = con.cursor()
    cur.execute('INSERT INTO Animals (name, age, genus) VALUES (?,?,?)', 
                (new_animal['name'],
                 new_animal['age'],
                 new_animal['genus'])
                ) # An dieser Stelle SQL-Befehl zum Hinzufügen des neuen Objektes
    con.commit()
    con.close()
    return jsonify({"message": "Tier wurde erfolgreich hinzugefügt"}), 201

## DELETE-Route, um ein Tier aus der Liste zu löschen
@app.route("/api/animals/<int:animal_id>", methods=['DELETE'])
def delete_animal(animal_id):
    """
    Ein Tier löschen
    ---
    parameters:
        - name: animal_id
          in: path
          type: integer
          required: true
          description: Der Name des zu löschenden Tieres
    responses:
        200:
            description: Tier wurde erfolgreich gelöscht
            examples:
                application/json:
                    - message: Tier wurde erfolgreich gelöscht
        404:
            description: Tier mit dieser ID existiert nicht
            examples:
                application/json:
                    - message: Tier mit dieser ID existiert nicht
    """
    con = get_db_connection()
    cur = con.cursor()
    animal = cur.execute('SELECT * FROM Animals WHERE id = ?', (animal_id,)).fetchone()
    if animal is None:
        return jsonify({"message": "Tier mit dieser ID existiert nicht"}), 404
    cur.execute('DELETE FROM Animals WHERE id = ?', (animal_id,))
    con.commit()
    con.close()
    return jsonify({"message": "Tier wurde erfolgreich gelöscht"}), 200

## Baue eine Funktion, zum Updaten
## PUT-Route -> Ersetze alle Eigenschaften eines Tieres, d.h. hier schicken wir alle Eigenschaften im Body als JSON mit
@app.route("/api/animals/<int:animal_id>", methods=['PUT'])
def put_animal(animal_id):
    """
    Ganzes Tier ersetzen
    ---
    parameters:
        - name: animal_id
          in: path
          type: integer
          required: true
          description: Der Name des Tiers, das ersetzt werden soll
        - in: body
          name: tier
          required: true
          schema: 
            type: object
            properties:
                name:
                    type: string
                    example: elephant
                age:
                    type: integer
                    example: 20
                genus:
                    type: string
                    example: mammals
    responses:
        200:
            description: Tier wurde ersetzt
            examples:
                application/json:
                    - message: Tier wurde ersetzt
        404:
            description: Tier ist nicht in der Datenbank vorhanden
            examples:
                application/json:
                    - message: Tier mit dieser ID existiert nicht
    """
    updated_animal = request.get_json() # in data wird das Ganze JSON-Objekt gespeichert, das vom Client im Body übergeben wird
    # Suche nach dem Objekt, das wir updaten wollen
    if updated_animal == None or 'name' not in updated_animal:
        return jsonify({"message": "Es wurde kein Objekt übergeben"})
    con = get_db_connection()
    cur = con.cursor()
    animal = cur.execute('SELECT * FROM Animals WHERE id = ?', (animal_id,)).fetchone()
    if animal is None:
        return jsonify({"message": "Tier mit dieser ID existiert nicht"}), 404
    cur.execute('''UPDATE Animals SET
            name = ?,
            age = ?,
            genus = ?
            WHERE id = ?''', (updated_animal['name'], updated_animal['age'], updated_animal['genus'], animal_id))
    con.commit()
    con.close()
    return jsonify({"message": "Tier wurde ersetzt"}), 200


## PATCH-Route -> Ersetze spezifisch einzelne Eigenschaften, d.h. hier schicken wir nur die zu ändernden Eigenschaften im Body als JSON mit
@app.route("/api/animals/<int:animal_id>", methods=["PATCH"])
def patch_animal(animal_id):
    """
    Tier teilweise ändern (z.B. nur das Alter)
    ---
    parameters:
        - name: animal_id
          in: path
          type: integer
          required: true
          description: Der Name des Tiers, das ersetzt werden soll
        - in: body
          name: tier
          required: anyOf
          schema: 
            type: object
            properties:
                name:
                    type: string
                    example: elephant
                age:
                    type: integer
                    example: 20
                genus:
                    type: string
                    example: mammals
    responses:
        200:
            description: Tier wurde geupdated
            examples:
                application/json:
                    - message: Tier wurde geupdated
        404:
            description: Tier wurde nicht gefunden
            examples:
                application/json:
                    - message: Tier wurde nicht gefunden
    """
    update_data = request.get_json()
    con = get_db_connection()
    cur = con.cursor()
    animal = cur.execute('SELECT * FROM Animals WHERE id = ?', (animal_id,)).fetchone()
    if animal is None:
        return jsonify({"message": "Tier mit dieser ID ist nicht in der DB"}), 404
    for key, value in update_data.items():
        if key in ['name', 'age', 'genus']: #SELECT name FROM pragma_table_info('Ihre_Tabelle') ??? um spaltenüberschriften aus der db zu laden damit validierung nicht hardcoded ist
            cur.execute(f'UPDATE Animals SET {key} = ? WHERE id = ?', (value, animal_id))
    con.commit()
    con.close()
    return jsonify({"message": "Tier wurde geupdated"}), 200

# App starten
if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5050, debug=True)
