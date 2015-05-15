# -*- coding: utf-8 -*-

#  Internet Movie Database (IMDb) provides a list of their top 250 movies of all times.
# Create a Python script that goes through all of these 250 movies and finds the cast of each movie.
# The script should then print out which actors appear most in these movies.
# The user should be able to control how many actors, at most,
# are printed (so you can for example ask to see only the top 10 or top 20).
# The user should also be able to filter the movies by year, or at least ask
# the script to only include movies that were released after a given year.
# The format of the output is completely up to you. You can print the actors
# in descending order, by the number of movies they have appeared in.
# You can also include the number of movies they have appeared in or even
# list the movies.

# Infos:
# http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html#The%20basic%20find%20method:%20findAll%28name,%20attrs,%20recursive,%20text,%20limit,%20**kwargs%29
import sys
import re
from bs4 import BeautifulSoup
import getopt
import urllib.request
from operator import itemgetter

BASE_URL = "http://www.imdb.com"
topUrl = BASE_URL+"/chart/top"

# The main procedure
def main(argv):

    uYear = None
    nrActors = None
    opts = ''
    beauty = False

    try:
        # Get user arguments, g is how many users to get and y is filter for
        # after which year we will be returning our result
        opts, args = getopt.getopt(argv, "g:y:bh", ["get=", "year=", "beauty", "help"])
    except getopt.GetoptError:
        pass

    for opt, arg in opts:
        if opt in ("-g", "--get"):
            nrActors = int(arg)

        if opt in ("-y", "--year"):
            uYear = int(arg)

        if opt in ("-b", "--beauty"):
            beauty = True
        if opt in ("-h", "--help"):
            printHelp()
            sys.exit(0)

    print("This program might take a while...Please wait")
    # Grab all movies in the top250 list
    MovieList = getMovieList(uYear)
    print("Grabed the movie list")
    print("Starting collecting actors from each movie")

    # Grab all the actors in each film,
    # list will be in the form of {movieID: {actorID: name, actorID: name....}, movieID: {...]...}
    allActors = getMoviesActors(MovieList)
    print("Grabed the actors list from each movie")
    print("Starting sorting the data")

    # Create an empty list to fill with the name of the actor and
    # number of roles in the top250 movies
    actorSet = {}
    for movie in allActors:
        for actor in allActors[movie]:
            # If actorID was in actorSet then raise his role number by 1
            if actor in actorSet:
                actorSet[actor]["count"] += 1
            else:
                # If the actor has not been added before we add him include raise his count by 1
                actorSet[actor] = {"name": allActors[movie][actor], "count":1}

    # Now if the actorset was filled with information we should only grap
    # actors name and his count
    if actorSet:
        finalList = [(actorSet[x]["name"],actorSet[x]["count"]) for x in actorSet]

    # Sort the list. First by how many roles each user has playd in
    # then by his name.
    finalSorted = sorted(finalList, key=lambda x: (-x[1], x[0]) )


    # We allow the user to print the list with some style

    if beauty:
        if nrActors:
            for x in finalSorted[:nrActors]:
                print("%s has played in %d movies" % (x[0],x[1]))
        else:
            for x in finalSorted:
                print("%s has played in %d movies" % (x[0],x[1]))
    # If the user has argument of how many users should be printed
    # we print out actors based on his input
    # else print all the list
    else:
        if nrActors:
            for x in finalSorted[:nrActors]:
                print(x[1],x[0])
        else:
            for x in finalSorted:
                print(x[1],x[0])

def printHelp():
    output = '''
    This program prints out the numbers of roles each actor has played in the top 250 movies
    on IMDB (The Internet Movie Database).
    You can choose between two formats, both containing the actors name and how many movies
    he as playd.
        The formats are:
        --- ActorsName has played in # movies
        --- # ActorsName

    Please make notice, this program takes a good time to run through large movie set
    so please be patience.

    Options:
        -h, --help
                Help message

        -g, --get
                How many actors to print out

        -y, --year
                From what year shall the program print out actors, the year of the films

        -b, --beauty
                Prints out: ActorsName has played in # movies
                instead of: # ActorsName
    '''
    print(output)

def getMoviesActors(movieList):
    """

    :param A list containing formatted movie list
    :return: A list containing ID of the movie and all actors in that movie including actors ID
    """
    actorsInMovies = {}

    for x in movieList:
        req = urllib.request.Request(BASE_URL+movieList[x]["Url"]+"/fullcredits")
        #print(req.full_url)
        # Header is necessary to get the right movie titles, as in the english title
        req.add_header('Accept-Language', 'en-US,en')
        # Send the request and get response
        response = urllib.request.urlopen(req)

        bsoup = BeautifulSoup(response)

        findCastList = bsoup.find("table", {"class": "cast_list"})

        findAllActors = findCastList.findAll("td", itemprop="actor")

        actors = {}
        for d in findAllActors:
            actorName = d.find("span", itemprop="name")
            actorNumber = d.find("a", href=re.compile("\/name\/nm"))
            actorID = re.match("(?:\/name\/nm)(?P<userid>\d+)", actorNumber["href"]).group("userid")
            actors[actorID] = actorName.contents[0]

        actorsInMovies[movieList[x]["ID"]] = actors

    return actorsInMovies

def getMovieList(uYear):
    """
    Get the list of all movies with all usefull information, such as TT number
    and link wich will be used elsewhere.
    :return: THe full list containing all information needed to evaluate the list
    """

    # Open a request to the IMDb webpage
    req = urllib.request.Request(topUrl)
    # Header is necessary to get the right movie titles, as in the english title
    req.add_header('Accept-Language', 'en-US,en')

    # Send the request and get response
    response = urllib.request.urlopen(req)

    # Use BeautifulSoup to manipulate the html
    bsoup = BeautifulSoup(response)

    # Movie list is in the tbody tag and in class lister-list
    findMovieList = bsoup.find("tbody", {"class": "lister-list"})
    # The information we are collecting is in a link tag ("a") containing the TT number and the title
    # of the movie
    #getMoviesList = findMovieList.findAll("a", href=re.compile("\/title\/tt"), title=re.compile(".+"))

    getMoviesList = findMovieList.findAll("td", {"class": "titleColumn"})

    # Empty return list
    MovieList = {}
    # For best result we start with number one
    for i, movieid in enumerate(getMoviesList, start=1):
        movieUrl = re.match(".+\/tt\d+", movieid.find("a", title=re.compile(".+"))["href"]).group(0)
        movieNumber = re.match("(?:\/title\/tt)(?P<movieid>\d+)", movieid.find("a", title=re.compile(".+"))["href"]).group("movieid")
        extractedYear = movieid.find("span", {"class": "secondaryInfo", "name":"rd"}).contents[0]
        movieYear = int(re.match("(?:\()(?P<movieYear>\d+)(?:\))", extractedYear).group("movieYear"))
        movieTitle = movieid.find("a", href=re.compile(".+"), title=re.compile(".+")).contents[0]

        if uYear and movieYear>uYear:
            MovieList[i] = {"ID":movieNumber,"Title":movieTitle, "Url":movieUrl}
        elif uYear and movieYear<uYear:
            continue
        else:
            MovieList[i] = {"ID":movieNumber,"Title":movieid.contents[0], "Url":movieUrl}

    return MovieList

if __name__ == '__main__':
    main(sys.argv[1:])