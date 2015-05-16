## Install

``virtualenv env``

``source env/bin/activate``

``pip install -r requirements.txt``


## Run
This program has some arguments you can use:

-g or --get <number>:

  Only display numbers of actors specified by the user.

-y or --year <year>:

 Only get the actors from films after the year specified.
 
-b or --beauty:

  Display actors as follow:
  
    ActorsName has played in # movies


Now to run it just run:

``env/bin/python imdb.py <arguments>``
