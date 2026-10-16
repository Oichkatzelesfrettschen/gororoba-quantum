> Full piece: [https://www.quantum-inspire.com/release-notes-old/](https://www.quantum-inspire.com/release-notes-old/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 68f45fbf08f897d63ee5c74bc79e9f78d17e377420b587e3e7e0561514034790.

# Release notes (Quantum Inspire 1.0)

# Scheduled maintenance

A regular maintenance window is scheduled for **every Wednesday between 08:00 and 12:00 CET** to roll-out updates on our software that may require a restart of part or all of the Quantum Inspire platform. This may result in delay or failure when interacting with the site, both via the web interface or via the SDK. We always try to limit the effect for the users but be aware that any submitted jobs during this period may fail because of these updates.

# SDK release notes

Starting from version 1.5.0, Quantum Inpsire SDK release notes are no longer tracked here, but can be found on the [SDK Releases page](https://github.com/QuTech-Delft/quantuminspire/releases).

## 2021-05-26

### New features

- Added range expressions for multi-qubit gates. As an example: cnot q\[0:2\],q\[3,4,6\] is a valid construct for { cnot q\[0\],q\[3\] \| cnot q\[1\],q\[4\] \| cnot q\[2\],q\[6\] }
- Implemented binary-controlled multi-qubit gates and binary-controlled parametrized gates, such as c-Rx b\[1\],q\[2\],1.12

### New emulator platform

- We have installed the QX emulator on Lisa, a powerful HPC system at Surf.

### Accounts

- Password validation issue fix
- Password field errors are shown
- Login email is now case-insensitive

### cQASM

- When using the `not` statement with Single Gate Multiple Qubit syntax (SGMQ syntax) to negate multiple bits in the classical register, only the first specified bit was flipped. This has been fixed.

### SDK feature release 1.4.0

- See <https://github.com/QuTech-Delft/quantuminspire/releases/tag/1.4.0>
- Notebook update for Qiskit Terra 0.17.3
- Read the docs added
- Quantum Inspire project name support for Qiskit projects, see [SDK readme](https://github.com/QuTech-Delft/quantuminspire/#readme)
- qi_job.result() now has a parameter to only fetch the results for the latest run (instead ALL results for the project)
- Added SAT example to docs

### WEB GUI

- Loading of external code into editor from knowledge base only for valid code
- Pop-up no longer shows warning about optimization for execution on hardware back-ends
- Cancelled jobs show no longer as done but as cancelled
- Gate circuits can be exported from the results or editor window to a .png file
- The results tab shows the calibration data of the chip as it was during the execution of the algorithm
- Minor fixes (Back-end types order, temperature notation, broken links)
- Icons for binary-controlled operations adapted for binary-controlled multi-qubit gates
- Prep has been removed from the list of operations
- cQASm parsing errors fixed
- Result calibration data can be viewed when back-end is offline
- New projects start with max number of qubits for hardware back-ends
- Status of back-ends is shown on landing page
- Operations tab shows which operations can be used on the selected back-end
- Cookie statement added

### Website and knowledge base

- Added some examples of the use of Quantum Inspire for Quantum Computing use cases on <https://www.quantum-inspire.com/reference/>
- The code examples on our knowledge base now also indicate on which back-end the code can be executed
- Open in editor link opens a new browser tab
- Fixed some broken links
- Sticky menu

## 2020-07-31

### Starmon-5 QPU

- Added arbitrary single-qubit rotations around all 3 axes Rx(angle), Ry(angle)and Rz(angle)
- Added measure, measure_x, measure_y and measure_zto the allowed gates, for measuring single qubits in different measurement bases
- Increased maximum number of shots to 16384 (default 8192)
- Improved the two-qubit gate time from 80 ns to 60 ns
- Improved the average single-qubit gate fidelity to 99.9%
- Improved the average two-qubit gate fidelity to 97.2%
- Improved the average initialization-readout fidelity to 97.1%
- Added binning of results in histogram when measuring less then than maximum number of qubits

### Knowledge base

- Added some examples of the use of Quantum Inspire for Quantum Computing use cases on <https://www.quantum-inspire.com/reference/>
- The code examples on our knowledge base now also indicate on which backend the code can be executed

## 2020-05-15

### SDK Feature release 1.2.0:

- Support for latest Qiskit and ProjectQ versions
- full_state_projection for API-calls execute_qasm and execute_qasm_async defaults to False instead of True
- Some minor changes for supporting hardware backends

### WEB FE/API Feature release 1.0.0

- blocking run when offline
- default number of shots increased to 4096 for hardware
- number of shots now comes from previous job if applicable
- add option to switch backend in the editor
- add polling for job results every 30 seconds
- add backend name with qubits and restyled run experiment
- load external code into editor from knowledge base
- Results list pagination
- next & prev buttons in knowledge base
- local time in new project name
- set default number of shots to for all backends
- do a code check when changing backends
- accepting optional whitespace before init and subcircuit statements
- Improved editor launch
- disable run button on save
- removed errorModels from new project template

## 2019-07-10

### New features and user experience improvements

- front-end:
  - Remove optimised label from hardware results
  - Make hardware button disabled in run dialog for simulation-only projects
  - Reload backend info whenever backend tab is opened in editor
  - Result page shows backend parameters
  - Pre-flight check in run dialog to determine whether user can run algorithm for selected backend
  - Tab shows information on backend status
  - Result page shows indication for hardware projects
  - Decorate project list with metadata about projects (last saved, number of results)
  - Modals (error pop-ups etc) are now scrollable
  - Dark header in editor
  - Projects can now be deleted and renamed
  - Results can now be deleted and renamed
  - Projects can now be sorted on last saved, created or alphabetically
  - Projects can be searched
  - Project list is split into pages, instead of showing just one long list
  - Password can now be changed from account page
  - Result page shows whether optimization was used
  - Result list is split in pending and completed jobs
  - It is now possible to delete your account permanently
  - The login screen shows a spinner while it is authenticating
  - Tabs in editor now are sticky, instead of scrolling with the content

### Bug fixes

- Front-end:
  - Visualisation of parallel gates within sub-circuits now works correctly
  - Typo in email verification fixed
  - Terms of service links now scroll to the relevant section
  - Clicking on the logo in edge now goes to the home page
  - A syntax error in the last line in the editor is now shown correctly
  - An error is now shown when email verification fails
  - Don't render emojis for external link icon
  - Fix histogram hover in edge 15/16

### Miscellaneous

- Remove storybook from build to prevent netlify timeouts
- Updated npm packages

## 2019-05-15

### New features

- Front-end:

  - When using many qubits, the labels in the histogram will now be truncated instead of overlapping (moving over the label reveals the full state bitstring) to improve readability

- API:

  - On [your account page](https://www.quantum-inspire.com/account) you can generate your API token to authenticate the Software Development Kit (SDK) to your Quantum Inspire account

### Bug fixes

- Front-end:
  - Fix password errors not shown on password reset and registration forms
  - The cancel button in the 'run experiment' dialog now works correctly
  - No longer show "related" videos after playing youtube videos

## 2019-05-01

**Note:** we had to roll back these changes due to issues with Edge and Internet Explorer browsers - we're working hard to get these changes back as soon as possible. Apologies for the inconvenience.

### Bug fixes

- Front-end:
  - Fix password errors not shown on password reset and registration forms
  - Fix for overlapping histogram labels when using many qubits
  - Fix for overlap of parallel multi-qubit gates in visualisation
  - Fix issue with cancel button in run experiment dialog
  - No longer show "related" videos after playing youtube videos

## 2019-03-28

### Bug fixes

- API:
  - Make groups view read-only
  - Deny access to sensitive endpoints for API token
  - Filter userlist in users list endpoint

## 2019-03-13 Release

### New features

- Backend now supports API token authentication
- New SDK version 0.5.0:
  - Project deletion now works as documented, when giving a project name the project is not deleted after execution, when not giving a name the project is deleted automatically
  - Various improvements to the Qiskit backend:
    - Arbitrary rotation gates x, y and z now supported
    - Re-use of classical qubits now possible

### Bug fixes

- Migrated to different database to fix deadlock errors when submitting or deleting jobs

## 2019-01-16 Release

### New features/updates

- New SDK version 0.4.2:
  - Qiskit support updated to new Qiskit 0.7.0 version Quantum Inspire SDK backends now also available from PyPI (`pip install quantuminspire`).

### Content

- Fixed a number of typo’s, broken links and grammar on our website and improved the contents of our website based on your feedback.

## 2018-12-17 Release

### New features/updates

- Refactored the Qiskit backend to conform to the 0.6.x interface.
- Added support for asynchronous jobs in the API wrapper.
- Increased cqasm size limit to 1MB to support larger algorithms.

### Bug fixes

- Fixed some broken links in the knowledge base.
- Bug fix in ProjectQ backend: The order of measurement bits was random/incorrect. This has been fixed.
- Bug fix in ProjectQ backend: The get_probabilities method would return too many bits and in the incorrect order when called with a subset of the quantum register.
- Bug fix in QX simulator: QX was returning an error message when integers were passed where a float was expected.

### New content

- A [page on error models](https://www.quantum-inspire.com/kbase/cqasm-error-models) has been added to the knowledge base.
- A [code example on the quantum full adder has been added](https://www.quantum-inspire.com/kbase/full-adder).

## 2018-11-06 Release

### Bug fixes

- Occasionaly the simulator returned PthreadMutexLock error which forced the user to re-run the simulation. This has been fixed.

## 2018-09-24 Release

### New features

- The list of gate operations in the editor now has a *copy to clipboard* functionality that copies an operation to the clipboard for immediate use in the editor.

### Bug fixes

- For optimized simulations with more than 18 qubits the error `IndexError: list index out of range` was returned. This has been fixed

- On the QX single-node simulator SurfSara backend the simulation optimization mode was used for all algorithms. This has been fixed.

- Using an error model returned an error message `No measure subcircuit provided.` This has been fixed.

### New content

- An [example repetition code](https://www.quantum-inspire.com/kbase/repetition-code) has been added to the list of examples.

## 2018-09-04 Release

First public release.
