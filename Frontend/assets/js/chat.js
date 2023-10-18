let checkout = {};

$(document).ready(function() {
  let $messages = $('.messages-content'),
    d, h, m,
    i = 0,
    userID = '';

  $(window).load(function() {
    $messages.mCustomScrollbar();
    insertResponseMessage('Hi there, I\'m your personal Concierge. How can I help?');
  });

  function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
      scrollInertia: 10,
      timeout: 0
    });
  }

  function setUserID() {
    d = new Date();
    userID = "user".concat(d.getMinutes().toString(), d.getMilliseconds().toString());
  }

  function setDate() {
    d = new Date();
    let hours = d.getHours();
    let am_pm = hours >= 12 ? "PM" : "AM";

    let timestamp = (hours % 13).toString() + ':' + (d.getMinutes() < 10 ? '0' : '') + d.getMinutes() + ' ' + am_pm;

    $('<div class="timestamp">' + timestamp + '</div>').appendTo($('.message:last'));
  }

  function callChatbotApi(message) {
    console.log("userID line 33:", userID)
    if (userID === '') {
      setUserID();
    }
    console.log("userID line 37:", userID)
    return sdk.chatbotPost({}, {
      messages: [{
        type: 'unstructured',
        unstructured: {
          text: message
        }}, {
        type: 'unstructured',
        unstructured: {
          text: userID
        }
      }]
    }, {});
  }

  function insertMessage() {
    msg = $('.message-input').val();
    msg = $.trim(msg);
    // console.log("from insertMessage line 54:", msg)
    if (msg === '') {
      return false;
    }

    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new').css('width', 'fit-content');
    setDate();
    $('.message-input').val(null);
    $('.message-input').attr('placeholder', "Type message...")
    updateScrollbar();

    callChatbotApi(msg)
      .then((response) => {
        console.log(response.data);
        let data = response.data;

        if (data.messages && data.messages.length > 0) {
          console.log('received messages from chatbot:', data.messages.length);

          for (let j_str of data.messages) {
            message = JSON.parse(j_str);
            if ('unstructured' in message) {
              insertResponseMessage(message.unstructured.text);
            } else if (message.type === 'structured' && message.structured.type === 'product') {
              var html = '';
              insertResponseMessage(message.structured.text);

              setTimeout(function() {
                html = '<img src="' + message.structured.payload.imageUrl + '" witdth="200" height="240" class="thumbnail" /><b>' +
                  message.structured.payload.name + '<br>$' +
                  message.structured.payload.price +
                  '</b><br><a href="#" onclick="' + message.structured.payload.clickAction + '()">' +
                  message.structured.payload.buttonLabel + '</a>';
                insertResponseMessage(html);
              }, 1100);
            } else {
              console.log('not implemented');
            }
          }
        } else {
            insertResponseMessage('Oops, something went wrong. Please try again.#1');
          }
        }
      )
      .catch((error) => {
        console.log('an error occurred', error);
        insertResponseMessage('Oops, something went wrong. Please try again.#2');
      });
  }

  // $('.message-submit').click(function() {
  //   insertMessage();
  // });

  $(window).on('keydown', function(e) {
    if (e.which == 13) {
      //alert('enter')
      insertMessage();
      return false;
    }
  });

  function insertResponseMessage(content) {
    $('<div class="message loading new"><figure class="avatar"><img src="https://media.tenor.com/images/4c347ea7198af12fd0a66790515f958f/tenor.gif" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function() {
      $('.message.loading').remove();
      $('<div class="message new"><figure class="avatar"><img src="https://media.tenor.com/images/4c347ea7198af12fd0a66790515f958f/tenor.gif" /></figure>' + content + '</div>').appendTo($('.mCSB_container')).addClass('new').css('width', 'fit-content');
      setDate();
      updateScrollbar();
      i++;
    }, 500);
  }

});
