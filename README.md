# Backend API for School Management System

This is the backend API written for the School Management System

## How to start in virtual environment


Clone the repository to a directory using terminal or git bash:
```sh
$ git clone https://github.com/HenryYDJ/flaskAPI.git
$ cd flaskAPI
```

Install the virtualenv package
```sh
$ pip3 install virtualenv
```
OR in Linux:
```sh
sudo apt-get install python3-venv
```

Create the virtual environment
```sh
$ python3 -m venv .venv
```

Activate the virtual environment

Mac OS/Linux
```sh
$ source .venv/bin/activate
```

Windows
```sh
.venv\Scripts\activate
```

Install all dependencies:
```sh
$ pip3 install -r requirements.txt
```

Start the API server:
```sh
$ python3 flaskAPI.py
```

## How to use

Use postman to work with the API interfaces.

## View the SQLite Database

Install SQL Browser

On Windows, download from [`SQLite Brower`](https://sqlitebrowser.org/dl/) and install

On Ubuntu use the following shell commands:
```sh
$ sudo add-apt-repository -y ppa:linuxgndu/sqlitebrowser
$ sudo apt-get update
$ sudo apt-get install sqlitebrowser
```



## Project structure (Under construction, this part is just a template as the placeholder)

After you check out this code you may need to rename folder `project` to something more relevant your needs. I prefer to have own name for each project. Next step to change all mentions of the word `project` in your code. I don't add any code generators for this project since anyway make code reviews every time starting new Flask project by adding or removing extensions or some parts of the source code.

    .
    ├── Dockerfile

If you need to run the project inside `Docker`

    ├── Makefile
    ├── README.md
    ├── babel.cfg

Configuration for `Flask-Babel`, generally you don't need to edit this file unless you use a different template system.

    ├── celery_run.py

To run Celery broker use this file.

    ├── entry.py

To run Flask server use this file, it is already prepared for `uwsgi`, `mod_wsgi` or other wsgi web server modules.

    ├── local.example.cfg

Rename this file to `local.cfg` and use on different versions on product, test and development environment.

    ├── manage.py

Use this file to register management commands. Alembic commands set already included with `db` prefix. 

    ├── migrations
    │   ├── README
    │   ├── alembic.ini
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions
    │       └── ee69294e63e_init_state.py

Migrations folder contains all your database migrations. 

    ├── packages.txt

This file used by Docker and contains all Ubuntu packages that need to be installed on a fresh Ubuntu server.

    ├── project

Your project code is here

    │   ├── __init__.py
    │   ├── api
    │   │   ├── __init__.py
    │   │   └── views.py

Put here your admin or API views created by `Flask-Admin` or `Flask-Restless`.

    │   ├── app.py

This cornerstone part of the project structure. But export only two functions `create_app` and `create_celery`. More info [inside file](https://github.com/xen/flask-project-template/blob/master/project/app.py). 

    │   ├── auth
    │   │   ├── __init__.py
    │   │   ├── forms.py
    │   │   ├── models.py
    │   │   ├── templates
    │   │   │   └── auth
    │   │   │       ├── index.html
    │   │   │       ├── macros.html
    │   │   │       ├── profile.html
    │   │   │       └── settings.html
    │   │   └── views.py

`project.auth` is working example of blueprint which shows how to organize user authentication using different OAuth providers, such as Facebook, GitHub, Twitter, etc. [Full list of supported social backends](http://psa.matiasaguirre.net/docs/backends/index.html#social-backends) available in `python-social-auth` documentation page.

    │   ├── config.py

The file contains default configuration for the project. My approach to have code that can run with defaults. When you don't need special Postgres or other database features on deployment environment for testing purpose enough to use SQLite, but a set of projects that are database agnostic is very limited in real life. More about [configuration](#configuration) is separate chapter.

    │   ├── docs
    │   │   └── index.md

Have a section with simple text files is common for sites. Sometimes you need to have "Contacts" or "Features" page without dynamic elements. Just simple HTML. Here are these files. By default available by `frontend.page` route, if you need to change it see inside [`frontend/views.py`](https://github.com/xen/flask-project-template/blob/master/project/frontend/views.py).

    │   ├── extensions.py

All Flask extensions registered here. You can access them by import from this file. More information is available in [configuration](#configuration) chapter.

    │   ├── frontend
    │   │   ├── __init__.py
    │   │   ├── templates
    │   │   │   └── frontend
    │   │   │       ├── index.html
    │   │   │       └── user_profile.html
    │   │   └── views.py

Frontpage of the site and some useful common pages combined in one blueprint. Generally, each site section has its blueprint, but if you are not sure where to put something small put it here.

    │   ├── models.py

Helper to access `SQLAlchemy` models. I found very comfortable to have all models collected together in one place. Since your models always mapped into the database you never should have conflict errors using the same name because the database doesn't allow to have several tables with the same name.

    │   ├── tasks.py

Celery tasks placed here. If you have worked with Celery you will found yourself familiar with this concept. If you need to spit tasks in different files then follow the idea of `models.py`.

    │   ├── templates
    │   │   ├── base.html
    │   │   ├── counter.html
    │   │   ├── macros.html
    │   │   ├── misc
    │   │   │   ├── 403.html
    │   │   │   ├── 404.html
    │   │   │   ├── 405.html
    │   │   │   ├── 500.html
    │   │   │   └── base.html
    │   │   ├── nav.html
    │   │   └── page.html

There are basic site templates. Each blueprint has it's own `template/<blueprint_name>` folder because of the recommendation of Jinja documentation. If you don't want to read how the Jinja environment lookup working then just follow this pattern. For your convenience `misc` folder contains templates for common error pages.   

    │   ├── translations
    │   │   ├── en
    │   │   │   └── LC_MESSAGES
    │   │   │       └── messages.po
    │   │   ├── messages.pot
    │   │   └── ru
    │   │       └── LC_MESSAGES
    │   │           ├── messages.mo
    │   │           └── messages.po

If you don't need internationalization you can ignore this folder. If you don't then your translation strings located here. `Po` files are standard for translation and internationalization of different projects. Always cover text inside `_` (underscore) function, project code contains all needed examples.

    │   └── utils.py

Trash-can for all common usefulness that can't find a place in other parts of the code.

    ├── requirements.txt

All project dependencies installed by `pip`.

    ├── setup.py

This file makes your folder python project that can be wrapped into an egg and distributed by DevOps. This part is not covered in the documentation and usually needed on past stages of the project.

    └── static
        ├── bower.json
        ├── code.js
        ├── favicon.png
        ├── libs
        ├── robots.txt
        └── style.css

All static dependencies are installed by [`bower`](http://bower.io/) packages manager. Of course, you can get rid of `node.js` as a dependency, but I found that full automation saves a vast amount of time and it is almost impossible to avoid of using popular JavaScript frameworks or compilers. Why avoid such things as `browserify` or CoffeScript? By default site already use Bootstrap.
