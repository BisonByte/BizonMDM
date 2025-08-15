import os
import sys
os.environ.setdefault('DATABASE_URL', 'sqlite:///bizon.db')
# Ensure we can import models.py from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import Admin, SessionLocal

def main():
    s = SessionLocal()
    try:
        admin = s.query(Admin).filter_by(username='admin').first()
        if admin:
            print('admin exists')
            return
        a = Admin(username='admin')
        a.set_password('admin')
        s.add(a)
        s.commit()
        print('admin created')
    finally:
        s.close()

if __name__ == '__main__':
    main()
