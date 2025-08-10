import os
import argparse
from typing import Optional
from flask import Flask, request, redirect, send_from_directory

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
        from Servidor.models import init_db, SessionLocal, Admin
        init_db(drop=True)
        with SessionLocal() as session:
            if not session.query(Admin).filter_by(username=user).first():
                admin = Admin(username=user)
                admin.set_password(pwd)
                session.add(admin)
                session.commit()
        return redirect('/admin/#/first-steps')
    root_dir = os.path.dirname(__file__)
    return send_from_directory(root_dir, 'instalacion_bizonmdm.html')


def install_application(
    db_host: str, db_name: str, db_user: str, db_pass: str, jwt_secret: str
) -> None:
    """Configura el entorno de la aplicación y ejecuta las migraciones."""
    db_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}/{db_name}"
    env_content = f"DATABASE_URL={db_url}\nJWT_SECRET={jwt_secret}\n"
    _write_env_file(env_content)
    os.environ['DATABASE_URL'] = db_url
    os.environ['JWT_SECRET'] = jwt_secret
    from Servidor.models import init_db
    init_db(drop=True)


def _write_env_file(content: str) -> None:
    """Write the given content to the Servidor/.env file."""
    base_dir = os.path.join(os.path.dirname(__file__), 'Servidor')
    env_path = os.path.join(base_dir, '.env')
    with open(env_path, 'w', encoding='utf-8') as fh:
        fh.write(content)


def _install_from_args(db: str, jwt: str, user: Optional[str], pwd: Optional[str]) -> None:
    env_content = f"DATABASE_URL={db}\nJWT_SECRET={jwt}\n"
    _write_env_file(env_content)
    os.environ['DATABASE_URL'] = db
    os.environ['JWT_SECRET'] = jwt
    from Servidor.models import init_db, SessionLocal, Admin
    init_db(drop=True)
    if user and pwd:
        with SessionLocal() as session:
            if not session.query(Admin).filter_by(username=user).first():
                admin = Admin(username=user)
                admin.set_password(pwd)
                session.add(admin)
                session.commit()


def _copy_example() -> None:
    """Create the .env file using server/.env.example."""
    example_path = os.path.join(os.path.dirname(__file__), '.env.example')
    with open(example_path, 'r', encoding='utf-8') as fh:
        content = fh.read()
    _write_env_file(content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Instala la aplicación BizonMDM')
    parser.add_argument('--db', help='URL de la base de datos')
    parser.add_argument('--jwt', help='Clave JWT secreta')
    parser.add_argument('--user', help='Usuario administrador inicial')
    parser.add_argument('--pwd', help='Contraseña del administrador')
    parser.add_argument(
        '--use-example',
        action='store_true',
        help='Genera el archivo .env a partir de server/.env.example',
    )
    args = parser.parse_args()

    if args.use_example:
        _copy_example()
        print('.env creado a partir de .env.example')
    elif args.db and args.jwt:
        _install_from_args(args.db, args.jwt, args.user, args.pwd)
        print('Instalación completada mediante línea de comandos.')
    else:
        app.run()
