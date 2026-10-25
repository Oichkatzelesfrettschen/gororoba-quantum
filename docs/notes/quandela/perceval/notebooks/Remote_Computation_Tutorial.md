> Full piece: [https://perceval.quandela.net/docs/v1.3/notebooks/Remote_Computation_Tutorial.html](https://perceval.quandela.net/docs/v1.3/notebooks/Remote_Computation_Tutorial.html)
> Retrieved 2026-10-25T09:12Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 7620330d92d010c642be6c7a52b3ef15235943e2abee2d0fdaf04b1e93671f37.

# Remote Computing

In this tutorial, we are going to send computations on remote platforms using Perceval. A “platform” is an online simulator or an actual physical photonic QPU available through a Cloud provider.

The main provider is the Quandela Cloud but please note that others exist, see [providers](https://perceval.quandela.net/docs/reference/providers.html) for additional information.

## I. Updated Hello World

Remember the *Hello World* code from the *Getting Started* page? Let’s update it in order to run the same simulation on a remote platform.

```
[1]:
```

``` python
import time
import math
from pprint import pprint
from tqdm.notebook import tqdm

from perceval import BS, PS, BasicState, RemoteConfig, Experiment, ExecutionFactory, RemoteComputer, QuandelaCommunicationLayer, pdisplay, NoiseModel, acquire
```

```
[3]:
```

``` python
# The first few lines remain unchanged
experiment = Experiment(BS())
experiment.with_input(BasicState("|1,1>"))
experiment.min_detected_photons_filter(1)

noise_model = NoiseModel(transmittance=0.05, indistinguishability=0.85)

# In this version, the local SimulatedComputer is replaced by a RemoteComputer which is constructed slightly differently:
# - It takes a CommunicationLayer that is able to talk to one provider. Here, we will use the Quandela one, constructed like this:
#   - The back-end name "SLOS" is replaced by the name of the platform we want to send our computation on (here, "sim:slos").
#   - The 2nd parameter is an authentication token to the Cloud provider we're using (by default, the Quandela Cloud).
#      Let's assume we have a valid token, for now. We'll see how to generate one, later on, in this tutorial.
# - Noise parameters can still be set, since this is a simulation platform
computer = RemoteComputer(QuandelaCommunicationLayer("sim:slos", "a valid authentication token"))
computer.noise = noise_model

# Starting from here, SimulatedComputer and RemoteComputer are fully interchangeable
# Here, the max_shots_per_call parameter is required to limit your credit usage on the Cloud
factory = ExecutionFactory(computer, experiment, max_shots_per_call=10_000)
with acquire(computer):
    samples = factory.sample_count(10_000)['results']
    probs = factory.probs()['results']
    print(f"Samples: {samples}")
    print(f"Probabilities: {probs}")
```

\
Samples: {\
  \|2,0\>: 115\
  \|0,2\>: 128\
  \|1,1\>: 24\
  \|1,0\>: 4829\
  \|0,1\>: 4904\
}\
Probabilities: {\
        \|1,0\>: 0.487179\
        \|1,1\>: 0.001923\
        \|0,1\>: 0.487179\
        \|0,2\>: 0.011859\
        \|2,0\>: 0.011859\
}\

Similar enough, isn’t it?

*A quick note on the* `with`` ``acquire(computer):` *line:*

On most computers, this line will do nothing. However, there are some providers that require to start a session before launching executions. This context manager starts that session at entering and stops it at exiting. For versatility, it is thus highly recommended that this line is always written, no matter which computer is used. It must be placed at the topmost level of the usage of the computer, typically at the same level as instantiation and destruction, so that start and stop are called only once (calling them several times could lead to disastrous behaviour).

If this is not possible or not wished to call this in your code, you can also call the `computer.start()` and `computer.stop()` methods manually, but nothing will guarantee that the `stop()` method is executed in case of errors.

Also, it can be replaced by a `with`` ``computer.acquire()` call, but the `acquire()` method can take several computers at once.

## II. Preparing for remote computing

Connecting to a remote provider requires a bit of configuration. You need to be able to connect and authenticate to the remote service.

Quandela Cloud authentication is managed through *user tokens*. These are created on the Cloud website, from your user account page. If you haven’t done so beforehand, please visit [cloud.quandela.com](https://cloud.quandela.com) and create an account. You’ll be able to check what platforms are available to you, as well as their specifications. You have to generate a token in order to use any platform on the Cloud using a Perceval script. A token is personal and should not be shared. You can create as many as you wish on a single account.

You can set your connection information up once and for all on a given computer, using Perceval persistent data system:

```
[3]:
```

``` python
# Save your token, cloud url and proxy configuration in a RemoteConfig instance, then call save().
# You only need to do this once per machine, data will be shared among different Perceval installs on the same machine.
# If your token changes, you'll need to redo this step once.
remote_config = RemoteConfig()  # The RemoteConfig is for the Quandela Provider
remote_config.set_token("MY_TOKEN")
remote_config.set_url("https://api.cloud.quandela.com") # Optional, by default the url is https://api.cloud.quandela.com
remote_config.set_proxies({"https": "socks5h://USER:PASSWORD@HOST:PORT"})  # Optional proxy configuration
remote_config.save()
```

If you need to use multiple authentication information within the same script, you will have to enter the token value for each RemoteComputer, as shown in the updated Hello World.

## III. Connect to a platform

Once you have chosen the platform you want your code executed on, all you have to do is to copy its name and define a `RemoteComputer` with it. Don’t forget to give the platform access rights to your token. Note that all simulators platform name start with “sim:” where an actual QPU starts with “qpu:”.

```
[4]:
```

``` python
# A RemoteComputer sends executions to a platform through its communication layer.
remote_simulator = RemoteComputer(QuandelaCommunicationLayer("sim:belenos")) # For instance, connect to sim:belenos
```

You can now access to the specifications of the platform directly in Perceval.

```
[5]:
```

``` python
specs = remote_simulator.specs
pdisplay(specs.architecture, recursive=True)
```

```
[5]:
```

![](https://perceval.quandela.net/docs/v1.3/_images/notebooks_Remote_Computation_Tutorial_14_0.svg)

```
[6]:
```

``` python
print("Platform constraints:")
pprint(specs.constraints)
print("\nPlatform supported parameters:")
pprint(specs.parameters)
```

\
Platform constraints:\
{'max_mode_count': 24,\
 'max_photon_count': 12,\
 'max_sample_count': None,\
 'min_mode_count': 1,\
 'min_photon_count': 1,\
 'support_multi_photon': False}\
\
Platform supported parameters:\
{'final_mode_number': 'number of modes of the output states. States having a '\
                      'photon on unused modes will be ignored. Useful when '\
                      'using computed circuits (default input_state.m)',\
 'min_detected_photons': 'minimum number of detected photons to keep a state '\
                         '(default input_state.n)',\
 'use_photon_recycling': 'boolean enabling the Photon Recycling noise '\
                         'mitigation process. (default enabled whenever it can '\
                         'be used)'}\

## IV. Run a remote simulation

Now, we can set our computation up. In order to give a value to a “platform supported parameter”, you have to use a special `set_parameter` function (or `set_parameters` to set multiple at once).

```
[7]:
```

``` python
experiment = Experiment(BS() // PS(phi=math.pi/4) // BS())
experiment.with_input(BasicState([1, 1]))
experiment.min_detected_photons_filter(1)

remote_simulator.noise = NoiseModel(indistinguishability=.95, transmittance=.1, g2=.01)
```

We can now use the `ExecutionFactory` with our `RemoteComputer`. You have to set a maximum shots threshold (`max_shots_per_call` named parameter) when creating an `ExecutionFactory` with a remote platform. Local simulations do not require this threshold. A shot is any detected event containing at least one photon, it is easy to explain, easy to measure. This shot threshold will prevent the user from consuming too many QPU resources, as once it’s reached, the acquisition stops. Shots up to this threshold can be reached for all executions generated by `ExecutionFactory` calls (e.g. calling `sample_count` thrice can lead to the use of at most `3*max_shots_per_call` shots).

A bit of terminology: we call job a computation sent to the cloud platform. This is what appears on the cloud interface. An `Execution` can create one or several jobs depending on where the error mitigation is executed and its nature. In any case, the `Execution` handles the complexity of dealing with several jobs.

```
[8]:
```

``` python
nsamples = 200000
# You have to set a 'max_shots_per_call' named parameter
factory = ExecutionFactory(remote_simulator, experiment, max_shots_per_call=nsamples)
# Here, with `min_detected_photons_filter` set to 1, all shots are de facto samples of interest.
# Thus, in this particular case, the expected sample number can be used as the shots threshold.

factory.default_job_name = "My sampling job"  # All jobs created by this factory instance will have this custom name on the cloud

# Create an execution and run it asynchronously (with execute_async method). Calling execute_sync, or __call__ would run the execution synchronously
# and would thus block the script execution until the execution ends and results are returned.

# When using async executions, we should not stop the session before its end, so we call start() and stop() manually since we will get the results in another cell (we could have used `with acquire()` if we did both in the same cell)
remote_simulator.start()
remote_execution = factory.sample_count.execute_async(nsamples)
print(remote_execution.status)  # We can check that the job has been sent
```

\
WAITING\

The request has now been sent to a remote platform through the cloud. As it is asynchronous, other computations can be performed locally before the results are retrieved. In this example, let’s just wait for the end of the computation. If you go to the Quandela Cloud website again, you can now see the job and its progress.

```
[9]:
```

``` python
previous_prog = 0
with tqdm(total=1, bar_format='{desc}{percentage:3.0f}%|{bar}|') as tq:
    tq.set_description(f'Get {nsamples} samples from {remote_execution.computer.name}')
    while not remote_execution.is_complete:
        tq.update(remote_execution.status.progress - previous_prog)
        previous_prog = remote_execution.status.progress
        time.sleep(1)
    tq.update(1-previous_prog)
    tq.close()

print(f"Job status = {remote_execution.status()}")
```

\
Job status = SUCCESS\

Once the previous cell has run to the end, the execution is finished (again, you can see its status on the website). Let’s retrieve the results to do some computation. In this case, the computation is expected to be fast (unless the simulator is unavailable or there are a lot of jobs queued), so we can use the `remote_execution` object we created previously. If the computation lasted for a long time, we could have shut down our computer, then turn it back on and finally created a new execution object by serializing and deserializing our `remote_execution` object. Note that the serialization doesn’t store your authentification data for security reason, so deserialization uses the `RemoteConfig` that we configured earlier to set it back.

```
[10]:
```

``` python
 # To retrieve your execution using a serialization/deserialization round
'''
from perceval import serialization
ar = serialization.OutputArchive()
serialization.Serialization.serialize(remote_execution, ar)
serialized = ar.to_text()  # Save this text somewhere

ar = serialization.InputArchive()
ar.from_text(serialized)
remote_execution = serialization.Serialization.deserialize(ar)  # Will fail if RemoteConfig has no token
'''

results = remote_execution.get_results()

# Now, everything we wanted to do with this computer is finished
remote_simulator.stop()
pdisplay(results['results'])
```

| state   | count |
|---------|------:|
| \|0,1\> | 94910 |
| \|1,0\> | 94788 |
| \|1,1\> |  5497 |
| \|0,2\> |  2425 |
| \|2,0\> |  2369 |
| \|1,2\> |     7 |
| \|2,1\> |     4 |

## V. Use a real photonic QPU

You can run the same sampling on the corresponding QPU. In order to manage your QPU credits, you can estimate the number of shots you’d need for a particular data acquisition. Please note that the maximum shots and maximum samples number act as a dual threshold system. As soon as one of these thresholds is exceeded, the acquisition stops and the results are returned.

```
[15]:
```

``` python
nsamples = 200000

remote_qpu = RemoteComputer(QuandelaCommunicationLayer("qpu:belenos"))
factory.computer = remote_qpu
computation = factory.build_computation("sample_count")  # We will need this for the shot estimation
computation.add_params(max_samples = nsamples)

print("With this setup:")
experiment.min_detected_photons_filter(2)
required_shots = remote_qpu.estimate_required_shots(computation, nsamples=nsamples)
print(f"To gather {nsamples} 2-photon coincidences on {remote_qpu.name}, you would need around {required_shots} shots.")

experiment.min_detected_photons_filter(1)
required_shots = remote_qpu.estimate_required_shots(computation, nsamples=nsamples)
print(f"To gather {nsamples} photon events (with at least 1 photon) on {remote_qpu.name}, you would need exactly {required_shots} shots.")
```

\
With this setup:\
To gather 200000 2-photon coincidences on qpu:belenos, you would need around 7038841 shots.\
To gather 200000 photon events (with at least 1 photon) on qpu:belenos, you would need exactly 200000 shots.\

```
[16]:
```

``` python
factory.max_shots_per_call = nsamples

remote_qpu.start()

remote_execution = factory.sample_count
remote_execution.name = "QPU sampling"  # You may also specify a name to individual jobs
remote_execution.execute_async(nsamples);
```

```
[17]:
```

``` python
previous_prog = 0
with tqdm(total=1, bar_format='{desc}{percentage:3.0f}%|{bar}|') as tq:
    tq.set_description(f'Get {nsamples} samples from {remote_execution.computer.name}')
    while not remote_execution.is_complete:
        tq.update(remote_execution.status.progress/100-previous_prog)
        previous_prog = remote_execution.status.progress/100
        time.sleep(1)
    tq.update(1-previous_prog)
    tq.close()

print(f"Job status = {remote_execution.status()}")
```

\
Job status = SUCCESS\

```
[18]:
```

``` python
results = remote_execution.get_results()
remote_qpu.stop()

pdisplay(results['results'])
```

| state   | count |
|---------|------:|
| \|0,1\> | 99079 |
| \|1,0\> | 94286 |
| \|2,0\> |  2628 |
| \|1,1\> |  2064 |
| \|0,2\> |  1935 |
| \|2,1\> |     5 |
| \|1,2\> |     3 |

Now, you know the basic ways to compute results using Quandela Cloud.
