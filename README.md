# taglink-api

The Taglink API is built using FastAPI and enables mappings of links to tags for different user accounts.

## Setup

For a complete setup guide from setup of virtual machine on Windows10, see [Launching a CentOS7 Virtual Machine on Windows10](https://allthecoding.com/linux/launching-a-centos7-virtual-machine-on-windows10/)
For a guide on setting up the API only, see [Launching a CentOS7 Virtual Machine on Windows10: Part 4: API Server](https://allthecoding.com/linux/launching-a-centos7-virtual-machine-on-windows10-part-4-api-server/)

Install MariaDB:

```bash
$ sudo yum install mariadb-server
$ sudo systemctl start mariadb
$ sudo systemctl enable mariadb
$ sudo mysql_secure_installation
```

Then answer the prompts. It is recommended to answer ‘Y’ to all questions, apart from setting a root password, 
or which you will need to set a secure password.

Create the fastapi venv:

```bash
$ python venv -m .venv-fastapi
$ . .venv-fastapi/bin/activate
(.venv-fastapi) $ pip install --upgrade pip
(.venv-fastapi) $ pip install "fastapi[all]"
(.venv-fastapi) $ pip install sqlalchemy
(.venv-fastapi) $ pip install mariadb
(.venv-fastapi) $ pip install python-multipart
(.venv-fastapi) $ pip install "python-jose[cryptography]"
(.venv-fastapi) $ pip install "passlib[bcrypt]"
```

Create the integration-tests venv:
```bash
$ python venv -m .venv-integration-tests
$ . .venv-integration-tests/bin/activate
(.venv-integration-tests) $ pip install requests
(.venv-integration-tests) $ pip install pyyaml
(.venv-integration-tests) $ pip install pytest
```

Create a hashed password for the apiuser by running:
```bash
(.venv-fastapi) $ export PASSWORD='<YOUR_PASSWORD>' # Replace <YOUR_PASSWORD> with a suitable password
(.venv-fastapi) $ python hash_password.py
```
Make a note of the hashed password in the output.
Replace HASHED_PASSWORD in sql/schema_00.sql with the hashed password.

Create a hashed password for the integration_test_user by running:
```bash
(.venv-fastapi) $ export PASSWORD='<INTEGRATION_TEST_USER_PASSWORD>' # Replace <INTEGRATION_TEST_USER_PASSWORD> with a suitable password
(.venv-fastapi) $ python hash_password.py
```
Make a note of the hashed password in the output. 
Replace 'INTEGRATION_TEST_USER_PASSWORD' in integration_tests/test.yaml with the password. 
Replace 'INTEGRATION_TEST_USER_HASHED_PASSWORD' in sql/schema_00.sql with the hashed password. 

Create a database apiservice_user password. 
Replace 'PASSWORD' in config.yaml with this password.
Replace 'PASSWORD' in sql/schema_00.sql with this password.

Create a test account password. 
Replace 'INTEGRATION_TEST_ACCOUNT_PASSWORD' in integration_tests/test.yaml with the password.


Create a secret key by running:
```bash
$ openssl rand -hex 32
```
Replace 'SECRET_KEY' in config.yaml with this key.

Update integration_tests/test.yaml, replacing <YOUR_IP> with your host's IP (or localhost).

Run the SQL in sql/schema_00.sql in your database.

## Run the Fast API server

You will need to have configured nginx to redirect requests to port 8000 to /api. See: [Creating an API with python: Part 6: HTTPS and Proxying](https://allthecoding.com/python/creating-an-api-with-python-part-6-https-and-proxying/)


```bash
$ . .venv-fastapi/bin/activate
(.venv-fastapi) $ uvicorn --host 0.0.0.0 main:app --root-path /api --reload
```

View the swagger page at https://<YOUR_IP>/api/docs

## Integration Tests

Run the integration tests with:

```bash
./integration_test.sh
```


## Version history

| Version | Change(s)
|---------| ---------
| 0.0.3   | Added pool_pre_ping=True, pool_recyle=3600 params to create_engine, to prevent database connections dropping
| 0.0.2   | Add start.sh and systemd service configuration file
| 0.0.1   | Initial commit
     
