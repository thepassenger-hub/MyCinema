# MyCinema

Personal project made with Django. Very simple Social networking with live chat functionality.
Send a movie suggestion to your friends. A crawler will fetch the data from google to provide better information about the movie.
Thanks to django channels package you can see who is online with live updates about your friends statuses and interact with them by using the live chat.

#### Home Page

![screenshot of home page](/movieapp_backend/static/images/home.png?raw=true "Home Page")

#### New Post Page

![screenshot of profile page](/movieapp_backend/static/images/newpost.png?raw=true "Profile Page")

#### Lice Chat

![screenshot of admin page](/movieapp_backend/static/images/livechat.png?raw=true "Admin Page")

### Features

* Basic Authentication.
* Create Posts to send to a specific user or to all your friends.
* Customize Profile and change password.
* Search bar to sort posts by title, user or rating.
* If movie url or avatar are not provided by the creator, a custom web crawerl will fetch the informations from <http://imdb.com> website.
* Live chat with every friend with fast response times.
* Live notifications about friend status and if you receive a message.

### Development

This webapp was developed following the TDD principles therefore you can find unit test and and functional test that use selenium.
To provide live action I used the [Django channels package](https://github.com/django/channels).
For frontend simple css and JQuery were used.

#### You can find a live demo at <http://mycinema.ezgameezlyf.top>

## License

This project is licensed under the MIT License.