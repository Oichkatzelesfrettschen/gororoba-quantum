> Full piece: [https://www.quantum-inspire.com/kbase/displaying-and-downloading-your-results/](https://www.quantum-inspire.com/kbase/displaying-and-downloading-your-results/)
> Retrieved 2026-10-16T22:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 bb4133c1e605efe376ae36f822b99741269a1a37eeca3a6947b2182f560c932b.

# Displaying and downloading your results

THIS PAGE IS OUTDATED

## Introduction

When you execute a quantum algorithm and examine the results (which are shown in a histogram) it is important to understand a few basic things:

- [Superposition and entanglement](https://www.quantum-inspire.com/kbase/superposition-and-entanglement/) influence the possible outcomes of a quantum measurement
- [Qubits can be measured in different bases and the measurement basis influences the outcome of a measurement](https://www.quantum-inspire.com/kbase/qubit-basis-states/)
- When using an emulator backend, Quantum Inspire makes a difference between [deterministic and non-deterministic algorithms which determines the way your algorithm will be executed](https://www.quantum-inspire.com/kbase/optimization-of-simulations/)
- [A bit register](https://www.quantum-inspire.com/kbase/binary-register/) is used to store the outcome of the measurement results. The resulting histogram shows the state of the bit register.

## Selecting a result

In [the editor](https://www.quantum-inspire.com/kbase/working-with-the-editor/), click on the 'Results' tab at the top. It will show a list of all executions of your algorithm. Of course, if you have never [executed the algorithm](https://www.quantum-inspire.com/kbase/executing-your-algorithm/), the list will be empty.

You can click on any of the rows that shows 'Done' (as opposed to 'Scheduled' or 'Running') to view the results.

A few notes on the status of results:

- The status of the execution is automatically refreshed in your web browser every 30 seconds. On most browsers clicking F5 will actively refresh your browser and results status.
- Including overhead (due to compilation, uploading pulses to control hadrware etc.) a typical job on a hardware backend takes 30 to 90 seconds. There may be other jobs before you in the queue which will add to the waiting time.
- The results tab shows the execution time of the job. This is the net time for the job (consisting of N runs) to be executed on the chip, including the time for the measurements of each run. The time varies between the different backends and is determined by the duration of each single and two-qubit operation, the duration of each qubit measurement and the duration of the re-initialization of the chip between runs.
- Hardware backends require regular tuning to maintain their optimum performance. The Spin-2 backend comes with an extensive automated tuning program that takes from a few seconds to 30 minutes long. When your job is scheduled while tuning is ongoing, this will add to your waiting time.

## Understanding the histogram

In addition to showing your algorithm code and visualization, the result page shows a histogram.

In essence, what the histogram shows is the probability of the outcome of a state measurement at the end of the algorithm. To interpret this histogram, you should be aware of two things:

- The labels on the x-axis show the value of the [binary register](https://www.quantum-inspire.com/kbase/binary-register/), and the bits are ordered such that the *most significant* bit is the *leftmost* bit and the *least significant* bit is the *rightmost* bit. In other words, the measurement for qubit 0 is in the rightmost bit, the measurement for qubit 3 is in the 3th bit from the right;
- There are three different modes in which simulations can run; each mode implements a different way of obtaining the data that generates the histogram.

The different modes are explained in detail below.

### Deterministic algorithms using a single shot (N=1)

If the algorithm is deterministic, it can be executed with simulation optimization.

When this mode is running with a single shot (number of shots is 1), the histogram data will contain the probability amplitude values of the final state in the computational z-basis. The histogram will be determined directly from the final state probability amplitudes. In this case the raw data file will only contain one entry, which is the same as the histogram data.

### Deterministic algorithms with multiple shots (N\>1)

When executing with simulation optimization and more than one shot, the histogram will be determined using a Monte Carlo simulation, based on the probability amplitudes of the final state. More information on the exact steps is given in the page on [simulation optimization](https://www.quantum-inspire.com/kbase/optimization-of-simulations/).

### Non-deterministic algorithms

When running a *non-deterministic algorithm on the emulator*, or when running an *algorithm on actual hardware*, the result is obtained by executing the algorithm multiple times (multiple number of shots) and reading out the binary measurement register. The histogram reflects the observed frequency of distinct measurement register values.

### Binning

Note that the bit register is always initialized to zeroes, so when no measurement result is assigned to a bit register, the corresponding bit in the bit register will be zero. Let's look at an example where we execute a 2-qubit algorithm, but we only measure the first qubit. Let's execute 1024 shots and see what happens on the different backends.

Close

## Export visualization

File format SVG PNG

Layout Horizontal Vertical

Theme Light Dark

Download

Export

- For *emulator* backends, the second bit in the measurement register (most significant bit) will remain zero and the results returned will look something like this. The states 10 and 11 have zero results and only the two output states are shown.

0.483

0

0.517

1

1.0

0.8

0.6

0.4

0.2

0.0

- On hardware backends we always physically measure all qubits, even if the user requests to only measure one qubit. The user has an option to measure only one qubit like in the example above. Since both qubits are measured, the measurement register will have results for all four states (00, 01, 10, 11). The control software will add the output results of 00 and 10 and bin it in the 00 state and it will add the output results of 01 and 11 and bin it in the 01 state, to reflect that just one qubit was measured, and the output will look similar as for the emulator (showing two states).

## Downloading results files

The result page offers links that download the histogram data and other data as a csv (comma-separated values) file for importing the data into a spreadsheet or as a json file for structured processing by other software.

The download links available are for:

- histogram data; a list of the bins in the histogram and their probabilities;
- raw data; a list of all observed measurement outcomes or states (empty when simulation optimization with 1 shot is executed);

Note that when you measure only a subset of qubits, the web interface will show the binned values, but the data file that you download will contain the non-binned values.

## Histogram data syntax

The histogram data is given as a table of decimal values for the measurement register and the normalized frequency of observing that value over all shots (non-observed values are omitted from the table). Example:

0.010

000

0.008

001

0.008

010

0.008

011

0.012

100

0.008

101

0.939

110

0.008

111

1.0

0.8

0.6

0.4

0.2

0.0

## Raw data syntax

The raw data is a list of integers, each integer being the decimal representation of the value of the measurement register at the end of each shot. Example:

[Previous](https://www.quantum-inspire.com/kbase/executing-your-algorithm/) [Next](https://www.quantum-inspire.com/kbase/managing-your-account/)
