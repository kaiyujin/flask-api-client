# Usage
## Run docker
```
docker image build -t flask-api-client .
docker run -p 5080:80 -v ${PWD}/app:/app -d --rm flask-api-client
```

## Open browser
```
open http://localhost:5080
```


# Log
```
tail -f app/flask.log
```
