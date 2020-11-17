## Events Finder Plus  
https://eventsfinderplus.herokuapp.com/

Events Finder Plus is an event search app.  Users can perform a quick search or an advanced search that will filter by location, date, or category.  Selecting an event returns the event info, venue details, as well as parking options around the venue.  

![results](./images/results.png)  

![advanced](./images/advanced.png)  

![details](./images/details.png)  

![dashboard](./images/dashboard.png)  

Users can also create an account to save events and view upcoming events in their area.  

## Prerequisites

Before you begin, ensure you have met the following requirements:
* You have an Internet browser (Chrome, Firefox, Safari, etc)
* You have a code editor (VS Code, Atom, etc)
* You have python3 and pip

## Installation

To install, follow these steps:

Via Downloading from GitHub:
1. Download this repository onto your machine by clicking the "Clone or Download" button or Fork the repo into your own Github account
2. Download and extract the zip file to a directory of your choice.

Via command line:
```
$ git clone https://github.com/puglisac/events_finder_plus.git
```


Backend Environment Setup:
In the directory you've cloned or downloaded the repo to, create the virtual environment and activate it

```
$ python3 -m venv venv
$ source venv/bin/activate
```

Install dependencies

```
(venv)$ pip3 install -r requirements.txt
```
[Install PostgreSQL](https://www.postgresql.org/download/) if you do not have it.

Create a database
```
$ createdb events_plus
```
Initialize the database

```
$ ipython
>>> %run app.py
>>> db.create_all()
>>> quit()
```

Register for an API key from [Eventful](https://api.eventful.com/) and [Google](https://console.developers.google.com/). 

Create a file called secrets.py and export:  

```
 event_key=\<your eventful key>  
 event_url="http://eventful.com"  
 google_key=\<your google key> 
``` 

Start up the Flask server
```
(venv)$ flask run
```
Navigate your preferred browser (Chrome suggested) to http://127.0.0.1:5000/

### Running Tests

Create test database

```
$ createdb events_plus_test
```
Run tests with unittest

```
$ python3 -m unittest
```

## Built Using
Languages:

- HTML/CSS
- Javascript
- Python

Framework:

- Flask
 - Flask Login
 - FlaskWTForms
- Bootstrap

Database:

- PostgreSQL
- Flask SQLAlchemy  

Password Hashing:  

- BCrypt  

APIs used:  

- Eventful API  
- Google MAPS Javscript API
- Google Places API



