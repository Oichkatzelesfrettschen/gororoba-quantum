> Full piece: [https://cloud.quandela.com/webide/guide/user-guide/03-token-and-job-management](https://cloud.quandela.com/webide/guide/user-guide/03-token-and-job-management)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/user-guide/03-token-and-job-management.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Token & Job Management

## Creating a token

To start using Quandela Cloud and running jobs on Quandela QPUs or noisy simulators, you need first to create a connection token that you will use to authenticate all your requests to the Quandela Cloud.

> This connection token is personal, and will be using your available credits - so never expose this token when sharing a notebook. If a token has been compromised, you can revoke it and create a new one.

- Connect to your Quandela Cloud personal space at [https://cloud.quandela.com/webide](https://cloud.quandela.com/webide) using the credentials you used for signing-up or you received from your account administrator.
- Open the left panel, and select `Tokens` (or directly go to [Quandela Cloud token management](https://cloud.quandela.com/webide/token) )
- Click on `+ Create New`

![Capture d’écran 2022-11-14 à 16.08.06.png](https://cloud.quandela.com/webide/docs-assets/93421664.png)

- Give a name to your test token - the name is for you a way to remember use and permissions you will give to the token. Set-up the duration of the token. It is a good practice to have tokens with relatively short duration time so that you don’t have to worry about losing them:

![image-20221114-152507.png](https://cloud.quandela.com/webide/docs-assets/93847558.png)

- Your token is created and appears in the token list. You can retrieve the token by clicking on `Show`. Just click the token when it appears and it will be copied to your clipboard:

![Capture d’écran 2022-11-14 à 16.32.50.png](https://cloud.quandela.com/webide/docs-assets/94568449.png)

![Capture d’écran 2022-11-14 à 16.36.38.png](https://cloud.quandela.com/webide/docs-assets/94437379.png)

![Capture d’écran 2022-11-14 à 16.36.46.png](https://cloud.quandela.com/webide/docs-assets/93716483.png)

- You should now copy your token in a safe place and use it every time you want to launch a job on the cloud (see [Your first job on the cloud](#your-first-job-on-the-cloud)).
- By clicking on the eye symbol - you see detailed information associated to each token:

![Capture d’écran 2022-11-14 à 16.53.43.png](https://cloud.quandela.com/webide/docs-assets/93683729.png)

- Click on the `Permissions` tab and you can enable use of platform for your token (select the platforms A, click on B, and `Save` C)

![image-20221114-161607.png](https://cloud.quandela.com/webide/docs-assets/93814817.png)

> if you try to use your token for a platform not associated to your token, an exception will be thrown at runtime like the following:

![image-20221114-164138.png](https://cloud.quandela.com/webide/docs-assets/94470159.png)

## Your first job on the cloud

Once you have configured a token, you are fully ready to launch your first tasks !

You have 2 different ways to do so:

- install locally Perceval on your laptop - see [GitHub - Quandela/Perceval: Installation](https://github.com/Quandela/Perceval#readme) for installation instructions
- connect to an online preconfigured Jupyter notebook

In both cases, check that you have the latest Perceval version installed using the following commands:

```python
import perceval as pcvl
pcvl.__version__
```

You should have the latest available Perceval version (see [https://pypi.org/project/perceval-quandela/](https://pypi.org/project/perceval-quandela/) ).

Then you are ready for your first job following the tutorial here: [Remote computing with Perceval](https://perceval.quandela.net/docs/notebooks/Remote%20computing.html).

## Monitoring jobs on the Cloud

When you have launched your first jobs on Quandela Cloud - you can check the status of the job selecting `Jobs` in the left panel of the web interface (or go directly to [Quandela Cloud Job Management](https://cloud.quandela.com/webide/job)).

You will see your task as following:

![image-20221114-164315.png](https://cloud.quandela.com/webide/docs-assets/93683745.png)

By clicking on the eye symbol on the left you can see details of the task (the workload, ie all the parameters sent by the client, and the output if the task is completed).

![Capture d’écran 2022-11-14 à 17.47.14.png](https://cloud.quandela.com/webide/docs-assets/94470165.png)
