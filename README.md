f9k9  🐱-🐶 [![Build Status](https://travis-ci.org/f9e/f9k9.svg?branch=master)](https://travis-ci.org/f9e/f9k9) [![Maintainability](https://api.codeclimate.com/v1/badges/6eeaeb2980decd05d190/maintainability)](https://codeclimate.com/github/f9e/f9k9/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/6eeaeb2980decd05d190/test_coverage)](https://codeclimate.com/github/f9e/f9k9/test_coverage)
====

A simple REST API for image classification

This API was built to be maintainable, easy to use, 
versatile and extensible. It is not the fastest nor most optimized design.

In addition to accepting a single image, it can also accept an array of 
images or any number of URLs that may be images.

As such, it aims to tackle the core problem of the internet today, having too many 
cat pictures or none.


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

Using the app

```json
flask app   # run a local daemon on port 5000
flask shell # start shell with access to app functions
```
Run tests

```json
pytest
```




## Configuration

There are `tk` two sample configurations in the `config` folder.  

* `CLASSIFIER_MODEL` location of Keras model hdf5 
* `CLASSIFIER_TRUE` is a human readable true string  
* `CLASSIFIER_FALSE` is the human readable false string 
* `CLASSIFIER_THRESH` is the threshold of truth 

If not provided, values default to the current example (i.e. 'Dog', 'Cat', 0.5)

## Deployment with docker

Build the docker image

```
docker build -t f9k9:latest .
```

Run the docker image on port 5000

```
docker run -d -p 5000:5000 f9k9
```

## Usage

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

> This setting is disabled by default

If the client has no local storage and the `ALLOW_PROXY` setting is `True`, the app will
 download and analyze image urls passed individually into the `url` parameter or as an 
 array into the `urls` parameter.   
 
 No multi-threading is done and it downloads images one at a time.

```
curl -d 'verbose=true' \
     -d 'url=https://ipfs.io/ipfs/QImAnInvalidHashhhhhhhh/cat.jpg'  \
     -d 'url=https://ipfs.io/ipfs/QmW2WQi7j6c7UgJTarActp7tDNikE4B2qXtFCfLPdsgaTQ/cat.jpg' \
     -d 'urls[]=https://upload.wikimedia.org/wikipedia/commons/b/b9/CyprusShorthair.jpg' \
     -d 'urls[]=https://upload.wikimedia.org/wikipedia/commons/4/4d/Cat_November_2010-1a.jpg' \
     -d 'urls[]=https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/June_odd-eyed-cat.jpg/1260px-June_odd-eyed-cat.jpg' \
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

* Caching 
* Generalize from binary to a list of categories.
* Vector input (svg, pdf)
* Video input (mp4, avi)