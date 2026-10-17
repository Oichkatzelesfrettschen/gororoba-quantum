> Full piece: [https://docs.openquantum.com/pennylane-plugin/troubleshooting/](https://docs.openquantum.com/pennylane-plugin/troubleshooting/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fc79933e76278291c673029952bab05746dce5daf54b376eb1b80007af1a7314.

# Troubleshooting

Common errors, debugging tips, and solutions for the Open Quantum PennyLane plugin.

## Common Errors

### Missing credentials

**Symptom**: `AuthenticationError: Authentication required. Provide a token or client_id+client_secret...` when constructing the device.

Pass `client=`, `token=` / `OPENQUANTUM_TOKEN`, `client_id`+`client_secret` / `OPENQUANTUM_CLIENT_ID` + `OPENQUANTUM_CLIENT_SECRET`, or an SDK-key file via `OPENQUANTUM_SDK_KEY`. The device builds its client with `OpenQuantumClient.from_env()`.

### Authentication Error (HTTP 401)

**Symptom**: `APIError` with an HTTP 401 status code, indicating the credentials were present but rejected.

**Causes and solutions**:

- **Invalid SDK key credentials.** Verify that your `client_id` and `client_secret` are correct. Client IDs start with `s_`.
- **Environment variables not set.** Check that `OPENQUANTUM_CLIENT_ID` and `OPENQUANTUM_CLIENT_SECRET` are set in your current shell session.
- **SDK key is disabled.** Log in to the [Open Quantum Portal](https://www.openquantum.com) and check that your SDK key is enabled on the [SDK Keys](https://www.openquantum.com/keys) page.
- **SDK key was deleted.** Create a new SDK key in the portal.

[](#__codelineno-0-1)`# Verify environment variables are set`\
[](#__codelineno-0-2)`echo`` ``$OPENQUANTUM_CLIENT_ID`\
[](#__codelineno-0-3)`echo`` ``$OPENQUANTUM_CLIENT_SECRET`\

### Authorization Error (HTTP 403)

**Symptom**: `OpenQuantumDeviceError` with an HTTP 403 status code.

This means the JWT is valid but the user does not have access to the specified organization. Verify that your `organization_id` is correct and that your user account is a member of that organization.

------------------------------------------------------------------------

### Insufficient Credits Error (HTTP 402)

**Symptom**: `OpenQuantumDeviceError` with an HTTP 402 status code, or an error message indicating insufficient credits.

**Solutions**:

- Check your credit balance on your [Dashboard](https://www.openquantum.com/dashboard) page.
- Reduce the number of shots to lower the job cost.
- Choose a backend with lower per-shot costs.
- Purchase additional credits through the portal (via Stripe).
- If using a Private execution plan, ensure you have Full credits (Spark credits only work with the Public plan).

------------------------------------------------------------------------

### Active Job Limit Error (HTTP 409)

**Symptom**: `OpenQuantumDeviceError` with an HTTP 409 status code, or an error message indicating the active job limit has been reached.

Your organization has reached the maximum of **10 active Public jobs** or **100 active Private jobs** (jobs in Created, Pending, Queued, or Running status). The two limits are counted separately.

**Solutions**:

- Wait for currently running jobs to complete.
- Cancel pending jobs you no longer need from the portal.
- Check active jobs in the portal under Jobs, filtered by status.

------------------------------------------------------------------------

### Timeout Error

**Symptom**: `OpenQuantumDeviceError: Operation timed out after 86400s`

The job did not complete within the `job_timeout_seconds` window (default: 86400 seconds / 1 day).

**Solutions**:

- Increase the timeout if needed: `job_timeout_seconds=600` (10 minutes) or higher.
- Check the job status in the portal -- the job may still be running.
- QPU backends may have long queue times during peak usage. Consider choosing a backend with a shorter queue.

[](#__codelineno-1-1)`dev`` ``=`` ``qml``.``device``(`\
[](#__codelineno-1-2)`    ``"openquantum.device"``,`\
[](#__codelineno-1-3)`    ``wires``=``2``,`\
[](#__codelineno-1-4)`    ``shots``=``128``,`\
[](#__codelineno-1-5)`    ``backend``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-1-6)`    ``job_timeout_seconds``=``600``,``  ``# Wait up to 10 minutes`\
[](#__codelineno-1-7)`)`\

------------------------------------------------------------------------

### "shots=None is not supported"

**Symptom**: Error when creating a device with `shots=None`

Open Quantum is a shot-based execution platform. Analytic mode is not supported.

**Solution**: Always specify a positive integer for `shots`:

[](#__codelineno-2-1)`# Incorrect`\
[](#__codelineno-2-2)`dev`` ``=`` ``qml``.``device``(``"openquantum.device"``,`` ``wires``=``2``,`` ``shots``=``None``,`` ``backend``=``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-2-3)\
[](#__codelineno-2-4)`# Correct`\
[](#__codelineno-2-5)`dev`` ``=`` ``qml``.``device``(``"openquantum.device"``,`` ``wires``=``2``,`` ``shots``=``128``,`` ``backend``=``"rigetti:cepheus-1-108q"``)`\

------------------------------------------------------------------------

### QASM Validation Errors

**Symptom**: Job preparation fails with a validation error message.

**Common causes**:

- **Unsupported gate**: The circuit uses a gate that cannot be decomposed into the supported gate set. Check [Supported Operations](https://docs.openquantum.com/pennylane-plugin/supported-operations/).
- **Too many qubits**: The circuit uses more qubits than the backend supports. Check the backend's `max_qubits` constraint.
- **Empty circuit**: The circuit has no operations.

Tip

PennyLane automatically decomposes unsupported gates into supported ones. If you still get a QASM error, the gate may not have a valid decomposition path to the supported set.

------------------------------------------------------------------------

### Connection Errors

**Symptom**: `OpenQuantumDeviceError` or connection error when attempting to authenticate.

**Solutions**:

- Check your internet connection.
- Verify that `https://www.openquantum.com` is accessible from your network.
- If you are behind a corporate firewall or proxy, configure your environment accordingly.

## Debugging Tips

### Enable the PennyLane Tracker

Use PennyLane's device tracker to monitor circuit executions:

[](#__codelineno-3-1)`dev`` ``=`` ``qml``.``device``(``"openquantum.device"``,`` ``wires``=``2``,`` ``shots``=``128``,`` ``backend``=``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-3-2)\
[](#__codelineno-3-3)`@qml``.``qnode``(``dev``)`\
[](#__codelineno-3-4)`def`` ``circuit``():`\
[](#__codelineno-3-5)`    ``qml``.``Hadamard``(``wires``=``0``)`\
[](#__codelineno-3-6)`    ``qml``.``CNOT``(``wires``=``[``0``,`` ``1``])`\
[](#__codelineno-3-7)`    ``return`` ``qml``.``counts``()`\
[](#__codelineno-3-8)\
[](#__codelineno-3-9)`with`` ``qml``.``Tracker``(``dev``)`` ``as`` ``tracker``:`\
[](#__codelineno-3-10)`    ``result`` ``=`` ``circuit``()`\
[](#__codelineno-3-11)\
[](#__codelineno-3-12)`print``(``f``"Executions: ``{``tracker``.``totals``[``'executions'``]``}``"``)`\
[](#__codelineno-3-13)`print``(``f``"Shots: ``{``tracker``.``totals``[``'shots'``]``}``"``)`\

### Check Job Status in the Portal

If a job seems stuck or fails unexpectedly:

1.  Log in to the [Open Quantum Portal](https://www.openquantum.com).
2.  Navigate to **Jobs**.
3.  Find your job by timestamp or filter by status.
4.  Check the job's status and any error messages.

### Verify QASM Output

To inspect the QASM that the plugin generates, you can serialize a tape manually:

[](#__codelineno-4-1)`import`` ``pennylane`` ``as`` ``qml`\
[](#__codelineno-4-2)`from`` ``pennylane_openquantum.qasm_serializer`` ``import`` ``circuit_to_qasm`\
[](#__codelineno-4-3)\
[](#__codelineno-4-4)`with`` ``qml``.``tape``.``QuantumTape``()`` ``as`` ``tape``:`\
[](#__codelineno-4-5)`    ``qml``.``Hadamard``(``wires``=``0``)`\
[](#__codelineno-4-6)`    ``qml``.``CNOT``(``wires``=``[``0``,`` ``1``])`\
[](#__codelineno-4-7)\
[](#__codelineno-4-8)`qasm`` ``=`` ``circuit_to_qasm``(``tape``,`` ``num_wires``=``2``)`\
[](#__codelineno-4-9)`print``(``qasm``)`\

Expected output:

[](#__codelineno-5-1)`OPENQASM 2.0;`\
[](#__codelineno-5-2)`include "qelib1.inc";`\
[](#__codelineno-5-3)`qreg q[2];`\
[](#__codelineno-5-4)`creg c[2];`\
[](#__codelineno-5-5)`h q[0];`\
[](#__codelineno-5-6)`cx q[0],q[1];`\
[](#__codelineno-5-7)`measure q[0] -> c[0];`\
[](#__codelineno-5-8)`measure q[1] -> c[1];`\

## Getting Help

If you cannot resolve your issue, contact <support@openquantum.com> and include:

- The full error message and traceback.
- Your Python and PennyLane versions.
- A minimal code example that reproduces the issue.
- The backend you are using.
