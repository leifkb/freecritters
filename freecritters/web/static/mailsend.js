addLoadEvent(function() {
    var container = $('premailmessagecontainer');
    connect('user', 'onchange', function() {
        container.innerHTML = '';
        var d = loadJSONDoc('http://192.168.1.101:8080/json/pre_mail_message',
                            {username: $('user').value});
        d.addCallback(function(data) {
            if (data.username != null && data.message != null) {
                container.innerHTML =
                    '<div class="premailmessage"><h3>' + data.username + 
                    ' says:</h3>' + data.message + '</div>';
            }
        });
    });
});
