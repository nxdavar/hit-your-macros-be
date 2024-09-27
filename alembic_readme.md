### Alembic Commmands:

#### Performing a Migration:

1. Ensuring the target table is sync:
   `alembic upgrade head`

2. If you made a change to the schema file and want alembic to autogenerate a mirgation file, use the following command:
   `alembic revision --autogenerate -m "your update message"`
   w
