[![Build Status](https://travis-ci.com/Dima2504/flask-simple-chats.svg?branch=master)](https://travis-ci.com/Dima2504/flask-simple-chats)
[![Coverage Status](https://coveralls.io/repos/github/Dima2504/flask-simple-chats/badge.svg?branch=master)](https://coveralls.io/github/Dima2504/flask-simple-chats?branch=master)
# Flask simple chats
Flask simple chats is an educational project which also fully represents **The Final Project** for [EPAM University Program](https://training.epam.ua/). It has 
been developed considering all the declared requirements and conditions. Now, the first release has come up and the product is ready for checking.

Flask simple chats is a simple web applicacation. It easily allows users to adjust the communication. The current stable version provides with an authentication system,
chats system and light api. The application realizes a pure web interface where users can register, login, look for each other, create chats, send messages and join
created chats after a certain period. The current api gives an access to all the implemented application features.

# Instalation
## Using docker-compose

The simples way to install and execute the application is to use [Docker](https://www.docker.com/) and [Docker-compose](https://docs.docker.com/compose/):
#### Clone the repository:
```bash
$ git clone https://github.com/Dima2504/flask-simple-chats.git
```
Note: if you are using Git on Windows, be carefull with [core.autocrlf](https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration#_core_autocrlf) setting: if it is true, git converts LF endings into CRLF when you check out the code. By this way, docker container with the application is expected to throw an error!  

#### Move to the appeared folder:
```bash
$ cd flask-simple-chats
```
#### Create [.env](https://docs.docker.com/compose/environment-variables/#the-env_file-configuration-option) file and specify there some necessary environment variables:
```dosini
# .env, private
# The complete list of possible variables is in app/config.py
SECRET_KEY=very-secret
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=example@gmail.com
MAIL_PASSWORD=example
```
#### Up the docker-compose:
```bash
$ docker-compose up
```
Open [http://localhost](http://localhost) and use the application. Docker-compose is configured to expose 80 port by default. If this port is busy on your local machine, do not hesitate to repleca the default value in file docker-compose.yml with more appropriate one. 

## From sources

If you do not opt to use docker-compose, please, follow the further steps:
#### Clone the repository and move to the root of the project:
```bash
$ git clone https://github.com/Dima2504/flask-simple-chats.git
$ cd flask-simple-chats
```
#### Setup virtual environment and install dependencies:  

```bash
# create environment
$ python -m venv venv

# activate environment
$ . ./venv/bin/activate

# install dependencies
$ pip install -r requirements.txt
```
Note: make sure, that you are using [Python 3.8.0](https://www.python.org/downloads/release/python-380/) or higher and have installed python3-venv package, if you have Debian/Ubuntu system.  

#### Create database on your postgres server:
```
postgres=# CREATE DATABASE "flask-simple-chats" ENCODING "UTF8";
```
Note: Application's config expects you to be using database, named 'flask-simple-chats', being a default user 'postgres' with a password equal to 'postgres'. If you have another password or work by different user, specify the valid credential in DB_NAME, DB_USERNAME and DB_PASSWORD environment variables.

#### Apply migrations:
```bash
$ flask db upgrade
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 1898f0bcaaf5, Add simple user model
INFO  [alembic.runtime.migration] Running upgrade 1898f0bcaaf5 -> 037027ecc99a, Add message model
INFO  [alembic.runtime.migration] Running upgrade 037027ecc99a -> 53a9bfcfee47, Add chats table
INFO  [alembic.runtime.migration] Running upgrade 53a9bfcfee47 -> ac141622b2da, add chat_id into chats table and into messages table like a foreign key
```

#### Run the server:
```bash
$ gunicorn
[2021-05-19 21:51:09 +0000] [3661] [INFO] Starting gunicorn 20.1.0
[2021-05-19 21:51:09 +0000] [3661] [INFO] Listening at: http://0.0.0.0:8000 (3661)
[2021-05-19 21:51:09 +0000] [3661] [INFO] Using worker: eventlet
[2021-05-19 21:51:09 +0000] [3663] [INFO] Booting worker with pid: 3663
```
Gunicorn config from the root of the application includes a few necessary settings, so you do not need to pass them directly.
Now, browse the following link: [http://localhost:8000](http://localhost:8000).  

# Configuration

Both using Docker and installing the application on you own, you may want to declare some 'outstanding' settings, or even just do not want to specify configuration in environment variables for some reasons. At this rate, flask [instance folder](https://flask.palletsprojects.com/en/1.1.x/config/#instance-folders) is the best choice. Create a file named "production_config.py" and freely set there necessary variables. Then build and up the docker-compose, or just start the server on you machine. 
```bash
.
├── instance
│   └── production_config.py
```

```python
# production_config.py, is not checked by version control
import secrets

SECRET_KEY = secrets.token_urlsafe(64)
LOGGING = False
```
Now, when starting the application, the settings above will be applied.

# API Quickstart
As it has been pointed out, flask simple chats realizes a light api interface. It is expected to expand, but even the current functionality has the right to use. So, here is a quick overview of the implemented functions.  
Note: all the api urls have **"/api"** prefix, so do not forget about that.


## Authorization details
Almost all the API requests require the use of [Basic](https://learning.postman.com/docs/sending-requests/authorization/#basic-auth) or [Bearer](https://learning.postman.com/docs/sending-requests/authorization/#bearer-token) http authorization, but, firts, you have to register:
```console
$ curl -X POST -H 'Content-Type: application/json' -d '{"email": "docs@gmail.com", "username": "docs_user", "name": "docs", "password": "12345678"}' localhost/api/register | json_pp
{
   "email" : "docs@gmail.com",
   "message" : "Successfully registered!"
}
```
Note: I am using [json_pp](https://docs.oracle.com/cd/E86824_01/html/E54763/json-pp-1.html) to format the output. It is not necessary and serves only to make the results look clearer.  

So, now there are two possible options: you can make requests with Basic authorization specifying your email and password each time, or get auth token and specify it. Let us get auth token:
```console
$ curl -X GET -u docs@gmail.com:12345678 localhost/api/token | json_pp
{
   "expires_in" : 3600,
   "token" : "eyJhbGciOiJIUzUxMiIsImlhdCI6MTYyMTUxMzc2NywiZXhwIjoxNjIxNTE3MzY3fQ.eyJ1c2VyX2lkIjoxNX0.LgbGHnVE42gZHghXnD6aE-kIPW9MIwulwsXZnauLX9y15rEd2HyA2vqUVqyD9KYvXGqgSPbGSrxB-kGswIDm_A"
}
```
Note: curl allows us to use Basic authorization by putting `-u, <user:password>` parameter, so there is no need to encode credentials and assign http header manually.

After requesting we receive token and the time in seconds before the token expired. Now we can use it for the next requests:
```console
$ curl -H 'Authorization: Bearer eyJhbGciOiJIUzUxMiIsImlhdCI6MTYyMTUxMzc2NywiZXhwIjoxNjIxNTE3MzY3fQ.eyJ1c2VyX2lkIjoxNX0.LgbGHnVE42gZHghXnD6aE-kIPW9MIwulwsXZnauLX9y15rEd2HyA2vqUVqyD9KYvXGqgSPbGSrxB-kGswIDm_A' localhost/api/users | json_pp
{
   "data" : [
      {
         "date_joined" : "Thu, 20 May 2021 11:52:17 -0000",
         "name" : "docs",
         "user_id" : 15,
         "username" : "docs_user"
      },
      {
         "date_joined" : "Thu, 20 May 2021 12:08:02 -0000",
         "name" : "Dmytro Afanasev",
         "user_id" : 16,
         "username" : "dima"
      },
      {
         "date_joined" : "Thu, 20 May 2021 13:11:53 -0000",
         "name" : "Ann",
         "user_id" : 17,
         "username" : "ann"
      }
   ],
   "user_id" : 15
}
```
We can see, that two more users had been using the system, when we signed up. Also, we received the current user's id.

Note: having received authorization token, you had better use exact it, but in order to make the commands shorter, I will use Basic authorization for the next examples.

## Resources
Because chat system is assumed to give an access only to owned chats and messages, each user has to be authenticated before receiving any data. Anyway, users cannot see other users' chats and messages.

Also, in order to make the interation easier, each response contains the information about the user who has made it and some other addition data.

#### Users
As I have demonstrated above, you can receive the list of users by requesting `/api/users`:
```console
$ curl -u docs@gmail.com:12345678 localhost/api/users | json_pp
...
```
To receive the information about only one certain user, request the following url with declared user's id:
```console
$ curl -u docs@gmail.com:12345678 localhost/api/users/16 | json_pp
{
   "data" : {
      "date_joined" : "Thu, 20 May 2021 12:08:02 -0000",
      "name" : "Dmytro Afanasev",
      "user_id" : 16,
      "username" : "dima"
   },
   "user_id" : 15
}
```

#### Chats
You can easily see the list of our user's chats, but sure, he has just been created, he has no chats. Let's create one. We need to make a POST request and specify 'companion_id' field in json data:
```console
$ curl -X POST -u docs@gmail.com:12345678 -H 'Content-Type: application/json' -d '{"companion_id": 16}' localhost/api/chats | json_pp
{
   "chat_id" : 11,
   "companion_id" : 16,
   "message" : "Chat was successfully created",
   "user_id" : 15
}
```
Let's create one more chat with the rest user:
```console
$ curl -X POST -u docs@gmail.com:12345678 -H 'Content-Type: application/json' -d '{"companion_id": 17}' localhost/api/chats | json_pp
...
```
Now, to see the list of chats, make the appropriate GET request:
```console
$ curl -u docs@gmail.com:12345678 localhost/api/chats | json_pp
{
   "data" : [
      {
         "chat_id" : 12,
         "user1_id" : 15,
         "user2_id" : 16
      },
      {
         "chat_id" : 13,
         "user1_id" : 15,
         "user2_id" : 17
      }
   ],
   "user_id" : 15
}
```
You can ask only for one certain chat. Put its id to url like below:
```console
$ curl -u docs@gmail.com:12345678 localhost/api/chats/13 | json_pp
{
   "data" : {
      "chat_id" : 13,
      "user1_id" : 15,
      "user2_id" : 17
   },
   "user_id" : 15
}
```
That is it!  
If you want to delete a certain chat, instead of GET, use DELETE request:
```console
$ curl -X DELETE -u docs@gmail.com:12345678 localhost/api/chats/12 | json_pp
{
   "chat_id" : 12,
   "message" : "Chat was successfully deleted",
   "user_id" : 15
}
```
Note: be careful, if you delete a chat, all the messages in will be deleted as well!  
#### Messages
First off, let's send a couple of messages to our just created chat. To do it, we need to make a POST requets and declare 'texts' parameter to json, which contains the list of messages like:
```console
$ curl -X POST -u docs@gmail.com:12345678 -H 'Content-Type: application/json' -d '{"texts": ["Hello", "How are you?"]}' localhost/api/chats/13/messages | json_pp
{
   "chat_id" : 13,
   "message" : "Your messages were successfully sent",
   "user_id" : 15
}
```
Take into consideration, we made a request into url with specifying chat id, and being registered as 'docs' user. So, the system exactly know, where to relate the messages.  

Note: we had created a chat before sending messages, but it is not necessary. It can be created automatically by a system.  
Let's send one more message:
```console
$ curl -X POST -u docs@gmail.com:12345678 -H 'Content-Type: application/json' -d '{"texts": ["The third one?"]}' localhost/api/chats/13/messages | json_pp
{
   "chat_id" : 13,
   "message" : "Your message was successfully sent",
   "user_id" : 15
}
```
If now we visit a website and glance at our user's chats, we will see:

![Chat_example](./documentation/readme_static/Docs_chat_example.png)

To see the same list of message from a certain chat, but using API instead of web interface, request like that:
```console
$ curl -u docs@gmail.com:12345678 localhost/api/chats/13/messages | json_pp 
{
   "chat_id" : 13,
   "data" : [
      {
         "datetime_writing" : "Thu, 20 May 2021 13:47:20 -0000",
         "message_id" : 116,
         "receiver_id" : 17,
         "sender_id" : 15,
         "text" : "Hello"
      },
      {
         "datetime_writing" : "Thu, 20 May 2021 13:47:20 -0000",
         "message_id" : 117,
         "receiver_id" : 17,
         "sender_id" : 15,
         "text" : "How are you?"
      },
      {
         "datetime_writing" : "Thu, 20 May 2021 13:53:54 -0000",
         "message_id" : 118,
         "receiver_id" : 17,
         "sender_id" : 15,
         "text" : "The third one?"
      }
   ],
   "user_id" : 15
}
```
And, as you can guess, we can request the information about one certain message:
```console
$ curl -u docs@gmail.com:12345678 localhost/api/chats/13/messages/113 | json_pp 
{
   "chat_id" : 13,
   "data" : {
      "datetime_writing" : "Thu, 20 May 2021 13:47:20 -0000",
      "message_id" : 116,
      "receiver_id" : 17,
      "sender_id" : 15,
      "text" : "Hello"
   },
   "user_id" : 15
}
```
Like with chats, we can delete a certain message by id:
```console
$ curl -X DELETE -u docs@gmail.com:12345678 localhost/api/chats/13/messages/116 | json_pp
{
   "chat_id" : 13,
   "message" : "Message 116 was successfully deleted",
   "message_id" : 116,
   "user_id" : 15
}
```
And, at last, we are able to change some message's text:
```console
$ curl -X PUT -u docs@gmail.com:12345678 -H 'Content-Type: application/json' -d '{"text": "I was changed"}' localhost/api/chats/13/messages/117 | json_pp
{
   "chat_id" : 13,
   "message" : "Message 117 was successfully updated",
   "message_id" : 117,
   "text" : "I was changed",
   "user_id" : 15
}
```
Now, our chat looks like this:

![Chat_example_2](./documentation/readme_static/Docs_chat_example_2.png)

The first message was deleted, the second was altered, as we can see above.

## Query components for filtering

Sometimes, you can come across requirements where you need to have users or messages sorted, filtered or limited based on some certain parameters. Here you can use url query parameters to limit the output as you need.

Note: it works only with users list and messages list for now.  

There are several possible variants of search, and, of course, they can be easily combined to attain the necessary result:
1. You can look for the messages by putting attributes' names directly and their theoretical values, like:
```console
$ curl -u docs@gmail.com:12345678 "localhost/api/users?username=docs_user&name=docs" | json_pp
{
   "data" : [
      {
         "date_joined" : "Thu, 20 May 2021 11:52:17 -0000",
         "name" : "docs",
         "user_id" : 15,
         "username" : "docs_user"
      }
   ],
   "user_id" : 15
}
```
2. To search without an exact match use `-like` ending after attribute names. It works only if column has type string:
```console
$ curl -u docs@gmail.com:12345678 "localhost/api/users?username-like=an" | json_pp
{
   "data" : [
      {
         "date_joined" : "Thu, 20 May 2021 13:11:53 -0000",
         "name" : "Ann",
         "user_id" : 17,
         "username" : "ann"
      }
   ],
   "user_id" : 15
}
```
3. To sort an output use `ordered-by` and `ordered-by-desc` parameter and specify db column name to order by:
```console
$ curl -u docs@gmail.com:12345678 "localhost/api/chats/13/messages?ordered-by-desc=datetime_writing" | json_pp
{
   "chat_id" : 13,
   "data" : [
      {
         "datetime_writing" : "Thu, 20 May 2021 14:18:38 -0000",
         "message_id" : 118,
         "receiver_id" : 17,
         "sender_id" : 15,
         "text" : "The third one?"
      },
      {
         "datetime_writing" : "Thu, 20 May 2021 14:18:28 -0000",
         "message_id" : 117,
         "receiver_id" : 17,
         "sender_id" : 15,
         "text" : "I was changed"
      }
   ],
   "user_id" : 15
}
```
4. To restrict the number of results use `limit` and `offset` statements together or separately:
```console
$ curl -u docs@gmail.com:12345678 "localhost/api/chats/13/messages?ordered-by-desc=datetime_writing&limit=1" | json_pp
{
   "chat_id" : 13,
   "data" : [
      {
         "datetime_writing" : "Thu, 20 May 2021 14:18:38 -0000",
         "message_id" : 118,
         "receiver_id" : 17,
         "sender_id" : 15,
         "text" : "The third one?"
      }
   ],
   "user_id" : 15
}
```
Note: if given params are not valid, they will be ignored.

## All the resources

All the implemented resources are below:

#### Authorization:
| Method | Url              | Description                                               |
|--------|------------------|-----------------------------------------------------------|
| POST   | /register        | Register user by given email, username, name and password |
| GET    | /token           | Get authorization token for the current user              |
| POST   | /update          | Update the current user's username and/or name            |
| POST   | /forgot-password | Send password reset token to the given email              |
| POST   | /reset-password  | Reset password by given reset password token              |

#### Users:
| Method | Url              | Description        |
|--------|------------------|--------------------|
| GET    | /users/          | List of users      |
| GET    | /users/{user_id} | User details by id |

#### Chats:
| Method | Url              | Description         |
|--------|------------------|---------------------|
| GET    | /chats/          | List of chats       |
| POST   | /chats/          | Create a new chat   |
| GET    | /chats/{chat_id} | Chat details by id  |
| DELETE | /chats/{chat_id} | Delete a chat by id |

#### Messages:
| Method | Url                                    | Description                                  |
|--------|----------------------------------------|----------------------------------------------|
| GET    | /chats/{chat_id}/messages              | List of messages from a chat by id           |
| POST   | /chats/{chat_id}/messages              | Send message(s) to a chat by id              |
| GET    | /chats/{chat_id}/messages/{message_id} | Message details by id from a chat by id      |
| DELETE | /chats/{chat_id}/messages/{message_id} | Delete a message by id from a chat by id     |
| PUT    | /chats/{chat_id}/messages/{message_id} | Change messsage text by id from a chat by id |

# Testing

The application is fully covered by tests. To be convinced, having activated the virtual environment, you can start testing.

## Unittest
Run the unitests using the command
```bash
# python -m unittest discover
$ flask tests
...

----------------------------------------------------------------------
Ran 80 tests in 21.253s

OK
```
Or if you have alredy built and upped the docker container, you can execute the tests the following command:
```bash
$ docker exec -it flask-simple-chats_web_1 flask tests
...
```
## Covarege
To run tests using [coverals](https://coveralls.io/), make sure that requirements are installed and execute:
```bash
$ coverage run --source=app -m unittest discover -s tests
...

----------------------------------------------------------------------
Ran 80 tests in 36.408s

OK
```
See the report:
```bash
$ coverage report
```
