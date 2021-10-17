## Privfiles - Encrypted file storage using Fernet with zero Javascript

Source code for the onion service: `l3n6v6dm63frml22tlmzacnasvp7co7wylu4hhcs34ukxe7q56yb4tyd.onion`

## Previews
![home page](https://i.imgur.com/LouGjvI.png)
![api page](https://i.imgur.com/SUHwwWU.png)

## Setup
### Git clone
`git clone https://github.com/WardPearce/privfiles`
### Install Mongodb
[community edition](https://www.mongodb.com/try/download/community)
### Install python requirements
`pip3 install -r requirements.txt`
### Nginx
- [Restricting Access to Admin Page with Nginx](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/)
- [Uvicorn deployment](https://www.uvicorn.org/deployment/)
```
server {
	listen 127.0.0.1:8080;
	client_max_body_size 4G;

	chunked_transfer_encoding on;

	location ~ /admin {
		auth_basic "privfiles admin";
		auth_basic_user_file /etc/apache2/.htpasswd;

		proxy_redirect off;
		proxy_buffering off;
		proxy_pass http://uvicorn;
	}

	location / {
		proxy_redirect off;
		proxy_buffering off;
		proxy_pass http://uvicorn;
	}
}

upstream uvicorn {
	server unix:/tmp/uvicorn.sock;
}
```
### Adding fonts for recaptcha
Add .ttf fonts to `privfiles/fonts` for recaptcha generation
### Configure
`run.py`
```
import uvicorn

from privfiles import PrivFiles
from privfiles.settings import B2Settings


app = PrivFiles(
    backblaze_settings=B2Settings(
        key_id="...",
        application_key="...",
        bucket_id="..."
    )
)


if __name__ == "__main__":
    uvicorn.run(
        app,
        uds="/tmp/uvicorn.sock",
        log_level="error"
    )
```
### Running
Use something like [pm2](https://pm2.keymetrics.io) to run `run.py` & `api_task.py` in the background.


## Thanks to
- [cryptography](https://pypi.org/project/cryptography/) by The Python Cryptographic Authority and individual contributors
- [motor](https://pypi.org/project/motor/) by A. Jesse Jiryu Davis
- [pymongo](https://pypi.org/project/pymongo/) by Bernie Hackett
- [starlette](https://pypi.org/project/starlette/) by Tom Christie
- [anyio](https://pypi.org/project/anyio/) by Alex Grönholm
- [idna](https://pypi.org/project/idna/) by Kim Davies
- [sniffio](https://pypi.org/project/sniffio/) by Nathaniel J. Smith
- [Jinja](https://pypi.org/project/Jinja/) by Armin Ronacher
- [backblaze](https://pypi.org/project/backblaze/) by WardPearce
- [httpx](https://pypi.org/project/httpx/) by Tom Christie
- [certifi](https://pypi.org/project/certifi/) by Kenneth Reitz
- [charset-normalizer](https://pypi.org/project/charset-normalizer/) by Ahmed TAHRI @Ousret
- [sniffio](https://pypi.org/project/sniffio/) by Nathaniel J. Smith
- [httpcore](https://pypi.org/project/httpcore/) by Tom Christie
- [h](https://pypi.org/project/h/) by Seth Michael Larson
- [anyio](https://pypi.org/project/anyio/) by Alex Grönholm
- [idna](https://pypi.org/project/idna/) by Kim Davies
- [aiofile](https://pypi.org/project/aiofile/) by Dmitry Orlov <me@mosquito.su>
- [caio](https://pypi.org/project/caio/) by Dmitry Orlov <me@mosquito.su>
- [aiofiles](https://pypi.org/project/aiofiles/) by Tin Tvrtkovic
- [asynctest](https://pypi.org/project/asynctest/) by Martin Richard
- [sphinxcontrib-trio](https://pypi.org/project/sphinxcontrib-trio/) by Nathaniel J. Smith
- [Sphinx](https://pypi.org/project/Sphinx/) by Georg Brandl
- [sphinxcontrib-applehelp](https://pypi.org/project/sphinxcontrib-applehelp/) by Georg Brandl
- [sphinxcontrib-devhelp](https://pypi.org/project/sphinxcontrib-devhelp/) by Georg Brandl
- [sphinxcontrib-jsmath](https://pypi.org/project/sphinxcontrib-jsmath/) by Georg Brandl
- [sphinxcontrib-htmlhelp](https://pypi.org/project/sphinxcontrib-htmlhelp/) by Georg Brandl
- [sphinxcontrib-serializinghtml](https://pypi.org/project/sphinxcontrib-serializinghtml/) by Georg Brandl
- [sphinxcontrib-qthelp](https://pypi.org/project/sphinxcontrib-qthelp/) by Georg Brandl
- [Jinja](https://pypi.org/project/Jinja/) by Armin Ronacher
- [Pygments](https://pypi.org/project/Pygments/) by Georg Brandl
- [docutils](https://pypi.org/project/docutils/) by David Goodger
- [snowballstemmer](https://pypi.org/project/snowballstemmer/) by Snowball Developers
- [Babel](https://pypi.org/project/Babel/) by Armin Ronacher
- [pytz](https://pypi.org/project/pytz/) by Stuart Bishop
- [alabaster](https://pypi.org/project/alabaster/) by Jeff Forcier
- [imagesize](https://pypi.org/project/imagesize/) by Yoshiki Shibukawa
- [requests](https://pypi.org/project/requests/) by Kenneth Reitz
- [setuptools](https://pypi.org/project/setuptools/) by Python Packaging Authority
- [packaging](https://pypi.org/project/packaging/) by Donald Stufft and individual contributors
- [pyparsing](https://pypi.org/project/pyparsing/) by Paul McGuire
- [sphinx-material](https://pypi.org/project/sphinx-material/) by Kevin Sheppard
- [BeautifulSoup](https://pypi.org/project/BeautifulSoup/) by Leonard Richardson
- [css-html-js-minify](https://pypi.org/project/css-html-js-minify/) by Juan Carlos
- [lxml](https://pypi.org/project/lxml/) by lxml dev team
- [captcha](https://pypi.org/project/captcha/) by Hsiaoming Yang
- [Pillow](https://pypi.org/project/Pillow/) by Alex Clark (PIL Fork Author)
- [uvicorn](https://pypi.org/project/uvicorn/) by Tom Christie
- [asgiref](https://pypi.org/project/asgiref/) by Django Software Foundation
- [click](https://pypi.org/project/click/) by Armin Ronacher
- [h](https://pypi.org/project/h/) by Seth Michael Larson
- [itsdangerous](https://pypi.org/project/itsdangerous/) by Armin Ronacher
- [python-dotenv](https://pypi.org/project/python-dotenv/) by Saurabh Kumar
- [bcrypt](https://pypi.org/project/bcrypt/) by The Python Cryptographic Authority developers
- [python-multipart](https://pypi.org/project/python-multipart/) by Andrew Dunham