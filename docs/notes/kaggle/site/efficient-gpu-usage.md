# Efficient GPU Usage Tips

Kaggle provides free access to NVIDIA TESLA P100 GPUs. These GPUs are useful for training deep learning models, though they do not accelerate most other workflows (i.e. libraries like pandas and scikit-learn do not benefit from access to GPUs).

You can use up to a quota limit per week of GPU. The quota resets weekly and is 30 hours or sometimes higher depending on demand and resources

Here are some tips and tricks to get the most of your GPU usage on Kaggle. In general, your most helpful levers will be:

- Only turn on the GPU if you plan on using the GPU. GPUs are only helpful if you are using code that takes advantage of GPU-accelerated libraries (e.g. TensorFlow, PyTorch, etc).
- Actively monitor and manage your GPU usage
- Kaggle has tools for monitoring GPU usage in the settings menu of the Notebooks editor, at the top of the page at kaggle.com/notebooks, on your profile page, and in the session management window.
- Avoid using batch sessions (the commit button) to save or checkpoint your progress. Batch sessions (commits) run all of the code from top to bottom. This is less efficient than simply downloading the .ipynb file from the Notebook editor.
- Cancel unnecessary batch sessions
- The same Notebook can have multiple concurrent batch sessions if you press the commit button prior to completing the first commit. If your latest code has been updated as compared to your previous code, it is likely better for you to cancel that first commit and leave only the 2nd commit running.
- Stop interactive sessions prior to closing the window. Interactive sessions remain active until they reach the 60 minute idle timeout limit. If you stop the session prior to closing your window it can save you up to 60 minutes of compute.
- You can use the Active Events window in the lower left hand corner of your screen to manage your active sessions including stopping unused interactive sessions. [Learn more about Active Events here](https://www.kaggle.com/product-feedback/193925).
- Consider using the Kaggle-API to avoid interactive sessions entirely. With the Kaggle API you can push a new version of your notebook without ever opening up an interactive session in the Notebook editor.

We hope help you get the most from our free GPU compute. Happy Kaggling!