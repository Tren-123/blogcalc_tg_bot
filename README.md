# Welocme to blogcalc_tg_bot
This bot created for interract with my [website](https://github.com/Tren-123/blogcalc) for blog creating
## Bot features
Available commands:
- /start, /help - show help note
- /create_post - start process for creating new post. Ask to input title, content for new post, check them after input and confirm sending
## Some technical details about bot 
- Bot built on sync python 3 - for this time it can work only with one user in parallel
- Bot ask credentials of user for website and store it in db (weak protection of sensitive data, but I haven't figured out with OAuth yet). Bot use basic auth to check credentials with website 
