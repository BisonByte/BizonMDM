import os
import argparse
from typing import Optional


def _write_env_file(content: str) -> None:
    """Write the given content to the Servidor/.env file."""
    base_dir = os.path.join(os.path.dirname(__file__), 'Servidor')
    env_path = os.path.join(base_dir, '.env')
    with open(env_path, 'w', encoding='utf-8') as fh:
        fh.write(content)


def _install_from_args(
    db: str,
    jwt: str,
    user: Optional[str],
    pwd: Optional[str],
    fcm: Optional[str],
) -> None:
    env_content = f"DATABASE_URL={db}\nJWT_SECRET={jwt}\n"
    _write_env_file(env_content)
    os.environ['DATABASE_URL'] = db
    os.environ['JWT_SECRET'] = jwt
    if fcm:
        key_path = os.path.join(os.path.dirname(__file__), 'Servidor', 'fcm_key.txt')
        with open(key_path, 'w', encoding='utf-8') as fh:
            fh.write(fcm)
        os.environ['FCM_SERVER_KEY'] = fcm
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
    parser.add_argument('--fcm', help='Clave de servidor FCM (opcional)')
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
        _install_from_args(args.db, args.jwt, args.user, args.pwd, args.fcm)
        print('Instalación completada mediante línea de comandos.')
    else:
        parser.print_help()
