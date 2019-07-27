# Pug Or Ugh API

This API create views to set up preferences to each user,
also sends a list of dogs that match with those preferences to shows them,
and you can mark dogs as liked, disliked, and undecided.

You can update your preferences whenever you want.


## To use
* Create a new Python virtual environment.

## Requirements
This project uses some requirements located on `requirements.txt` file, to install:
```
(env) $ pip install -r requirements.txt
```

## Run app
To run the application you need to enter the first `backend` folder and run the server as follows:
```
(env) $ python manage.py migrate
(env) $ python manage.py runserver
```

To see the webpage you have to make `ctrl + click` in `http://127.0.0.1:8000/`this open a new window in your browser
```
Django version 2.2.3, using settings 'backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## To load data
If the database doesn't have data, you can add them by running the following scrip:
```
(env) $ python .\pugorugh\scripts\data_import.py
```

## Example of a view

<p align="center">
  <img src="https://github.com/luqp/Pug_or_Ugh_API/blob/master/backend/pugorugh/static/images/toReadme/Dog.png">
</p>
