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

- Dominos (requests to [Dominos online order]
        (https://order.dominos.com/en/pages/order/))
    - Pizza cost
        - [x] price of a single pizza
        - [x] price of multiple same pizzas
        - [ ] price of multiple different pizzas
    - Pizza orders
        - [x] order a single pizza
        - [x] order multiple same pizzas
        - [ ] order multiple different pizzas

- Facebook (requests to [Facebook Graph API]
    (https://developers.facebook.com/docs/graph-api))
    - [x] Post to timeline on behalf of user

- Movies (using the TMDB API)
    - [x] What movies was this person involved in (acting, directing, etc.)
    - [x] Was this person involved in this movie?
    - [x] How many movies was this person involved in?
    - [x] When did this movie come out?
    - [x] Who acted/directed/etc. in this movie?
    - [ ] Who played this character in this movie?

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

- Wolfram|Alpha (requests using [Wolfram|Alpha's API]
    (http://products.wolframalpha.com/api/))
    - [x] Run queries on natural language and get numerical output
    - [ ] Keep track of our limited number of queries (difficult due to concurrency issues)

- Yelp (requests to [Yelp API]
    (http://www.yelp.com/developers/documentation))
    - [x] Businesses by search terms
    - [x] Ratings, URL, Phone Number
    - [x] Find by location
    - [ ] Businesses appear on map
