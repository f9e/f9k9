f9k9  🐱-🐶 [![Build Status](https://travis-ci.org/f9e/f9k9.svg?branch=master)](https://travis-ci.org/f9e/f9k9) [![Maintainability](https://api.codeclimate.com/v1/badges/6eeaeb2980decd05d190/maintainability)](https://codeclimate.com/github/f9e/f9k9/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/6eeaeb2980decd05d190/test_coverage)](https://codeclimate.com/github/f9e/f9k9/test_coverage)
====

A simple REST API for image classification

This API was built to be maintainable, easy to use, 
versatile and extensible. It is not the fastest nor most optimized design.

In addition to accepting a single image, it can also accept an array of 
images or any number of URLs that may be images.

As such, it aims to tackle the core problem of the internet today, having too many 
feline pictures or none.


## Installation 

Clone the source code:
```
git clone https://github.com/f9e/f9k9.git;
cd f9k9;
```

Configure a virtual environment in the project directory:
```
virtualenv -p python3 venv;
source venv/bin/activate;
pip install -r requirements/dev.txt
```

Using the app from the command line

```json
flask app   # run a local daemon on port 5000
flask shell # start shell with access to app functions
```
Run tests

```json
pytest
```




## Configuration

There are sample configurations in the `config.py` .  

* `APP_MODEL` location of Keras model hdf5 
* `APP_TRUE` is a human readable true string  
* `APP_FALSE` is the human readable false string 
* `APP_THRESH` is the threshold of truth 
* `APP_PROXY` enables downloading of images from external urls 

If not provided, values default to the current example (i.e. 'Dog', 'Cat', 0.5)

Several configurations are provided in `config.py`, they can be activated prior to starting the app
by setting the `APP_SETTINGS` environment variable to the desired setting class. 
 

```
export APP_SETTINGS="config.DevConfig"
```


## Deployment 

### with docker

Build the docker image

```
docker build -t f9k9:latest .
```

Run the docker image on port 5000

```
docker run -d -p 5000:5000 f9k9
```

## Usage

### Example Python Usage

Below are examples written with the `requests` library of python.

#### put a single image,

```python
import requests, json

url = "http://localhost:5000/api/v1.0.0/identify/"
image = open('./static/cat_1.jpg', 'r+b')
r = requests.put(url=url,data=image)
'Status: {}'.format(r.status_code)
r.content

```

returns

```python
Status: 200
b'["Dog"]'
```

#### post a single image verbosely,

```python
import requests, json

url = "http://localhost:5000/api/v1.0.0/identify/"
filename = './static/cat_3.jpeg'
image = [('images', (filename, open(filename, 'r+b')))]
r = requests.post(url=url,params={'verbose':'true'},files=image)
'Status: {}'.format(r.status_code)
json_data = r.content.decode('utf-8')
print(json_data)
```

returns

```json
[
  {
    "is_error": false,
    "value": 0.43634799122810364,
    "filename": "./static/cat_3.jpeg",
    "hash_func": "openssl_md5",
    "result": "Cat",
    "hash": "d41d8cd98f00b204e9800998ecf8427e"
  }
]

```

#### Post a directory

```python
from glob import glob
import requests

endpoint_url = "http://localhost:5000/api/v1.0.0/identify/"

filenames = glob('./static/*')
files = []
for filename in filenames:
    files += [('images', (filename, open(filename, 'r+b')))]

r = requests.post(url=endpoint_url, files=files, )
print("{}".format(r.status_code))

for f in files:
    f[1][1].close()
```

### Example Curl Usage

#### using form-urlencoded (-d)

Using form or url encoded data, the endpoint behaves as such 

#### PUT a glob of files individually at the endpoint

> Note: Curl append the file to the endpoint name, so the actual 
endpoint location for this call is `/api/v1.0.0/identify/<filename>`

```
curl -T "./static/cat_{3,5,6}.jpeg" http://localhost:5000/api/v1.0.0/identify/
```

returns

```
["Cat"]
["Cat"]
["Cat"]
```



PUT from stdin in verbose mode (without filename):

```
cat static/cat_3.jpeg | curl -T - http://localhost:5000/api/v1.0.0/identify/?verbose=true
```

returns 

```
[
  {
    "filename": "",
    "hash": "d41d8cd98f00b204e9800998ecf8427e",
    "hash_func": "openssl_md5",
    "result": "Cat",
    "value": 0.43634799122810364
  }
]
```

#### Proxy usage

If the client has no local storage and the `ALLOW_PROXY` setting is `True`, the app will
 download and analyze image urls passed individually into the `url` parameter or as an 
 array into the `urls` parameter.   
 
 No multi-threading is done and it downloads images one at a time.

```
curl -d 'verbose=true' \
     -d 'url=https://ipfs.io/ipfs/QImAnInvalidHashhhhhhhh/cat.jpg'  \
     -d 'url=https://ipfs.io/ipfs/QmW2WQi7j6c7UgJTarActp7tDNikE4B2qXtFCfLPdsgaTQ/cat.jpg' \
     -d 'urls=https://upload.wikimedia.org/wikipedia/commons/b/b9/CyprusShorthair.jpg' \
     -d 'urls=https://upload.wikimedia.org/wikipedia/commons/4/4d/Cat_November_2010-1a.jpg' \
     -d 'urls=https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/June_odd-eyed-cat.jpg/1260px-June_odd-eyed-cat.jpg' \
     http://localhost:5000/api/v1.0.0/identify/
```
Which returns:

```json
[
  {
    "hash": "d41d8cd98f00b204e9800998ecf8427e",
    "hash_func": "openssl_md5",
    "filename": "https://ipfs.io/ipfs/QImAnInvalidHashhhhhhhh/cat.jpg",
    "value": null,
    "result": "Error - Downloading : 400",
    "is_error": true
  },
  {
    "hash": "d41d8cd98f00b204e9800998ecf8427e",
    "hash_func": "openssl_md5",
    "filename": "https://ipfs.io/ipfs/QmW2WQi7j6c7UgJTarActp7tDNikE4B2qXtFCfLPdsgaTQ/cat.jpg",
    "value": 0.9544882774353027,
    "result": "Dog",
    "is_error": false
  },
  {
    "hash": "d41d8cd98f00b204e9800998ecf8427e",
    "hash_func": "openssl_md5",
    "filename": "https://upload.wikimedia.org/wikipedia/commons/b/b9/CyprusShorthair.jpg",
    "value": 0.09424301236867905,
    "result": "Cat",
    "is_error": false
  },
  {
    "hash": "d41d8cd98f00b204e9800998ecf8427e",
    "hash_func": "openssl_md5",
    "filename": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Cat_November_2010-1a.jpg",
    "value": 0.3212617039680481,
    "result": "Cat",
    "is_error": false
  },
  {
    "hash": "d41d8cd98f00b204e9800998ecf8427e",
    "hash_func": "openssl_md5",
    "filename": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/June_odd-eyed-cat.jpg/1260px-June_odd-eyed-cat.jpg",
    "value": 0.9087091684341431,
    "result": "Dog",
    "is_error": false
  }
]

```



### using multipart form-data (-F)

Multipart form-data is useful for uploading a batch of images. The POST method 
is used in this case 

#### POST an array of image files

A client may post an array of files to the `images` parameter as a  multipart formpost request:
```sh
curl -F 'images=@static/cat_1.jpg' \
       -F 'images=@static/cat_2.jpeg' \
       -F 'images=@static/cat_3.jpeg' \
       -F 'images=@static/cat_4.jpeg' \
       -F 'images=@static/cat_5.jpeg' \
       -F 'images=@static/cat_6.jpeg' \
       -F 'images=@static/cat_7.jpeg' \
      "http://localhost:5000/api/v1.0.0/identify/"
```

returns a single json array

```json
["Dog","Dog","Cat","Dog","Cat","Cat","Cat"]
```

#### Getting verbose results

With the verbose flag, information regarding the file as well as the numeric value are returned. 

This mode may be useful for processing batch responses.

```
curl -F 'verbose=true' \
     -F 'images=@static/cat_6.jpeg' \
     -F 'images=@static/cat_7.jpeg' \
      http://localhost:5000/api/v1.0.0/identify/
```

returns:

```json
[
  {
    "filename": "cat_6.jpeg",
    "hash": "d41d8cd98f00b204e9800998ecf8427e",
    "hash_func": "openssl_md5",
    "result": "Cat",
    "value": 0.07044649124145508
  },
  {
    "filename": "cat_7.jpeg",
    "hash": "d41d8cd98f00b204e9800998ecf8427e",
    "hash_func": "openssl_md5",
    "result": "Cat",
    "value": 0.04014977067708969
  }
]

```

## Todo

* Crop images centrally for evaluation
* `tf.image.per_image_standardization` to make the model insensitive to dynamic range
* Zappa deployment with s3 model storage
* Caching 
* Generalize settings to handle a list of categories.
* Vector input (svg, pdf)
* Video input (mp4, avi)

## Proposal

* Remove all batching functionality
* Convert to OO design
* Split into two services: 1) a robust array preparation service 
and 2) a highly optimized processing service
