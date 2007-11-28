addLoadEvent(function() {
    var container = $('premailmessagecontainer');
    connect('user', 'onchange', function() {
        container.innerHTML = '';
        var d = loadJSONDoc(url_for('mail.pre_mail_message_json', {username: $('user').value}));
        d.addCallback(function(data) {
            if (data.username != null && data.message != null) {
                container.innerHTML =
                    '<div class="premailmessage"><h3>' + data.username + 
                    ' says:</h3>' + data.message + '</div>';
            }
        });
    });
});
