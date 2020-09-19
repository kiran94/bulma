# Bulma

![Upload Python Package](https://github.com/kiran94/bulma/workflows/Upload%20Python%20Package/badge.svg)

A companion to [Vegeta](https://github.com/tsenart/vegeta) that tells him what to do. Define a configuration file like below and run: 

```sh
python -m bulma -c samples/bulma.config.json
```

**bulma.config.json**

```json
{
    "Project": "My Super Project",
    "Duration": "5s",
    "Rate": "50/1s",
    "Header": {
        "Content-Type":[ "application/json" ],
        "Accept-Encoding":[ "*" ]
    },
    "Corpus": [
        {
            "id": "Getting Todo JSON data",
            "method": "GET",
            "url": "https://jsonplaceholder.typicode.com/todos/1",
            "header": { "Content-Type": ["application/json"] }
        },
        {
            "id": "Converting text to Md5",
            "method": "GET",
            "url": "http://md5.jsontest.com/?text=example_text",
            "header": { "Content-Type": ["application/json"] }
        }
    ]
}
```

Each of the cases within the `Corpus` are passed directly to [Vegeta's JSON format](https://github.com/tsenart/vegeta#json-format) allowing you to specify anything that would normally be supported by that tool.

Bulma supports the following body types which can be attached to any cases witin the `Corpus`:

- `body`: Raw string body
- `body_file`: Relative location to a file, content's are extracted
- `body_graphql`: Relative location to a file containing a GraphQL query. contents are extracted and pushed into `query` property for a GraphQL request

[Full Sample](samples/bulma.config.json)