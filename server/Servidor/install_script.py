import os
from models import init_db


def install_application(db_host: str, db_name: str, db_user: str, db_pass: str, jwt_secret: str) -> None:
    """Configura el entorno de la aplicación y ejecuta las migraciones."""
    db_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}/{db_name}"
    base_dir = os.path.dirname(__file__)
    env_path = os.path.join(base_dir, '.env')
    with open(env_path, 'w', encoding='utf-8') as fh:
        fh.write(f"DATABASE_URL={db_url}\nJWT_SECRET={jwt_secret}\n")

    os.environ['DATABASE_URL'] = db_url
    os.environ['JWT_SECRET'] = jwt_secret
    init_db(drop=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Instala la aplicación BizonMDM')
    parser.add_argument('--db-host', required=True)
    parser.add_argument('--db-name', required=True)
    parser.add_argument('--db-user', required=True)
    parser.add_argument('--db-pass', required=True)
    parser.add_argument('--jwt-secret', required=True)
    args = parser.parse_args()
    install_application(args.db_host, args.db_name, args.db_user, args.db_pass, args.jwt_secret)
    print('Instalación completada.')
