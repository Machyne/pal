var http = require('http')
  , querystring = require('querystring')
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
      callback(req, res, querystring.parse(queryData));
    });
  } else {
    // Only allow posts.
    res.writeHead(405, {'Content-Type': 'text/plain'});
    res.end();
  }
};

var dominosHandler = function (req, res, post) {
  console.log(post);
  // Handle needed top level parameters.
  var need = ['phone', 'firstName', 'lastName', 'email', 'address', 'card'];
  for (var i = 0; i < need.length; i++) {
    var key = need[i];
    if (!post.hasOwnProperty(key)) {
      res.writeHead(400, {'Content-Type': 'text/plain'});
      return res.end('Need key `' + key + '`.');
    };
  };

  // Handle needed card parameters.
  var need_card = ['num', 'type', 'expire', 'cvv', 'zip'];
  for (var i = 0; i < need_card.length; i++) {
    var key = need_card[i];
    if (!post.card.hasOwnProperty(key)) {
      res.writeHead(400, {'Content-Type': 'text/plain'});
      return res.end('Need key `card.' + key + '`.');
    };
  };

  // TODO handle actual order.

  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Pizza complete.');
};

http.createServer(function(req, res) {
  processReq(req, res, dominosHandler);
}).listen(8000);
console.log('Server listening on port 8000.');
