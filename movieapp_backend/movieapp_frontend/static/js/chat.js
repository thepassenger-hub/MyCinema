var $height = window.innerHeight;

var $width = window.innerWidth;

$(document).ready(function(){
    $(window).resize(function(){
        $width = window.innerWidth;
        $height = window.innerHeight;
    });
    window.setInterval(function(){
        if(chat_socket.readyState == WebSocket.CLOSED) {
            // Open socket to notify if new messages between user and friends.
            chat_socket = new WebSocket('ws://' + window.location.host + '/inbox/');

            chat_socket.onopen = function open() {
                console.log('ChatWebSocket connection created.');
                showNotifications();
            };

            chat_socket.onmessage = function message(event) {
                var data = JSON.parse(event.data);
                // NOTE: We escape JavaScript to prevent XSS attacks.
                var viewed = encodeURI(data['viewed']);
                if (viewed == "false") {
                    var friend = encodeURI(data['friend']);
                    // If chat with this friend is open
                    if (friend == $('.panel-title').data("value")) {
                        // show new messages in chat
                        getMessages(friend);
                    }
                    else {
                        // otherwise get a notification
                        showNotifications();
                    }
                } else if (viewed == "true") {
                    deleteNotifications();
                }
            };

            if (chat_socket.readyState == WebSocket.OPEN) {
              chat_socket.onopen();
            }
        }
        if (socket.readyState == WebSocket.CLOSED) {
            // Open socket to notify if user is online or offline.
            socket = new WebSocket('ws://' + window.location.host + '/users/');

            socket.onopen = function open() {
              console.log('WebSockets connection created.');
            };

            socket.onmessage = function message(event) {
                  var data = JSON.parse(event.data);
                  // NOTE: We escape JavaScript to prevent XSS attacks.
                  var username = encodeURI(data['username']);
                  var user = $('.friends').filter(function () {
                    return $(this).data("value") == username;
                  });
                  var is_logged_in = encodeURI(data['is_logged_in']);
                  if (is_logged_in == 'true') {
                    user.html(username + ': Online');
                  }
                  else if(is_logged_in == 'false'){
                    user.html(username + ': Offline');
                  }
                };

            if (socket.readyState == WebSocket.OPEN) {
              socket.onopen();
            }
        }
    }, 5000);
    $("#open_chat").click(function(){
        var $this = $("#chat_popup");
        if ($this.hasClass("closed")) {
            $(".navbar-collapse.collapse.in").collapse("hide");
            if ($width > 1050) {
                $("#chat_popup").animate({ "right": 0 }, "fast");
            }
            else {
                close_notifications();
                $("#chat_popup").animate({ "left": 0 }, "fast");
                $(".main").css("max-height", "calc("+$height+"px - 212px)");
                $(".main").css("overflow", "auto");
            }
            $("#friend_list").show();
            $("#close_friend_list").show();
            $("#chat_popup").bringToTop();
            $this.removeClass("closed");
            $this.addClass("opened");
        }
        else if ($this.hasClass("opened")) {
            closeChat();
        };
    });
    $("#close_friend_list").click(closeChat);
    $('.friends').click(function(){
        getMessages($(this).data("value"));
    });
    $("#close_chat_button").click(closeChat);
    $('#chat_message').on('keyup change', toggle_send_button);
    $("#chat_form").submit(function(event) {
        // Stop form from submitting normally
        event.preventDefault();
        var friendForm = $(this);
        // Send the data using post
        var posting = $.post( friendForm.attr('action'), friendForm.serialize() );
        // if success:
        posting.done(function(data) {
            // success actions, maybe change submit button to 'friend added' or whatever
            $('#chat_message').val("");
        });
        // if failure:
        posting.fail(function(data) {
            // 4xx or 5xx response, alert user about failure
        });
    });

    /* When you open the notification page */
    $("#notifications_counter").click(function(){
        if ($width < 1050){
            if ($("#chat_popup").hasClass("opened")){
                closeChat2();
            }
        }
        $this = $("#notifications_container");
        if ($this.hasClass("closed")) {
            open_notifications();
        }
        else {
            close_notifications();
        }
    });
    $("#notifications_container").on('click', '#clear_notifications_button', markMessagesAsViewed);
    $("#notifications_container").on("click", ".notifications", openChat);
    $("#notifications_container").on("click", "#close_notifications_container", close_notifications);
});

/* Deactivate the chat send button if input field is empty
   to avoid posting blank messages */
var toggle_send_button = function(){
    if ($('#chat_message').val().trim() == '') {
        $("#send_chat_message").prop('disabled', true);
    }
    else {
        $("#send_chat_message").prop('disabled', false);
    }
}

/* Ajax get call to fetch all messages between you and a friend
   and show them in the chat box */
var getMessages = function($friend){
    $.get("/chat/"+$friend+'/', function(data){
        showMessages(data, $friend)
    });
    $("#chat_form").attr("action", "/chat/" + $friend + "/");
    $(".panel-title").text("Chat - " + $friend );
    $(".panel-title").data("value", $friend);

    $("#friend_list").hide();
    $("#close_friend_list").hide();
    $("#slider-content").show();
    $("#slider-content").bringToTop();
}

/* Show chat messages when you open the chat */
var showMessages = function(data, friend) {
    $(".panel-body").empty();
    data.forEach(function(item) {
        $class = "sent'";
        if (item["creator__username"] == friend) {
            $class = "received'";
        }
        time = formatDatetime(item["created"]);
        $(".panel-body").append(
            "<div class='open_chat_messages'><div class='messages_wrapper "+$class+">"+
            "<h4>"+item["message"]+"</h4>"+"<p>"+time+"</p>"+
            "</div></div>"
        );
    });
    $(".panel-body").scrollTop($(".panel-body")[0].scrollHeight);

}

// Open socket to notify if user is online or offline.
var socket = new WebSocket('ws://' + window.location.host + '/users/');
socket.onopen = function open() {
  console.log('WebSockets connection created.');
};

socket.onmessage = function message(event) {
      var data = JSON.parse(event.data);
      // NOTE: We escape JavaScript to prevent XSS attacks.
      var username = encodeURI(data['username']);
      var user = $('.friends').filter(function () {
        return $(this).data("value") == username;
      });
      var is_logged_in = encodeURI(data['is_logged_in']);
      if (is_logged_in == 'true') {
        user.html(username + ': Online');
      }
      else if(is_logged_in == 'false'){
        user.html(username + ': Offline');
      }
    };

if (socket.readyState == WebSocket.OPEN) {
  socket.onopen();
}

// Open socket to notify if new messages between user and friends.
var chat_socket = new WebSocket('ws://' + window.location.host + '/inbox/');
chat_socket.onopen = function open() {
    console.log('ChatWebSocket connection created.');
    showNotifications();
};

chat_socket.onmessage = function message(event) {
    var data = JSON.parse(event.data);
    // NOTE: We escape JavaScript to prevent XSS attacks.
    var viewed = encodeURI(data['viewed']);
    if (viewed == "false") {
        var friend = encodeURI(data['friend']);
        // If chat with this friend is open
        if (friend == $('.panel-title').data("value")) {
            // show new messages in chat
            getMessages(friend);
        }
        else {
            // otherwise get a notification
            showNotifications();
        }
    } else if (viewed == "true") {
        deleteNotifications();
    }
};

if (chat_socket.readyState == WebSocket.OPEN) {
  chat_socket.onopen();
}

// Ajax GET to fetch new messages.
var showNotifications = function(){
    $.get("/notifications/", function(data){
        // Change notifications icon if new notifications
        if (data.length > 0) {
            $("#notifications_counter").css("background-image", "url(/static/images/notify_icon.png)");

        } else {
            $("#notifications_counter").css("background-image", "url(/static/images/notify_icon_viewed.png)");

        }
        data.forEach(createNotification);
    });
}

var createNotification = function(message) {
    var $creator = message["creator__username"];
    $("#notifications_wrapper").append('<h4 class="notifications" data-value="'+$creator+'">'+$creator+' has sent you a message.'+'</h4>');
}

var markMessagesAsViewed = function(){
    // Send message to socket to launch signal and mark as viewed into db
    $('#notifications_wrapper').empty();
    chat_socket.send("viewed");
}

var deleteNotifications = function(){
    $("#notifications_counter").css("background-image", "url(/static/images/notify_icon_viewed.png)");
}

var openChat = function(event) {
    close_notifications()
    if ($width > 1050) {
        $("#chat_popup").animate({ "right": 0 }, "fast");
    }
    else {
        $("#chat_popup").animate({ "left": 0 }, "fast");
        $(".main").css("max-height", "calc("+$height+"px - 212px)");
    }
    $("#chat_popup").removeClass("closed");
    $("#chat_popup").addClass("opened");
    $("#chat_popup").bringToTop();

    getMessages($(event.target).data("value"));
}

var close_notifications = function(){
    $this = $("#notifications_container")
    $this.addClass("closed");
    $this.removeClass("open");
    $this.hide();
    if ($width < 1050) {
        $(".main").css("max-height", "none");
        $(".main").css("overflow", "initial");
    }
    $(".notifications").hide();

}

var open_notifications = function(){
    $this = $("#notifications_container")
    $this.addClass("open");
    $this.removeClass("closed");
    $this.show();
    if ($width < 1050) {
        $(".main").css("max-height", "calc("+$height+"px - 212px)");
        $(".main").css("overflow", "auto");
    }
    $(".notifications").show();
}

var closeChat2 = function() {
    if ($width > 1050) {
        $("#chat_popup").animate({ "right": "-100vw" }, "fast")
    }
    else {
        $("#chat_popup").animate({ "left": "-100vw" }, "fast")
    }
    $(".main").css("max-height", "none");
    $(".panel-body").empty();
    $(".panel-title").data("value", "");

    $("#slider-content").hide();
    $("#chat_popup").removeClass("opened");
    $("#chat_popup").addClass("closed");
}
var closeChat = function() {
    if ($width > 1050) {
        $("#chat_popup").animate({ "right": "-100vw" }, "fast")
    }
    else {
        $("#chat_popup").animate({ "left": "-100vw" }, "fast", function(){
            $(".main").css("max-height", "none");
        });
    }
    $(".panel-body").empty();
    $(".panel-title").data("value", "");

    $("#slider-content").hide();
    $("#chat_popup").removeClass("opened");
    $("#chat_popup").addClass("closed");

}

/* Function to display most recent opened tab on top. Needs rework */
var highest = 1;
$.fn.bringToTop = function(){
    $(this).css('z-index', ++highest); // increase highest by 1 and set the style
};

var formatDatetime = function(data){
    var date = (new Date(data));
    var year = date.getFullYear();
    var month = date.getMonth();
    var day = date.getDate();
    var hour = date.getHours();
    var minutes = date.getMinutes();
    if ((new Date() - date) > 3600 * 24 * 1000){
        return date.toLocaleDateString()+" "+date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12: false})
    }
    else {
        return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12: false})
    }
};