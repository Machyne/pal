# PAL
---------

## Services
- Bon Appetit (actively scraped from [Bon Appetit website]
    (http://carleton.cafebonappetit.com/cafe/))
    - [x] Single dining hall, single day, any or all meals

- Dictionary/Thesaurus (actively scraped from [dictionary]
        (http://dictionary.reference.com/browse/) or [thesaurus]
        (http://www.thesaurus.com/browse/))
    - [x] Definitions
    - [x] Synonyms
    - [x] Antonyms

- Directory (pre-scraped from [Carleton campus directory]
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

- Facebook (requests to [Facebook Graph API](https://developers.facebook.com/docs/graph-api))
    - [x] Post to timeline on behalf of user

- Translations (requests through [UltraLingua REST API]
    (http://api.ultralingua.com/ulapi/rest)
    - [x] From English to {Spanish, French, German, Italian, Portuguese}
    - [x] From {Spanish, French, German, Italian, Portuguese} to English
    - [x] Between {Spanish, French, German, Italian, Portuguese}
    - [ ] Use correct SpeechSynthesisVoice for the destination language

- Weather (requests to [Yahoo weather API]
        (https://query.yahooapis.com/v1/public/yql?))
    - [x] High/low temperatures
    - [x] Snow/rain
    - [x] General forecast
    - [x] Geolocation

- Wolfram|Alpha (requests using Wolfram|Alpha's API)
    - [x] Run queries on natural language and get numerical output
    - [ ] Keep track of our limited number of queries (difficult due to concurrency issues)

- Yelp (requests to [Yelp API]
    (http://www.yelp.com/developers/documentation))
    - [x] Businesses by search terms
    - [x] Ratings, URL, Phone Number
    - [x] Find by location
    - [ ] Businesses appear on map
    
## Installation & Running
--------------------------------
### Requirements
- Python 2.7 with `pip`
	- Required Python packages in requirements.txt
- PostgreSQL 9.3 required for directory service
- Node.js > v0.10 for pizza service
- Web server capable of running wsgi applications for deployment

### Base Installation
We recommend installing PAL in a python virtual environment by using the `virtualenv` package. Use pip to install virtualenv then create a new virtualenv in the pal directory 

`virtualenv env`

and activate the virtual environment

`source env/bin/activate`

If not using the directory service and/or PostgreSQL is not installed, remove the line containing `psycopg2` from the `requirements.txt` file. Install the required packages 

`pip install -r requirements.txt`

Next, install the required `nltk` libraries. Open a python shell and type

~~~
>>> import nltk
>>> nltk.download()
~~~

and install `maxent_ne_chunker`, `maxent_treebank_pos_tagger`, `punkt`, `qc`, and `words`.

Obtain API keys for TMDB, Wolfram, and Yelp and insert them into `config.py`. Obtain a Facebook app ID and insert it into `static/home.js`. 

PAL is now ready to run locally. Start it by running `python server.py`. PAL can be accessed by connecting to `localhost:5000` in a browser. 

### Pizza Service Installation
The pizza service requires Node.js or io.js. Install one of these and `npm`. Navigate to the `api/dominos` directory and run 

`npm install`

Next, install `forever` with

`npm install -g forever`

Start the pizza server with 

`forever start server.js`

### Scraping the Directory
In order for the directory service to function, the directory must be pre-scraped. Navigate to the `api/directory` directory. Insert the username and password for the database in the `stalkernet_scraper.py` file with the format `postgresql://username:password@database_url/table_name`

Create the database schema by running

`python models.py`

Populate the buildings, majors, and departments tables by running

`python stalkernet_scraper.py -b buildings.txt`
`python stalkernet_scraper.py -m majors.txt`
`python stalkernet_scraper.py -d depts.txt`

Finally, scrape the directory with

`python stalkernet_scraper.py -s`

### Installing in Apache
PAL can be run by Apache HTTP Server by using the `mod_wsgi` module. Modify the `pal.wsgi` file by changing the absolute path to the `pal` directory on the server. The last known functioning Apache configuration file is 

~~~
<VirtualHost *:443>
        Servername pal.rocks

        SSLEngine On
        SSLCertificateFile /etc/ssl/pal_rocks.crt
        SSLCertificateKeyFile /etc/ssl/palserver.key
        SSLCertificateChainFile /etc/ssl/pal_rocks.ca-bundle

        WSGIDaemonProcess pal user=pal-server group=servergroup threads=5
        WSGIScriptAlias / /var/www/pal/pal.wsgi
        DocumentRoot /var/www/pal
        ErrorLog /var/www/pal/error.log
        LogLevel debug
        Alias /favicon.ico /var/www/pal/pal.ico
        <Directory /var/www/pal>
                WSGIApplicationGroup %{GLOBAL}
                Order allow,deny
                Allow from all
        </Directory>
</VirtualHost>

<VirtualHost *:80>
        ServerAlias cmc307-01.mathcs.carleton.edu
        Servername pal.rocks
        Redirect permanent / https://www.pal.rocks
</VirtualHost>
~~~


