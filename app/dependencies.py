from hotel_business_module.session.session import get_session


def get_db():
    """
    Зависимость для получения сессии sqlalchemy
    :return:
    """
    db = get_session()
    try:
        yield db
    finally:
        db.close()
        