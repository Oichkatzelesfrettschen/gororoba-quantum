> Full piece: [https://www.quantum-inspire.com/faq/](https://www.quantum-inspire.com/faq/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 ab2c5b8a1f27bc58b131d3eb93a50962b5b332937d05880230bc5ffd70632e82.

# FAQ

![](https://www.datocms-assets.com/119587/1584000832-faq.jpg)

## Scheduled and unscheduled maintenance

Maintenance of our systems is crucial. To give you the best performance we are doing extra maintenance, tuning and calibration of our systems and are preparing our systems for some hardware upgrades. This may lead to limited online availability and/or reduced performance of our systems. Meanwhile you can continue using our simulators.

Note that we also use our backends for research and development. This does mean that our backends are sometimes offline for a longer period. We will announce this on our website where possible.

## Known issues and Frequently Asked Questions

### reporting bugs or issues

**I found a bug that is not listed below or I want to provide some feedback on QI. Who do I contact?**

Your feedback, questions, bugs and comments can be sent to:

<support@quantum-inspire.com>

Please include where possible:

- a detailed description of the error/bug, with step by step instructions how to reproduce the error
- what exactly happened
- what you were expecting to happen
- a copy of your code that returns an error
- a screenshot of your observations

### Login and accounts

**I forgot my password or want to change it**

You can reset your password by clicking the 'Forgot password?' link on the log in screen or 'Change password' under My Account. Enter your email address and you will be sent a link to change your password.

**I want to delete my account**

If you want your account and user data to be deleted, please [contact our support team at support@quantum-inspire.com](mailto:support@quantum-inspire.com). Once your account is deleted, it cannot be restored.

**I cannot login with my account**

Your login name is the email address that you used for registration. If you keep having issues with logging in and resetting your password does not help, please [contact our support team at support@quantum-inspire.com](mailto:support@quantum-inspire.com).

**I cannot change my username or email address**

This functionality is not included. if you have issues with your account please [contact our support team at support@quantum-inspire.com](mailto:support@quantum-inspire.com).

**Password not accepted during registration or change of password.**

When your password does not conform to the requirements, it is not accepted. Sometimes this happens silently (you don't get feedback that it failed or why). Please make sure you follow the following password requirements:

- Should not be similar to your email address (or parts thereof)
- Must be 8 characters at least
- Cannot be too common (things like ‘secret’ are not allowed)
- Cannot be just numbers

**Password change does not work even when I use the rules above.**

When you register your account you are requested to provide your email address.

- Please check whether you filled in the correct email address.
- We do not check for correctness of the email address to avoid database probing.

**I did not get a confirmation email.**

This may have the following causes:

- Receiving the email sometimes takes a few minutes. If the actions below do not work, please wait for about ten minutes.
- We do not check for correctness of the email address to avoid database probing. Make sure you do not have a typing error in your email address (like <myname@gmial.com> instead of <myname@gmail.com>)
- The confirmation email is regarded as spam. Please check your spam-box or contact your emial provider.
- Some Chinese providers like NetEase (163.com) and Tencent (qq.com) show a high rate of email bounces (our confirmation mail does not reach the new user). If you experience these issues contact us directly at <support@quantum-inspire.com> so we can help ou activate your account.

### Writing algorithms

**No known issues**

### Executing algorithms

**It takes many minutes/hours for my job to be executed.**

We have two quantum chip chips available. When many users submit jobs, your job will be put in the queue and executed when it reaches the front of the queue. You are not allowed to have more than 3 jobs in the queue for a hardware backend, in order to provide equal access opportunities for everybody. (Attempts of) abuse will lead to removal of your account.

- The status of the execution is automatically refreshed in your web browser every 30 seconds. On most browsers clicking F5 will actively refresh your browser and results status.
- Including overhead a typical quantum-only job on a hardware backend takes 30 to 90 seconds. There may be other jobs before you in the queue which will add to the waiting time.
- A hybrid job, including both classical and quantum parts may take up to 15 minutes or longer to execute.
- Hardware backends require regular tuning to maintain their optimum performance. Each backend comes with an extensice automated tuning program that takes from a few seconds to 30 minutes long. When your job is scheduled while tuning is ongoing, this will add to your waiting time.
- It could be that you selected a large number of shots for an algorithm. Try to start a new project with a smaller number of shots and re-run. Please [contact our support team at support@quantum-inspire.com](mailto:support@quantum-inspire.com) if you think your algorithm stays in queue for a too long time.

**Based on the reported fidelities I expect a higher probability for certain outcomes of experiments.**

The reported fidelities for single- and two-qubit gates are based on standard benchmark methods like randomized benchmarking, which are independent of initialization and readout fidelity (sometimes reported as visibility), which are usually the dominant factor in current state-of-the-art devices. In research papers, the initialization and readout fidelities are sometimes *compensated* by performing normalization of the results. We do not normalize the outputs of our measurements, in order to show the actual measured outcomes, including all infidelities/errors of the system.

**The histogram shows up empty and an error message is shown instead.**

This usually indicates an error in the backend, e.g. due to a syntax error. Check the error output file for hints on what might be wrong.
