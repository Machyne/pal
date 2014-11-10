Feature Extraction
==================

Examples:
---------

**"How many movies was Tom Hanks in?"**

    [('How', 'WRB'),
     ('many', 'JJ'),
     ('movies', 'NNS'),
     ('was', 'VBD'),
     ('Tom', 'NNP'),
     ('Hanks', 'NNP'),
     ('in', 'IN'),
     ('?', '.')]
    
    { keywords: ["movies"],
      nouns: [("movies", "NNS"), ("Tom Hanks", "PERSON")],
      tense: "past",
      isQuestion: true,
      questionType: "quantity" }

**"Where is the nearest Starbucks?"**

    [('Where', 'WRB'),
     ('is', 'VBZ'),
     ('the', 'DT'),
     ('nearest', 'JJS'),
     ('Starbucks', 'NNP'),
     ('?', '.')]    
    
    { keywords: ["nearest", "starbucks"],
      nouns: [("Starbucks", "NNP")],
      tense: "present",
      isQuestion: true,
      questionType: "location" }

**"Find me an expensive coffee."**

    [('Find', 'NNP'),
     ('me', 'PRP'),
     ('an', 'DT'),
     ('expensive', 'JJ'),
     ('coffee', 'NN'),
     ('.', '.')]
    
    { keywords: ["find", "coffee"],
      nouns: [("person", "me"), ("thing", "coffee")],
      tense: "present",
      isQuestion: false,
      actionType: "location" }

**"Is there a Starbucks nearby?"**

    [('Is', 'VBZ'),
     ('there', 'EX'),
     ('a', 'DT'),
     ('Starbucks', 'NNP'),
     ('nearby', 'NN'),
     ('?', '.')]
    
    { keywords: ["starbucks", "nearby"],
      nouns: [("place", "Starbucks")],
      tense: "present",
      isQuestion: true,
      questionType: "boolean" }

**"Do dogs dream?"**

    [('Do', 'NNP'),
     ('dogs', 'NNS'),
     ('dream', 'VB'),
     ('?', '.')]
    
    { keywords: ["dogs", "dream"],
      nouns: [("thing", "dogs")],
      tense: "present",
      isQuestion: true,
      questionType: "boolean" }

**"Do androids dream of electric sheep?"**

    [('Do', 'NNP'),
     ('androids', 'NNS'),
     ('dream', 'VB'),
     ('of', 'IN'),
     ('electric', 'JJ'),
     ('sheep', 'NN'),
     ('?', '.')]
    
    { keywords: ["androids", "dream", "sheep"],
      nouns: [("thing", "androids"), ("thing", "sheep")],
      tense: "present",
      isQuestion: true,
      questionType: "boolean" }

**"Do electric sheep dream of androids?"**

    [('Do', 'NNP'),
     ('electric', 'JJ'),
     ('sheep', 'VB'),
     ('dream', 'NN'),
     ('of', 'IN'),
     ('androids', 'NNS'),
     ('?', '.')]
    
    { keywords: ["androids", "dream", "sheep"],
      nouns: [("thing", "androids"), ("thing", "sheep")],
      tense: "present",
      isQuestion: true,
      questionType: "boolean" }

**"Call Jenny."**

    [('Call', 'NNP'),
     ('Jenny', 'NNP'),
     ('.', '.')]
    
    { keywords: ["call"],
      nouns: [("Person", "Jenny")],
      tense: "present",
      isQuestion: false,
      actionType: "phone" }

**"Is the Moon closer to Earth than the Sun?"**

    [('Is', 'VBZ'),
     ('the', 'DT'),
     ('Moon', 'NNP'),
     ('closer', 'NN'),
     ('to', 'TO'),
     ('Earth', 'NNP'),
     ('than', 'IN'),
     ('the', 'DT'),
     ('Sun', 'NNP'),
     ('?', '.')]
    
    { keywords: ["moon", "closer", "earth", "sun"],
      nouns: [("place", "moon"), ("place", "earth"), ("place", "sun")],
      tense: "present",
      isQuestion: true,
      questionType: "boolean" }

**"Where does Matt Cotter live?"**

    [('Where', 'WRB'),
     ('does', 'VBZ'),
     ('Matt', 'NNP'),
     ('Cotter', 'NNP'),
     ('live', 'JJ'),
     ('?', '.')]
    
    { keywords: ["where", "Matt Cotter", "live"],
      nouns: [("person", "Matt Cotter")],
      tense: "present",
      isQuestion: true,
      questionType: "location" }

**"What is Matt Cotter’s address?"**

    [('What', 'WP'),
     ('is', 'VBZ'),
     ('Matt Cotter', 'NNP'), ("'s", 'POS'),
     ('address', 'NN'),
     ('?', '.')]
    
    { keywords: ["address"],
      nouns: [("person", "Matt Cotter"), ("thing", "address")],
      tense: "present",
      isQuestion: true,
      questionType: "location" }

**"Is Hogan Brothers a good place to eat?"**

    [('Is', 'VBZ'),
     ('Hogan', 'NNP'),
     ('Brothers', 'NNPS'),
     ('a', 'DT'),
     ('good', 'JJ'),
     ('place', 'NN'),
     ('to', 'TO'),
     ('eat', 'VB'),
     ('?', '.')]
    
    { keywords: ["Hogan Brothers", "good", "eat"],
      nouns: [("place", "Hogan Brothers"), ("place", "place")],
      tense: "present",
      isQuestion: true,
      questionType: "boolean" }

**"Which is better, The Dark Knight, or The Empire Strikes Back?"**

    [('Which', 'WDT'),
     ('is', 'VBZ'),
     ('better', 'RBR'),
     (',', ','),
     ('The', 'DT'),
     ('Dark', 'NNP'),
     ('Knight', 'NNP'),
     (',', ','),
     ('or', 'CC'),
     ('The', 'DT'),
     ('Empire', 'NNP'),
     ('Strikes', 'NNP'),
     ('Back', 'NNP'),
     ('?', '.')]
    
    { keywords: ["better", "The Dark Knight", "The Empire Strikes Back"],
      nouns: [("title", "The Dark Knight"), ("title", "The Empire Strikes Back")],
      tense: "present",
      isQuestion: true,
      questionType: "choice" }
