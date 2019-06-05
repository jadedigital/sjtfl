How to get a fresh site up and running. Replace variables inside [] with your actual values.

# Update Packages

    sudo apt-get update
    sudo apt-get upgrade
    
# Install and Configure Nginx

    sudo apt-get install nginx
    
Configure Nginx

    sudo service nginx start

Create new Nginx config file:
    
    sudo nano /etc/nginx/sites-available/sjtfl

Paste the following in the new config file:
    server {
        listen 80;
        server_name [URL].com www.[URL].com;
        return 301 https://$server_name$request_uri;
    }

    server {

        # SSL configuration

        listen 443 ssl http2 default_server;
        include snippets/ssl-[URL].com.conf;
        include snippets/ssl-params.conf;

        location /static/ {
            root [VIRTUALENV DIR]/sjtfl/sjtfl;
            if (-f $request_filename) {
                rewrite ^/static/(.*)$ /static/$1 break;
            }
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:[VIRTUALENV DIR]/sjtfl.sock;
        }

        location /.well-known {
            alias [VIRTUALENV DIR]/sjtfl/sjtfl/.well-known;
        }

    }

# Install and Configure PostgreSQL

Install dependencies for PostgreSQL to work with web.py with this command:

    sudo apt-get install libpq-dev python-dev

Next install PostgreSQL:

    sudo apt-get install postgresql postgresql-contrib

Configure postgreSQL

    sudo su - postgres
    createdb [DBNAME]
    createuser -P

enter psql
    
    psql
 
Grant user privileges

    GRANT ALL PRIVILEGES ON DATABASE [DBNAME] TO [USERNAME];
    
Exit psql with `\q`

Import database backup if possible

# Install and Configure Virtualenv
    
    pip install virtualenv

Create a virtualenv named `sjtfl`

    sudo virtualenv [VIRTUALENV DIR]/sjtfl

# Install and Configure Supervisord

    pip install supervisor
    
Create the supervisord config file named `sjtfl.conf` and reference it from the supervisord.conf file.

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

    deactivate

Clone this repo inside the venv.

Creat a .env file in this cloned repo. Fill in values.

    DATABASE_USER='[USERNAME]'
    DATABASE_PASSWORD='[DBPASSWORD]'
    DATABASE_NAME='[DBNAME]'
    DATA_PATH='[DATAPATH]'
    INSTAGRAM_ACCESS_TOKEN='[ACCESSTOKEN]'

# Run Site 

    cd /etc/nginx/sites-enabled
    sudo ln -s ../sites-available/sjtfl
    sudo service nginx restart
    sudo supervisorctl start sjtfl
