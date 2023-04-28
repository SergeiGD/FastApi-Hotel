from hotel_business_module.gateways.workers_gateway import WorkersGateway
import sys
from hotel_business_module.session.session import get_session


if __name__ == '__main__':
    with get_session() as session:
        email = sys.argv[1]
        password = sys.argv[2]
        print(email, password)

        if not email or not password:
            print('Введите почту и пароль')
        else:
            try:
                WorkersGateway.create_superuser(email, password, session)
            except ValueError as err:
                print(str(err))
