# importiere Flask von dem Modul flask
from flask import Flask, jsonify, request
# importiere Swagger vom flasgger Modul
from flasgger import Swagger

# initialisiere ein app-Objekt von der Klasse Flask
app = Flask(__name__)
# initialisiere ein swagger-Objekt von der Klasse Swagger, übergebe dabei das app-Objekt
swagger = Swagger(app)

## Tiere in einer Liste speichern -> Local Storage
animals = [
    { "id": 1, "name": "dog", "age": 3, "genus": "mammals"},
    { "id": 2, "name": "cat", "age": 2, "genus": "mammals"}
]

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
    return jsonify(animals), 200

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
                id:
                    type: integer
                    example: 3
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
            description: Name wurde erfolgreich hinzugefügt
        400:
            description: Fehler, kein Objekt übergeben
    """
    ## Funktion um die Daten im JSON-Format aus dem Request-Objekt zu bekommen
    new_animal = request.get_json() # Hole dir aus dem Request-Objekt die Daten im JSON-Format
    # { "id": 3, "name": .., "age": ..., "genus": ...}
    if not new_animal:
        return f"Fehler, kein Objekt übergeben", 400
    animals.append(new_animal) # hänge das Objekt im JSON-Format hinten dran
    return f"{new_animal} wurde erfolgreich hinzugefügt", 201

## DELETE-Route, um ein Tier aus der Liste zu löschen
@app.route("/api/animals/<name>", methods=['DELETE'])
def delete_animal(name):
    """
    Ein Tier löschen
    ---
    parameters:
        - name: name
          in: path
          type: string
          required: true
          description: Der Name des zu löschenden Tieres
    responses:
        200:
            description: Tier wurde gelöscht
        404:
            description: Tier wurde nicht gefunden
    """
    for animal in animals:
        if animal["name"] == name:
            animals.remove(animal)
            return f"{name} wurde gelöscht", 200
    return f"{name} wurde nicht gefunden", 404

## Baue eine Funktion, zum Updaten
## PUT-Route -> Ersetze alle Eigenschaften eines Tieres, d.h. hier schicken wir alle Eigenschaften im Body als JSON mit
@app.route("/api/animals/<name>", methods=['PUT'])
def put_animal(name):
    """
    Ein vorhandenes Tier KOMPLETT überschreiben
    ---
    parameters:
        - name: name
          in: path
          type: string
          required: true
          description: Der Name des Tieres das mit den neuen Daten komplett überschrieben werden soll
        - in: body
          name: tier
          required: true
          schema:
            type: object
            properties:
                id:
                    type: integer
                    example: 3
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
        200:
            description: Tier wurde geupdated
        404:
            description: Tier wurde nicht gefunden
    """
    data = request.get_json() # in data wird das Ganze JSON-Objekt gespeichert, das vom Client im Body übergeben wird
    # Suche nach dem Objekt, das wir updaten wollen
    for animal in animals:
        if animal["name"] == name:
            animal.clear() # Lösche alle Werte des gefundenen Tieres
            animal.update(data) # Setze die Werte auf die Werte, die wir im JSON-Format in der Variablen data speichern
            return f"{name} wurde geupdated", 200
    return f"{name} wurde nicht gefunden", 404


## PATCH-Route -> Ersetze spezifisch einzelne Eigenschaften, d.h. hier schicken wir nur die zu ändernden Eigenschaften im Body als JSON mit
@app.route("/api/animals/<name>", methods=["PATCH"])
def patch_animal(name):
    """
       Einen Wert eines vorhandenen Tiers überschreiben
       ---
       parameters:
           - name: name
             in: path
             type: string
             required: true
             description: Der Name des Tieres das bei dem ein Wert überschrieben werden soll
           - in: body
             name: tier
             required: anyOf
             schema:
               type: object
               properties:
                   id:
                       type: integer
                       example: 3
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
           200:
               description: Tier wurde geupdated
           404:
               description: Tier wurde nicht gefunden
       """
    data = request.get_json()
    for animal in animals:
        if animal["name"] == name:
            animal.update(data)
            return f"{name} wurde geupdatet", 200
    return f"{name} wurde nicht gefunden", 404

# App starten
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
