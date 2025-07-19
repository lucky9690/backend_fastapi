from database import engine ,Base
from models import user,Blog


def init_db():
    print("Dropping all tables....")
    Base.metadata.drop_all(bind=engine)
    print("Database initialized successfully")


if __name__=="__main__":
 init_db()