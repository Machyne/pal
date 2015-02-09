var queryPAL = function(query, usdat, clidat, callback) {
  $.ajax({
    type: 'POST',
    url: '/api/pal',
    data: {
      query: query,
      client: 'web',
      'user-data': usdat,
      'client-data': clidat
    },
    success: function (response) {
      callback(query, response.result);
    },
    error: function () {
      console.log('server error');
      $('.prompt').removeAttr('disabled');
      $('#go-btn').removeAttr('disabled');
    }
  });
};

function expandData (el) {
  $(el).toggleClass('expanded');
  return true;
}

var mapGo;

$(document).ready(function () {

  // show speak checkbox only if browser supports it
  if ('SpeechSynthesisUtterance' in window && !navigator.userAgent.match(/(iPad|iPhone|iPod)/g) ? true : false)  {
    $("#speak").show();
    // load user preference on speech from cookie
    if (document.cookie) {
      if (document.cookie === 'speech=true') {
        $("#speak-check").attr("checked", true);
      }
    }
  }

  var prompt = $('#prompt');
  var lastQuery = '';

  // FOR THE LOVE OF GOD PLEASE COMMENT ME WHOEVER WROTE THIS
  var showResult = function (query, result) {
    if (result.status == 3) {
      var needs = result.needs_client;
      var keys = Object.keys(needs);
      var sendError = function (msg) {
        $('#user-data').html('');
        $('.history').prepend('<li class="error"><div class="query">' +
                              query + '</div><div class="result">' +
                              msg + '</div></li>');
      };
      var handleIndex = function (i, data) {
        if (i >= keys.length) {
          queryPAL(query, getUserData(), data, showResult);
          return true;
        };
        var need = keys[i];
        var type = needs[need].type;
        var msg = needs[need].msg;
        switch(type) {
          case 'loc':
            if (navigator.geolocation) {
              navigator.geolocation.getCurrentPosition(function (idx) {
                return function(pos) {
                  data[need] = pos.coords.latitude + ',' + pos.coords.longitude;
                  return handleIndex(idx + 1, data);
                };
              }(i), function (posError) {
                return sendError(msg);
              });
            } else {
              return sendError(msg);
            } 
            break;
          default:
            return sendError(msg);
        };
      };
      handleIndex(0, {});
    } else if (result.status == 2) {
      $('#user-data').html('');
      for (need in result.needs_user) {
        var type = result.needs_user[need].type;
        var def = result.needs_user[need].default;
        switch(type) {
          case 'str':
            $('#user-data').append(
              '<li data-type="' + type + '" data-param="' + need + '">' +
              need + ': ' + '<input type="text" value="' + def + '"></li>')
            break;
          default:
            console.log('unknown requested data type')
        }
      };
    } else if (result.status == 1) {
      $('#user-data').html('');
      var data = '';
      if (result.hasOwnProperty('data')) {
        data = '<div class="data" onclick="expandData(this);">...<br>' +
               result.data.replace(/\n+/ig, '<br>') + '</div>'
      }
      $('.history').prepend('<li><div class="query">' + query +
                            '</div><div class="result">' +
                            result.summary.replace(/\n+/ig, '<br>') +
                            '</div>' + data + '</li>');
    } else {
      $('#user-data').html('');
      $('.history').prepend('<li class="error"><div class="query">' +
                            query + '</div><div class="result">' +
                            result.summary.replace(/\n+/ig, '<br>') +
                            '</div></li>');
    };

    if($('#speak-check').is(':checked') && result.status <= 1) {
      // to avoid pronouncing 'li' etc.
      var no_html = result.summary.replace(/(<([^>]+)>)/ig, '');
      var utterance = new SpeechSynthesisUtterance(no_html);
      utterance.rate = 1.1;
      window.speechSynthesis.speak(utterance);
    };

    $('#prompt').val('');
    $('#prompt').focus();
    prompt.removeAttr('disabled');
    $('#go-btn').removeAttr('disabled');
  };

  var getUserData = function () {
    var ret = {}
    $('#user-data li').each(function () {
      var li = $(this);
      var need = li.attr('data-param');
      var type = li.attr('data-type');
      switch(type) {
        case 'str':
          ret[need] = li.find('input').val();
          break;
      }
    });
    return ret;
  };

  var sendQuery = function () {
    var query = prompt.val();
    if (query.length > 0) {
      prompt.attr('disabled', 'disabled');
      $('#go-btn').attr('disabled', 'disabled');
      lastQuery = query;
      queryPAL(query, getUserData(), {}, showResult);
    }
  };

  prompt.focus();

  prompt.on('keypress', function (e) {
    // 'enter' key
    if (e.which == 13) {
      sendQuery();
    }
  });

  // remember if user has checked the speech checbox
  $("#speak-check").on('click', function(event) {
    if($('#speak-check').is(':checked')) {
      document.cookie = 'speech=true;';
    }
    else {
      document.cookie = 'speech=false;';
    }
  });

  $('#go-btn').on('click', sendQuery);

  mapGo = function (el) {
    var div = $(el).parent();
    var userData = getUserData();
    var lat = div.find('.lat').val();
    var lng = div.find('.lng').val();
    userData['location'] = lat + ',' + lng;
    queryPAL(div.find('.q').val(), userData, {}, showResult);
  };

});
