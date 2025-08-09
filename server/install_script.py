import os
import bcrypt
from flask import Flask, request, redirect, send_from_directory
from Servidor.models import init_db, SessionLocal, Admin

app = Flask(__name__)


@app.route('/install', methods=['GET', 'POST'])
def install():
    if request.method == 'POST':
        db = request.form['db']
        jwt = request.form['jwt']
        user = request.form['user']
        pwd = request.form['pwd']

        base_dir = os.path.join(os.path.dirname(__file__), 'Servidor')
        env_path = os.path.join(base_dir, '.env')
        with open(env_path, 'w', encoding='utf-8') as fh:
            fh.write(f"DATABASE_URL={db}\nJWT_SECRET={jwt}\n")

        os.environ['DATABASE_URL'] = db
        os.environ['JWT_SECRET'] = jwt
        init_db()
        with SessionLocal() as session:
            if not session.query(Admin).filter_by(username=user).first():
                admin = Admin(username=user)
                admin.set_password(pwd)
                session.add(admin)
                session.commit()
        return redirect('/admin/#/first-steps')
    root_dir = os.path.dirname(__file__)
    return send_from_directory(root_dir, 'instalacion_bizonmdm.html')


if __name__ == '__main__':
    app.run()
