# alertmanager-assure1-middleware
This python flask app ingests alertmanager webhook alerts at
localhost:5000/alerts and forwards them to assureone. 

## Setup

    python3 -m venv venv
    pip3 install -r requirements.txt
    vim .venv
    flask run

## Sample .env

    FLASK_APP=alertassure1
    FLASK_ENV=development
    FLASK_DEBUG=1
    ASSURE1_ENDPOINT=http://servername.company.com:10080


## Author
[Cameron King](http://cameronking.me)

## Copying
This software is released under the MIT License. See LICENSE for details.

