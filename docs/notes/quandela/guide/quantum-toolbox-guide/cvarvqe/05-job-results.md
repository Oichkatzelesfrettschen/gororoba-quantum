> Full piece: [https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/cvarvqe/05-job-results](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/cvarvqe/05-job-results)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/quantum-toolbox-guide/cvarvqe/05-job-results.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Job Results

## Request

The `--url` argument has to be on this form:

- `https://api.cloud.quandela.com/qt/cvarvqe/{job_id}`
- The *{job_id}* is given in response to the POST request ([CVaR VQE - Job Creation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/cvarvqe/03-job-creation))

| **Example of a Shell Post request using cURL** | **Example of a python request using requests** |
| --- | --- |
| <pre>curl --request GET \\<br>  --url https://api.cloud.quandela.com/qt/cvarvqe/{job_id} \\<br>  --header 'Accept: application/json' \\<br>  --header 'Authorization: Bearer 123....'</pre> | <pre>import requests<br><br>url = "https://api.cloud.quandela.com/qt/cvarvqe/{job_id}"<br>headers = {<br>    "Accept": "application/json",<br>    "Authorization": "Bearer 123...."<br>}<br><br>response = requests.get(url, headers=headers)<br><br>print(response.json())</pre> |

*Be careful! These queries are just examples! They won't work because **token** and **{job_id}** have to be replaced.*

## Responses

### Correct

- Here is the response when you send a **correct** request.
  - The `status` field can take the value :
    - *running*: The work is being processed
    - *waiting*: The job is in a queue, waiting to be processed
    - *canceled*: The calculations have been canceled
    - *error*: There is an error during the calculation (eg: the server was closed during calculations)
    - *completed*: The job is finished, we have reached the maximum number of iteration.
  - The `duration` field :
    - Tells you the time of the calculations (in seconds)
  - The `progress` field :
    - This field tells you which iteration the job is in.
  - The `intermediate_results` field:
    - Contains the result of each iteration founded for your inputs
    - `bitstring`: The bitstring corresponds to the most probable output state for 1 iteration by the optimization function. The bitstring is represented in the Hilbert space.
    - `loss`: The ground state energy approximation founded for 1 iteration by the optimisation function
    - `timestamp`: Exact date the iteration was performed
  - The `results` field:
    - Contains the final and best values founded for your inputs

```json
{
  "duration": 18,
  "intermediate_results": [
    {
      "bitstring": "00",
      "loss": -22.77308871070437,
      "timestamp": 1709722774.60474
    }
  ],
  "job_id": "bebdd65f-70f1-44c9-aa7f-ef2807900ff7",
  "progress": 1,
  "results": {
    "bitstring": "00",
    "loss": -270.59578966105886
  },
  "status": "completed"
}
```

### Errors

*It is important to note that the errors listed here are **not exhaustive**! However, most errors are **explicit** and **easily understandable**.*

- Here is the error when the job is pending:

```json
500 Internal Server Error
{
  "error": "'<' not supported between instances of 'NoneType' and 'int'"
}
```

*<u>Solution</u> : Wait until the previous jobs are done…*

- Here is the error when the **job ID is not correct**: (Not recognized by the server)

```json
400 Bad Request
{
  "error": "Invalid job id: ab76c93b-5aeb-4b43-956e-d5a95bb5841"
}
```

*<u>Solution</u> : Check if you copied the ID from the POST response correctly.*

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

- Here is the error when you send a request to the **wrong url**:

```json
404: NOT FOUND
{
  "error" : "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
}
```

*<u>Solution</u>: Verify that you have well copied the URL*
