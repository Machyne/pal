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
