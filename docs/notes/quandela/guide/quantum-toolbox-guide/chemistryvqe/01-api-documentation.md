> Full piece: [https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/01-api-documentation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/01-api-documentation)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/quantum-toolbox-guide/chemistryvqe/01-api-documentation.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Chemistry VQE

## What is this algorithm?

This algorithm is a **variational quantum eigensolver** (VQE), which finds the ground state of the **LiH** or **BeH2** molecules exclusively.

This algorithm uses **cobyla** as a classic optimizer.

Visite this page to have more informations about VQE: [VQE H2 - Algorithm explanation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/vqe/02-algorithm-explanation)

## How to make it work?

This API is a flexible tool for quantum computing. It uses the standard HTTP protocol and supports different data formats like JSON and XML. It ensures security to protect sensitive data and is easy to use. Plus, it integrates smoothly with any existing web setup.

### Create an account & configure Quandela Cloud

To start using Quandela Cloud and running jobs on Quandela QPUs or noisy simulators, you need to first create a **connection token** that you will use to authenticate all your requests to the Quandela Cloud. A complete documentation to make the cloud works is available here: [Documentation - Quandela IDE](https://cloud.quandela.com/webide/guide/user-guide/03-token-and-job-management)

You should find how to:

- [Create a token](https://cloud.quandela.com/webide/guide/user-guide/03-token-and-job-management#creating-a-token)
- [Submit your first job on the cloud](https://cloud.quandela.com/webide/guide/user-guide/03-token-and-job-management#your-first-job-on-the-cloud)
- [Monitor jobs on the Cloud](https://cloud.quandela.com/webide/guide/user-guide/03-token-and-job-management#monitoring-jobs-on-the-cloud)

### Send your first request on the web API interface

You can utilize the web API interface to send requests, providing a straightforward and intuitive method to grasp the API's functionality.

- Here is the web page for the POST request of Chemistry VQE: [Quandela Web Api 1.0.0 - Elements](https://api.cloud.quandela.com/api/docs/#/paths/qt-chemistryvqe/post)
- Here is the web page for the GET request of Chemistry VQE: [Quandela Web Api 1.0.0 - Elements](https://api.cloud.quandela.com/api/docs/#/paths/qt-chemistryvqe-job_id/get)

*The example provided serves as a general demonstration aimed at helping you comprehend how to test the API via its web interface:*

1. <u>Modify the authentification Header</u>

You first need to put your token here:

![image-20240305-092806.png](https://cloud.quandela.com/webide/docs-assets/420806689.png)

2. <u>Modify the body</u>

Then you can modify the body of your request:

![image-20240305-092840.png](https://cloud.quandela.com/webide/docs-assets/420806686.png)

3. <u>Send your request</u>

After composing your request, you can submit it to the cloud by clicking the "Send API Request" button:

![image-20240305-093529.png](https://cloud.quandela.com/webide/docs-assets/420806677.png)

4. <u>See your response</u>

Finally, you should see a new window appear displaying the response:

![image-20240305-092917.png](https://cloud.quandela.com/webide/docs-assets/420806680.png)

### Send your first request with cURL (Ubuntu)

- If cURL is not installed on your system, type in a terminal:

```bash
sudo apt install curl
```

- In a terminal try to send this first request to see if you can run **cURL**:

```bash
curl --request POST   --url https://api.cloud.quandela.com/qt/chemistryvqe
```

- You should see the response from the server:
  - ***TIPS:** If you want more information about the response (such as the **response code**), add the* `-v` *argument to your request.*

```json
{
  "error" : "Invalid credentials, token not received"
}
```

### Send your first request with Python

- In a python file, write this code:

```python
import requests

r = requests.post('https://api.cloud.quandela.com/qt/chemistryvqe')
print(r.json())
```

- Execute your file
- You should see the response from the server:

```json
{
  "error" : "Invalid credentials, token not received"
}
```

## About the requests

For the transmission of informations to the server, the HTTP protocol provides different request methods. The two used in this API are GET and POST. Although both achieve the same result, they are fundamentally different. Here is an overview of how the GET or POST methods are used in this API.

### Job Creation

This HTTP POST request will create a job with all required data, the system will execute it asynchronously.

Here are the details for the POST request : [Chemistry VQE - Job Creation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/02-job-creation)

### Job Estimator

This HTTP POST request will create a job with all required data. As a result, you will obtain an estimation of the number of shots.

Here are the details for the POST request : [Chemistry VQE - Job Estimator](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/03-job-estimator)

### Job Results

This HTTP GET request will retrieve the results for a job and format it as described by the VQE.

Here are the details for the GET request : [Chemistry VQE - Job Results](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/04-job-results)
