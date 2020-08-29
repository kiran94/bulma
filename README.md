# Bulma

A companion to [Vegeta](https://github.com/tsenart/vegeta) that tells him what to do.

**bulma.config.json**

```json
{
    "Project": "Project 1",
    "Duration": "2s",
    "Corpus": [
        {"desc":"Loading Instagram","method":"GET","url":"https://www.instagram.com/","header": {"Content-Type":["text/plain"]}, "body": "hello" },
        {"desc":"Loading Facebook","method":"GET","url":"https://www.facebook.com/","header": {"Content-Type":["text/json"]}, "body_file": "examples/fb_body_file.json" }
    ]
}
```