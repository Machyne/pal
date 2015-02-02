var queryPAL = function(query, data, callback) {
  $.ajax({
    type: 'POST',
    url: '/api/pal',
    data: {
      query: query,
      client: 'web',
      'user-data': data
    },
    success: function (response) {
      callback(query, response.result);
    },
    error: function () {
      $('.prompt').removeAttr('disabled');
      $('#go-btn').removeAttr('disabled');
    }
  });
};

function expandData (el) {
  $(el).toggleClass('expanded');
  return true;
}

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

  var showResult = function (query, result) {
    if (result.status == 2) {
      $('#user-data').html('');
      for (need in result.needs) {
        var type = result.needs[need].type;
        var def = result.needs[need].default;
        switch(type) {
          case 'loc':
            var li = $('<li data-type="' + type + '" data-param="' + need +
                       '">Location: <input type="text" class="address" ' +
                       'style="width: 200px"><br><div class="map" ' +
                       'style="width: 500px; height: 400px; display: ' +
                       'inline-block;"></div>' +
                       '<input type="tel" class="lat" style="display:none">' +
                       '<input type="tel" class="lon" style="display:none">')
            $('#user-data').append(li);
            li = $('#user-data li').last();
            li.hide()
            var finish = function () {
              li.find('.map').locationpicker({
                location: {latitude: def[0], longitude: def[1]},
                radius: 0,
                inputBinding: {
                  latitudeInput: li.find('.lat'),
                  longitudeInput: li.find('.lon'),
                  locationNameInput: li.find('.address')
                },
                enableAutocomplete: true
              });
              li.show();
            };
            if (navigator.geolocation) {
              navigator.geolocation.getCurrentPosition(function (pos) {
                def[0] = pos.coords.latitude;
                def[1] = pos.coords.longitude;
                finish();
              });
            } else {
              finish();
            };
            break;
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
    if($('#speak-check').is(':checked')) {
      // to avoid pronouncing 'li' etc.
      var no_html = '';
      if (result.status == 2) {
        no_html = 'Sorry, I need to know more';
      } else {
        no_html = result.summary.replace(/(<([^>]+)>)/ig, '');
      };
      var utterance = new SpeechSynthesisUtterance(no_html);
      utterance.rate = 1.1;
      window.speechSynthesis.speak(utterance);
    }

    $('#prompt').val('');
    $('#prompt').focus();
    prompt.removeAttr('disabled');
    $('#go-btn').removeAttr('disabled');
  };
  var prompt = $('.prompt');
  var lastQuery = '';
  var getUserData = function () {
    var ret = {}
    $('#user-data li').each(function () {
      var li = $(this);
      var need = li.attr('data-param');
      var type = li.attr('data-type');
      switch(type) {
        case 'loc':
          ret[need] = '' + li.find('.lat').val() + ',' + li.find('.lon').val()
          break;
        case 'str':
          ret[need] = li.find('input').val();
          break;
      }
    });
    return ret;
  };
  var sendQuery = function () {
    var query = prompt.val();
    if (query.length > 0 &&
        (query.trim() != lastQuery.trim() ||
         $('#user-data').html().trim() != '')) {
      prompt.attr('disabled', 'disabled');
      $('#go-btn').attr('disabled', 'disabled');
      lastQuery = query;
      queryPAL(query, getUserData(), showResult);
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

});
