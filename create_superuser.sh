#!/bin/sh
docker exec -it fastapi_app sh -c "python create_superuser.py '$1' '$2'"