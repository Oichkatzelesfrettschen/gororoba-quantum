> Full piece: [https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphdsi/02-job-creation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphdsi/02-job-creation)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/quantum-toolbox-guide/graphdsi/02-job-creation.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Job Creation

## Request

The `--url` argument has to be on this form:

- `https://api.cloud.quandela.com/qt/graphDSI`

The `--data` argument (JSON) needs:

- A `graph` field: **[MANDATORY]**
  - The graphs are represented with a **list of list** for the edges.
  - *<u>Example</u>:* `[[0,1],[1,2],[2,3],[2,4],[3,4]]` can represent the graph:

  ![image-20240307-143050.png](https://cloud.quandela.com/webide/docs-assets/426409998.png)

- A `seed` field: **[MANDATORY]**
  - A **list** of node numbers from where to start looking for the subgraph.
  - *<u>Example</u>: [0, 1, 2, 3]*

- A `size_subgraph` field: **[MANDATORY]**
  - **Integer** for the size of the subgraph that you want to find.
  - Must be greater than or equal to 1.
  - Be careful! The `size_subgraph` have to be **greater or equal** to the length of the `seed`.
  - *<u>Example</u>: 2*

- A `platform_name` field: **[MANDATORY]**
  - You can set here the name of the platform you want to use from the cloud
  - *<u>Examples</u>:* `sim:ascella` *,* `sim:clifford` *,* `qpu:ascella` *, …*

- A `nb_samples` field: **[NOT MANDATORY]**
  - **Integer** to generate with quantum device for each cycle (depends on the minimum number of samples we want for the estimation)
  - *By default: 100000*

- A `nb_samples_min_accepted` field: **[NOT MANDATORY]**
  - Minimum **integer** of accepted samples after post-selection.
  - *By default: 100*

- A `max_iteration` field: **[NOT MANDATORY]**
  - This **integer** represents the maximum number of iterations for the optimization algorithm.
  - If not precised in the request or set to *'null'*, the default value will be **1000**.
  - Must be greater than or equal to 1.

| **Example of a Shell Post request using cURL** | **Example of a python request using requests** |
| --- | --- |
| <pre>curl --request POST \\<br>  --url https://api.cloud.quandela.com/qt/graphDSI \\<br>  --header 'Accept: application/json' \\<br>  --header 'Authorization: Bearer 123' \\<br>  --header 'Content-Type: application/json' \\<br>  --data '{<br>  "graph": [<br>    [0, 1],<br>    [1, 2],<br>    [2, 3],<br>    [2, 4],<br>    [3, 4]<br>  ],<br>  "max_iterations": 30,<br>  "nb_samples": 10000,<br>  "nb_samples_min_accepted": 100,<br>  "platform_name": "sim:ascella",<br>  "seed": [0],<br>  "size_subgraph": 0<br>}'</pre> | <pre>import requests<br><br>url = "https://api.cloud.quandela.com/qt/graphDSI"<br>headers = {<br>    "Accept": "application/json",<br>    "Authorization": "Bearer 123",<br>    "Content-Type": "application/json"<br>}<br>data = {<br>    "graph": [<br>        [0, 1],<br>        [1, 2],<br>        [2, 3],<br>        [2, 4],<br>        [3, 4]<br>    ],<br>    "max_iterations": 30,<br>    "nb_samples": 10000,<br>    "nb_samples_min_accepted": 100,<br>    "platform_name": "sim:ascella",<br>    "seed": [0],<br>    "size_subgraph": 0<br>}<br><br>response = requests.post(url, headers=headers, json=data)<br><br>print(response.json())</pre> |

> *Be careful! These queries are just examples! They won't work because the token is in the wrong format.*

The full request examples:

```bash
curl --request POST \
  --url https://api.cloud.quandela.com/qt/graphDSI \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --data '{
  "graph": [
    [
      0,
      1
    ],
    [
      1,
      2
    ],
    [
      2,
      3
    ],
    [
      2,
      4
    ],
    [
      3,
      4
    ]
  ],
  "max_iterations": 30,
  "nb_samples": 10000,
  "nb_samples_min_accepted": 100,
  "platform_name": "sim:ascella",
  "seed": [
    0
  ],
  "size_subgraph": 0
}'
```

```python
import requests

url = "https://api.cloud.quandela.com/qt/graphDSI"
headers = {
    "Accept": "application/json",
    "Authorization": "Bearer 123",
    "Content-Type": "application/json"
}
data = {
    "graph": [
        [0, 1],
        [1, 2],
        [2, 3],
        [2, 4],
        [3, 4]
    ],
    "max_iterations": 30,
    "nb_samples": 10000,
    "nb_samples_min_accepted": 100,
    "platform_name": "sim:ascella",
    "seed": [0],
    "size_subgraph": 0
}

response = requests.post(url, headers=headers, json=data)

print(response.json())
```

## Responses

### Correct

- Here is the response when you send a **correct** request:
  - The `job_id` is used in the GET request ([Graph DSI - Job Results](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphdsi/04-job-results)) to get more informations about the current job

```json
200 Ok
{
  "job_id": "f1ebeb88-b349-4b41-a7bf-b594717ab090"
}
```

### Errors

*It is important to note that the errors listed here are **not exhaustive**! However, most errors are **explicit** and **easily understandable**.*

- This is the error you receive when you try to send a request for an algorithm with a token that **does not have the correct access**:

```json
400 Bad Request
{
  "error": "No permission to use algorithm qt/graphDSI"
}
```

> *<u>Solution</u>: Give a correct access to you token on the Quandela Cloud*

- This is the error you receive when you try to send a **bad written request**:

```json
400 Bad Request
{
  "error": "The browser (or proxy) sent a request that this server could not understand."
}
```

> *<u>Solution</u>: Check your request to see if you missed a punctuation…*

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

> *<u>Solution</u>: Verify that you have well copied your token in your request*

- Here is the error when you send a valid credential but with a **not verified email**:

```json
401 Unauthorized
{
  "error": "Your email has not been verified"
}
```

> *<u>Solution</u>: Check your mailbox to allow your email verification*

- This is the error you receive when you try to send an **uncompleted request**:

```json
422 Unprocessable Entity
{
  "detail": {
    "json": {
      "platform_name": [
        "Missing data for required field."
      ]
    }
  },
  "message": "Validation error"
}
```

> *<u>Solution</u>: Check your request to see if you follow the structure. You must have forgotten a required field...*

- Here is the error when you send a request to the **wrong url**:

```json
404: NOT FOUND
{
  "error" : "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
}
```

> *<u>Solution</u>: Verify that you have well copied the URL*
