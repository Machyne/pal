# PAL
---------

## Installation & Running
--------------------------------
### Requirements
- Python 2.7 with `pip`
    - Required Python packages in requirements.txt
- PostgreSQL 9.3 required for directory service
- Node.js > v0.10 for pizza service
- Web server capable of running wsgi applications for deployment

### Base Installation
We recommend installing PAL in a python virtual environment by using the `virtualenv` package.
Use pip to install virtualenv then create a new virtualenv in the pal directory

```sh
virtualenv env
```

and activate the virtual environment

```sh
source env/bin/activate
```

If not using the directory service and/or PostgreSQL is not installed, remove the line containing
`psycopg2` from the `requirements.txt` file. Install the required packages

```sh
pip install -r requirements.txt
```

Next, install the required `nltk` libraries. Open a python shell and type

```python
>>> import nltk
>>> nltk.download()
```

and install `maxent_ne_chunker`, `maxent_treebank_pos_tagger`, `punkt`, `qc`, and `words`.

Obtain API keys for TMDB, Wolfram, and Yelp and insert them into `config.py`.
Obtain a Facebook app ID and insert it into `static/home.js`.

PAL is now ready to run locally. Start it by running `python server.py`.
PAL can be accessed by connecting to `localhost:5000` in a browser.

### Git Hooks
To install the git hooks run the following command from the project root:

```sh
hooks/install.sh
```

Which will install the scripts in `hooks` by creating symlinks to them in your 
`.git` directory.

### Hill Climb Instructions
To ensure that queries are properly sorted into the proper services,
hill climbing should be run. From the base directory, run

```sh
python -m pal.heuristics.hill_climb.hill_climb
```

After running hill climbing, updated heuristics values can be found in the
`pal/heuristics/hill_climb/climbed_values` directory, and will be automatically
referenced by the rest of PAL. Hill climbing should be re-run whenever a new
service is added to PAL.

### Pizza Service Installation
The pizza service requires Node.js or io.js. Install one of these and `npm`.
Navigate to the `api/dominos` directory and run

```sh
npm install
```

Next, install `forever` with

```sh
npm install -g forever
```

Start the pizza server with

```sh
forever start server.js
```

### Scraping the Directory
In order for the directory service to function, the directory must be
pre-scraped. Navigate to the `api/directory` directory. Insert the
username and password for the database in the `stalkernet_scraper.py`
file with the format `postgresql://username:password@database_url/table_name`

Create the database schema by running

```sh
python models.py
```

Populate the buildings, majors, and departments tables by running

```sh
python stalkernet_scraper.py -b buildings.txt
python stalkernet_scraper.py -m majors.txt
python stalkernet_scraper.py -d depts.txt
```

Finally, scrape the directory with

```sh
python stalkernet_scraper.py -s
```

### Installing in Apache
PAL can be run by Apache HTTP Server by using the `mod_wsgi` module.
The [Flask documentation](http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/)
has pretty detailed instructions on how to set this up.


## Services
--------------------------------
### Bon Appetit (actively scraped from [Bon Appetit website]
        (http://carleton.cafebonappetit.com/cafe/))
    - [x] Single dining hall, single day, any or all meals

### Dictionary/Thesaurus (actively scraped from [dictionary]
        (http://dictionary.reference.com/browse/) or [thesaurus]
        (http://www.thesaurus.com/browse/))
    - [x] Definitions
    - [x] Synonyms
    - [x] Antonyms

### Directory (pre-scraped from [Carleton campus directory]
        (http://apps.carleton.edu/campus/directory/))
    - Single-person queries
        - [x] Professor offices / Student rooms
        - [x] email addresses (both)
        - [x] phone numbers (both)
        - [ ] departments/majors (professors/students)
        - [ ] Class year
    - Multi-person queries
        - [ ] All students on a floor / in a dorm
        - [ ] All students for a given major
        - [ ] All professors in a department
        - [ ] "Show me all the Brians on campus"

### Dominos (requests to [Dominos online order]
        (https://order.dominos.com/en/pages/order/))
    - Pizza cost
        - [x] price of a single pizza
        - [x] price of multiple same pizzas
        - [ ] price of multiple different pizzas
    - Pizza orders
        - [x] order a single pizza
        - [x] order multiple same pizzas
        - [ ] order multiple different pizzas

### Facebook (requests to [Facebook Graph API]
        (https://developers.facebook.com/docs/graph-api))
    - [x] Post to timeline on behalf of user

### Movies (using the [TMDB API]
        (https://www.themoviedb.org/documentation/api))
    - [x] What movies was this person involved in (acting, directing, etc.)
    - [x] Was this person involved in this movie?
    - [x] How many movies was this person involved in?
    - [x] When did this movie come out?
    - [x] Who acted/directed/etc. in this movie?
    - [ ] Who played this character in this movie?

### Translations (requests through [UltraLingua REST API]
        (http://api.ultralingua.com/ulapi/rest))
    - [x] From English to {Spanish, French, German, Italian, Portuguese}
    - [x] From {Spanish, French, German, Italian, Portuguese} to English
    - [x] Between {Spanish, French, German, Italian, Portuguese}
    - [ ] Use correct SpeechSynthesisVoice for the destination language

### Weather (requests to [Yahoo weather API]
        (https://query.yahooapis.com/v1/public/yql?))
    - [x] High/low temperatures
    - [x] Snow/rain
    - [x] General forecast
    - [x] Geolocation

### Wolfram|Alpha (requests using [Wolfram|Alpha's API]
        (http://products.wolframalpha.com/api/))
    - [x] Run queries on natural language and get numerical output
    - [ ] Keep track of our limited number of queries (difficult due to concurrency issues)

### Yelp (requests to [Yelp API]
        (http://www.yelp.com/developers/documentation))
    - [x] Businesses by search terms
    - [x] Ratings, URL, Phone Number
    - [x] Find by location
    - [ ] Businesses appear on map
