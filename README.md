# Update Packages

    sudo apt-get update
    sudo apt-get upgrade
    
# Install and Configure Nginx

    sudo apt-get install nginx
    
Configure Nginx

# Install and Configure Postgresql

Install dependencies for PostgreSQL to work with web.py with this command:

    sudo apt-get install libpq-dev python-dev

Next install PostgreSQL:

    sudo apt-get install postgresql postgresql-contrib

Configure postgresql

    sudo su - postgres
    createdb [DBNAME]
    createuser -P

enter psql
    
    psql
 
Grant user privileges

    GRANT ALL PRIVILEGES ON DATABASE [DBNAME] TO [USERNAME];
    
Exit psql with `\q`

# Install and Configure Virtualenv
    
    pip install virtualenv

Create a virtualenv named `sjtfl`

    sudo virtualenv [VIRTUALENV DIR]/sjtfl

# Install and Configure Supervisord

    pip install supervisor
    
Create the supervisord config file named `sjtfl.conf` and reference it from the supervisord.conf file. Replace variables inside [] with your actual values.

    [program:sjtfl]
    command = [VIRTUALENV DIR]/sjtfl/bin/python [VIRTUALENV DIR]/sjtfl/bin/gunicorn --workers 4 --bind unix:[VIRTUALENV DIR]/sjtfl.sock code:wsgiapp
    directory = [VIRTUALENV DIR]/sjtfl/sjtfl
    user = [USER]
    stdout_logfile = [VIRTUALENV DIR]/sjtfl/logs/gunicorn/gunicorn_stdout.log
    stderr_logfile = [VIRTUALENV DIR]/sjtfl/logs/gunicorn/gunicorn_stderr.log
    redirect_stderr = True
    environment = PRODUCTION=1

# Install Environment Dependencies

First activate the venv

    source [VIRTUALENV DIR]/bin/activate

And install dependencies

    pip install -r requirements.txt

This will install `web.py`, `psycopg2`, `gunicorn`, `bcrypt`, `requests`, and `python-dotenv`.

Clone this repo inside the venv.

Creat a .env file in this cloned repo. Fill in values.

    DATABASE_USER='[USERNAME]'
    DATABASE_PASSWORD='[DBPASSWORD]'
    DATABASE_NAME='[DBNAME]'
    DATA_PATH='[DATAPATH]'
    INSTAGRAM_ACCESS_TOKEN='[ACCESSTOKEN]'

Run site using 

    supervisorctl start sjtfl
