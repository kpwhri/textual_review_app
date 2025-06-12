
<h1 style="text-align: center;">
    <!--- img src="" --->
    <br>
    Textual Review App
    <br>
</h1>

<h4 style="text-align: center;">
    NLP Review tool using textual
</h4>

<p style="text-align: center">
    <a href="#features">Features</a>
    <a href="#usage">Usage</a>
    <a href="#license">License</a>
</p>

## Features

## Usage

### Prerequisites

What you'll need:
1. The code installed locally:
  * `git clone https://github.com/kpwhri/textual_review_app`
  * `cd textual_review_app`
  * `pip install .`
2. A pre-processed corpus in jsonlines format (see more info [below](#corpus))
3. Configuration File (see [below](#config-file))

Examples configs and corpus are available in [`/example/wksp`](/example/wksp)

### Deployment

The app can be deployed in different ways: command line or web.

For all of these approaches, you'll need to clone and install:


For command line:
* `textual-review-app /path/to/config.toml`

For web:
* `textual-review-web /path/to/config.toml --port 8080`

#### Command Line

Run the application:
* `textual-review-app /path/to/config.toml`

#### Web

Run the application:
* `textual-review-web /path/to/config.toml --port 8080`

Open a browser, and navigate to `127.0.0.1:8080` and begin your review.

To use the computer as a server for external access, deploy with:
* `textual-review-web /path/to/config.toml --host 0.0.0.0 --port 8080`

Open a browser and navigate to `SERVER_NAME:8080` where `SERVER_NAME` is the computer name.


#### Web Behind a Proxy

Textual-serve doesn't currently have a way to add authentication. One approach for providing basic authentication is to use caddy. To setup caddy:
* Download the relevant caddy executable from the Github repo: https://github.com/caddyserver/caddy/releases
  * Unzip to, e.g., C:\caddy
* Create authentication hashes
  * Decide username/passwords to use (e.g., `user`, `s3cret+`)
  * Hash the password with `C:\caddy\caddy.exe hash-password`
  * Type and then confirm password `s3cret+`
  * Copy the result hash
* Create Caddyfile to store confiration
  * Create a new textfile in `C:\caddy\Caddyfile`
  * Include content like this, which will:
    * Listens on `SERVER_NAME:8080/review`
    * Run textual app listening on `--port 8081`
    * On textual app, set `--public-url SERVER_NAME:8080`

```
:8080 {

    route /review {
        basicauth * {
            user $2a$14...[include hash here]
        }

        uri strip_prefix /review

        reverse_proxy localhost:8081 {
            transport http {
                versions h1
            }
        }
    }
}
```
* Launch `textual_review_app`
  * `python /path/to/config.toml --port 8081 --public-url SERVER_NAME`
* Launch caddy: `C:\caddy\caddy.exe run`

***SERVER_NAME***: computer name, and may require `http` prefix (e.g., `http://pc123.example.com:8080`)


## Corpus

The corpus required as input includes matches with context windows. The best approach to getting this format is to create a jsonlines corpus, create some regular expression patterns to review, and run `textual-review-search`. Examples for all of these steps is in [`/example/wksp`](/example/wksp)

* A jsonlines corpus is requires. In preparation, create a jsonlines corpus with 'text' and any metadata keys:
  * `{"text": "Target text to search", "id": 1, ...}`
* Create a `patterns.txt` file with the following format:
  * `CATEGORY==regex`
* Run `textual-review-search /path/to/patterns.txt /path/to/corpus.jsonl`
* This will output a `corpus.patterns.jsonl` which you can use as input.

## Config File

To run the app, we need to provide some settings. It's best not to modify this after the review has started as certain keys (e.g., `offset`) are used to maintain state by the application.

```toml
title = "App Name"
offset = 0
corpus = "/path/to/corpus.patterns.jsonl"
highlights = []
instructions = [
    "Review and select the relevant options."
]
options = [
    'Relevant',
    'Uncertain',
    'Not Relevant'
]
```

## License

* [MIT License](https://kpwhri.mit-license.org)
