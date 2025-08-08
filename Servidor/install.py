import os
from flask import Flask, request, redirect, render_template_string
from models import init_db

app = Flask(__name__)

FORM = """
<!doctype html>
<title>Instalación BizonMDM</title>
<h1>Configuración inicial</h1>
<form method="post">
  <label>URL Base de Datos<input name="db" required></label><br>
  <label>Clave JWT<input name="jwt" required></label><br>
  <label>Clave Firebase<input name="fcm" required></label><br>
  <label>Usuario admin<input name="user" required></label><br>
  <label>Contraseña<input type="password" name="pwd" required></label><br>
  <button type="submit">Instalar</button>
</form>
"""

@app.route('/', methods=['GET', 'POST'])
def install():
    if request.method == 'POST':
        db = request.form['db']
        jwt = request.form['jwt']
        fcm = request.form['fcm']
        user = request.form['user']
        pwd = request.form['pwd']
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_path, 'w', encoding='utf-8') as fh:
            fh.write(f"DATABASE_URL={db}\nJWT_SECRET={jwt}\nADMIN_USER={user}\nADMIN_PASSWORD={pwd}\n")
        key_path = os.path.join(os.path.dirname(__file__), 'fcm_key.txt')
        with open(key_path, 'w', encoding='utf-8') as fh:
            fh.write(fcm)
        os.environ['DATABASE_URL'] = db
        os.environ['JWT_SECRET'] = jwt
        init_db()
        return redirect('/admin')
    return render_template_string(FORM)

if __name__ == '__main__':
    app.run()
