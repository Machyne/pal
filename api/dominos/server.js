var http = require('http')
  , dominos = require('dominos');

var processReq = function (req, res, callback) {
  var queryData = "";
  if(req.method == 'POST') {
    req.on('data', function(data) {
      queryData += data;
      if(queryData.length > 1e6) {  // Don't flood RAM.
        queryData = "";
        res.writeHead(413, {'Content-Type': 'text/plain'}).end();
        req.connection.destroy();
      }
    });
    req.on('end', function() {
      if (typeof(queryData) !== typeof({})) {
        queryData = JSON.parse(queryData);
      };
      callback(req, res, queryData);
    });
  } else {
    res.writeHead(405, {'Content-Type': 'text/plain'});
    res.end();
  }
};

var dominosHandler = function (req, res, post) {
  console.log('\nReceived post:\n', post);
  // Handle needed top level parameters.
  var need = ['phone', 'firstName', 'lastName', 'address', 'card', 'instr'];
  for (var i = 0; i < need.length; i++) {
    var key = need[i];
    if (!post.hasOwnProperty(key)) {
      res.writeHead(400, {'Content-Type': 'text/plain'});
      return res.end(JSON.stringify({msg: 'Need key `' + key + '`.'}));
    };
  };

  // Handle needed card parameters.
  var need_card = ['num', 'type', 'expire', 'cvv', 'zip'];
  for (var i = 0; i < need_card.length; i++) {
    var key = need_card[i];
    if (!(key in post.card)) {
      res.writeHead(400, {'Content-Type': 'text/plain'});
      return res.end(JSON.stringify({msg: 'Need key `card.' + key + '`.'}));
    };
  };

  placeOrder(post, function (err) {
    if (err) {
      if (post.onlyPrice && typeof(err) === 'number') {
        res.writeHead(200, {'Content-Type': 'application/JSON'});
        return res.end(JSON.stringify({price: err}));
      };
      res.writeHead(400, {'Content-Type': 'application/JSON'});
      return res.end(JSON.stringify(err));
    }
    res.writeHead(200, {'Content-Type': 'application/JSON'});
    res.end(JSON.stringify({msg: 'Pizza complete.'}));
  });
};

http.createServer(function(req, res) {
  processReq(req, res, dominosHandler);
}).listen(8000);
console.log('Server listening on port 8000.');

var placeOrder = function (data, callback) {
  var order = new dominos.class.Order();
  order.Order.Phone = data.phone;
  order.Order.FirstName = data.firstName;
  order.Order.LastName = data.lastName;
  order.Order.Email = 'pizza@pal.rocks';

  dominos.store.find(data.address, function (storeData) {
    if (!storeData.success || !storeData.result.Stores[0]) {
      console.log('\nNo store found');
      return callback({msg: 'no stores found'});
    };
    console.log('\nAddress Data:\n', storeData.result.Address);
    order.Order.Address = storeData.result.Address;
    order.Order.Address.DeliveryInstructions = data['instr'];
    order.Order.StoreID = storeData.result.Stores[0].StoreID;

    for (var i = 0; i < data.pizzas.length; i++) {
      var pizza = data.pizzas[i];
      order.Order.Products.push({
        Code: pizza.crust,
        ID: 1,
        Options: pizza.options,
        Qty: pizza.quantity,
        isNew: true
      })
    };

    dominos.order.validate(order, function (orderData) {
      if (!orderData.success) {
        console.log('\nOrder could not be validated\n');
        return callback({msg: 'cannot validate order'});
      };

      dominos.order.price(orderData.result, function (priceData) {
        console.log('\nPrice Data:\n', priceData);
        if ('StatusItems' in priceData.result) {
          console.log('\nResult status items:\n', priceData.result.StatusItems);
        }
        if ('StatusItems' in priceData.result.Order) {
          console.log('\nOrder status items:\n', priceData.result.Order.StatusItems);
          return callback({msg: 'Bad address format'});
        }

        var cardInfo = new dominos.class.Payment();
        cardInfo.Amount = priceData.result.Order.Amounts.Customer;

        cardInfo.Number = data.card.num;
        cardInfo.CardType = data.card.type;
        cardInfo.Expiration = data.card.expire;
        cardInfo.SecurityCode = data.card.cvv;
        cardInfo.PostalCode = data.card.zip;

        order.Order.Payments.push(cardInfo);

        console.log('Total cost:', cardInfo.Amount);
        if (data.onlyPrice) {
          return callback(cardInfo.Amount)
        };

        // Place order
        dominos.order.place(order, function (orderData) {
          var curOrder = orderData.result.Order;
          console.log('\nOrder placed:\n', curOrder);
          if (curOrder.Status < 0) {
            var errorCodes = [];
            if (curOrder.StatusItems) {
              errorCodes = errorCodes.concat(curOrder.StatusItems.map(function (item) {
                return '- ' + item['Code'];
              }));
            };
            if (curOrder.CorrectiveAction) {
              errorCodes = errorCodes.concat(curOrder.CorrectiveAction.map(function (item) {
                return '- ' + item['Code'];
              }));
            };
            var details = errorCodes.join('\n');
            console.log(
                '\n######### ERROR! ########\n',
                details,
                '\n#########################\n\n'
            );
            if (curOrder.CorrectiveAction) {
              var msg = curOrder.CorrectiveAction.Detail + ': ' +
                curOrder.CorrectiveAction.Code;
            } else {
              var msg = 'One or more errors ocurred:';
            }
            return callback({msg: msg, details: details});
          }

          dominos.track.phone(orderData.result.Order.Phone, function (pizzaData) {
            console.log('\nTracking data: ', pizzaData);
            return callback();
          });
        });
      });
    });
  });
};
