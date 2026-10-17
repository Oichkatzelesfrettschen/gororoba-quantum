> Full piece: [https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/02-job-creation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/02-job-creation)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/quantum-toolbox-guide/chemistryvqe/02-job-creation.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Job Creation

## Request

The `--url` argument has to be on this form:

- `https://api.cloud.quandela.com/qt/chemistryvqe`

The `--data` argument (JSON) needs:

- A `geometry` field: [MANDATORY]
  - This field is a list of elements composed of:
    - `element`: One of the elements present in the molecule.
    - `coordinates`: The coordinates of the current element in the molecule in the `'sto-3g'` basis.
  - *<u>Example</u>: `[('Li', (0.,  0., 0.)), ('H', (0., 0., 0.7414))]` represent 1 lithium and 1 hydrogen atom separated by 0.7414 Angstrom on the Z axis.*

- A `platform_name` field: [MANDATORY]
  - You can set here the name of the platform you want to use from the cloud
  - *<u>Examples</u>: `sim:ascella` , `sim:clifford`, `qpu:ascella`, …*

- A `max_iteration` field: [NOT MANDATORY]
  - This **integer** represents the maximum number of iterations for the optimization algorithm.
  - If not precised in the request or set to *'null'*, the default value will be **200**.
  - Must be greater than or equal to 1.

Example of a Shell Post request using cURL:

```bash
curl --request POST \
  --url https://api.cloud.quandela.com/qt/chemistryvqe \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123.....' \
  --header 'Content-Type: application/json' \
  --data '{
  "geometry": [
    {
      "coordinates": [
        0,
        0,
        0
      ],
      "element": "Li"
    },
    {
      "coordinates": [
        0,
        0,
        1.595
      ],
      "element": "H"
    }
  ],
  "max_iterations": null,
  "platform_name": "sim:ascella"
}'
```

Example of a python request using requests:

```python
import requests

url = "https://api.cloud.quandela.com/qt/chemistryvqe"
headers = {
    "Accept": "application/json",
    "Authorization": "Bearer 1234.....",
    "Content-Type": "application/json"
}
data = {
    "geometry": [
        {
            "coordinates": [
                0,
                0,
                0
            ],
            "element": "Li"
        },
        {
            "coordinates": [
                0,
                0,
                0.7414
            ],
            "element": "H"
        }
    ],
    "max_iterations": null,
    "platform_name": "sim:ascella"
}

response = requests.post(url, headers=headers, json=data)

print(response.json())
```

> *Be careful! These queries are just examples! They won't work because the token is in the wrong format.*

## Responses

### Correct

- Here is the response when you send a **correct** request:
  - The `job_id` is used in the GET request ([Chemistry VQE - Job Results](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/04-job-results)) to get more informations about the current job

```json
200 Ok
{
  "job_id": "f1ebeb88-b349-4b41-a7bf-b594717ab090"
}
```

### Errors

> *It is important to note that the errors listed here are **not exhaustive**! However, most errors are **explicit** and **easily understandable**.*

- This is the error you receive when you try to send a request for an algorithm with a token that **does not have the correct access**:

```json
400 Bad Request
{
  "error": "No permission to use algorithm qt/chemistryvqe"
}
```

*<u>Solution</u> : Give a correct access to you token on the Quandela Cloud*

- This is the error you receive when you try to send a **bad written request**:

```json
400 Bad Request
{
  "error": "The browser (or proxy) sent a request that this server could not understand."
}
```

*<u>Solution</u> : Check your request to see if you missed a punctuation…*

- Here are the errors when you send an **invalid credentials** (token empty or wrong):

```json
401 Unauthorized
{
  "error": "Invalid credentials"
}
```

```json
401 Unauthorized
{
  "error": "Invalid token"
}
```

```json
500 Internal Server Error
{
  "error": "Invalid header padding"
}
```

```json
500 Internal Server Error
{
  "error": "Not enough segments"
}
```

```json
500 Internal Server Error
{
  "error": "Invalid crypto padding"
}
```

```json
500 Internal Server Error
{
  "error": "Invalid header string: 'utf-8' codec can't decode byte 0xc2 in position 13: invalid continuation byte"
}
```

*<u>Solution</u>: Verify that you have well copied your token in your request*

- Here is the error when you send a valid credential but with a **not verified email**:

```json
401 Unauthorized
{
  "error": "Your email has not been verified"
}
```

*<u>Solution</u> : Check your mailbox to allow your email verification*

- This is the error you receive when you try to send an **uncompleted request**:

```json
422 Unprocessable Entity
{
  "detail": {
    "json": {
      "geometry": [
        "Missing data for required field."
      ]
    }
  },
  "message": "Validation error"
}
```

*<u>Solution</u> : Check your request to see if you follow the structure. You must have forgotten a required field...*

- This is the error you receive when you try to send an **wrong chimical element** in your request:

```json
422 Unprocessable Entity
{
  "detail": {
    "json": {
      "geometry": [
        "Input must represent either LiH or BeH2 molecule."
      ]
    }
  },
  "message": "Validation error"
}
```

*<u>Solution</u> : Check your request to see if you have only H/Li/B molecules in the fields "element".*

- Here is the error when you send a request to the **wrong url**:

```json
404: NOT FOUND
{
  "error" : "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
}
```

*<u>Solution</u>: Verify that you have well copied the URL*
