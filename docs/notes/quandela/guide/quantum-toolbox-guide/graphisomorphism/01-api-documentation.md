> Full piece: [https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphisomorphism/01-api-documentation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphisomorphism/01-api-documentation)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/quantum-toolbox-guide/graphisomorphism/01-api-documentation.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Graph Isomorphism

## What is this algorithm?

This **graph isomorphism** algorithm output if two graphs are isomorphic or not.

[**Graph isomorphism**](https://en.wikipedia.org/wiki/Graph_isomorphism) is a concept in graph theory that refers to the notion of two graphs being structurally identical, or essentially the same, despite potentially having different labels assigned to their vertices and edges. The problem is not known to be solvable in [polynomial time](https://en.wikipedia.org/wiki/Polynomial_time).

![image-20240307-110157.png](https://cloud.quandela.com/webide/docs-assets/425918469.png)

Here is the **structure of the algorithm:**

1. First, it encodes two input graphs into two single linear optical circuits.
2. Take samples from both circuits and post-selects them:

![post selection image.png](https://cloud.quandela.com/webide/docs-assets/429883402.png)

3. For each value of **x** (randomly chosen points calculated with `epsilon`), we observe whether the values of the **Laplacian permanental polynomial** for each circuits correspond or not:
   1. If for one value of x, the Laplacian permanents of each graph are not the same (computed up to some `error` value), then the output result is **False**.
   2. When, for all the values of x, the **permanent estimation is** the same for both graphs, then the graphs are isomorphic and the output of the algo is **True**.

      The permanent with Laplacian permanental polynomial is calculated with the following formula:

![image-20240311-152020.png](https://cloud.quandela.com/webide/docs-assets/430768143.png)

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

- Here is the web page for the POST request of Graph Isomorphism: [Quandela Web Api 1.0.0 - Elements](https://api.cloud.quandela.com/api/docs/#/paths/qt-graphIsomorphism/post)
- Here is the web page for the GET request of Graph Isomorphism: [Quandela Web Api 1.0.0 - Elements](https://api.cloud.quandela.com/api/docs/#/paths/qt-graphIsomorphism-job_id/get)

*The example provided serves as a general demonstration aimed at helping you comprehend how to test the API via its web interface:*

1. <u>Modify the authentification Header</u>

You first need to put your token here:

![image-20240305-092806.png](https://cloud.quandela.com/webide/docs-assets/424018077.png)

2. <u>Modify the body</u>

Then you can modify the body of your request:

![image-20240307-103119.png](https://cloud.quandela.com/webide/docs-assets/424706067.png)

3. <u>Send your request</u>

After composing your request, you can submit it to the cloud by clicking the "Send API Request" button:

![image-20240307-103225.png](https://cloud.quandela.com/webide/docs-assets/424837138.png)

4. <u>See your response</u>

Finally, you should see a new window appear displaying the response:

![image-20240305-092917.png](https://cloud.quandela.com/webide/docs-assets/424018086.png)

### Send your first request with cURL (Ubuntu)

- If cURL is not installed on your system, type in a terminal:

```bash
sudo apt install curl
```

- In a terminal try to send this first request to see if you can run **cURL**:

```bash
curl --request POST   --url https://api.cloud.quandela.com/qt/graphIsomorphism
```

- You should see the response from the server:
  - ***TIPS:** If you want more information about the response (such as the **response code**), add the `-v` argument to your request.*

```json
{
  "error" : "Invalid credentials, token not received"
}
```

### Send your first request with Python

- In a python file, write this code:

```python
import requests

r = requests.post('https://api.cloud.quandela.com/qt/graphIsomorphism')
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

Here are the details for the POST request: [Graph Isomorphism - Job Creation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphisomorphism/02-job-creation)

### Job Estimator

This HTTP POST request will create a job with all required data. As a result, you will obtain an estimation of the number of shots.

Here are the details for the POST request: [Graph Isomorphism - Job Estimator](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphisomorphism/03-job-estimator)

### Job Results

This HTTP GET request will retrieve the results for a job and format it as described by the VQE.

Here are the details for the GET request: [Graph Isomorphism - Job Results](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphisomorphism/04-job-results)

## Resources

- Solving graph problems with single-photons and linear optics:
  *Rawad Mezher, Ana Filipa Carvalho, and Shane Mansfield*
  [[2301.09594] Solving graph problems with single-photons and linear optics (arxiv.org)](https://arxiv.org/abs/2301.09594)
- [Graph isomorphism - Wikipedia](https://en.wikipedia.org/wiki/Graph_isomorphism)
