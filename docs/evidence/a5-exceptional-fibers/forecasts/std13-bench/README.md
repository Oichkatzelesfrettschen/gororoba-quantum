# Singular speed: std(J + m^13) on the workstation and an Azure FX4

[std13.sing](std13.sing) computes std(J + m^13) for the E8-bar -> N- header at p = 32009 (standard basis of 6,739
elements in every run). [bench.sh](bench.sh) ran Ubuntu's Singular 4.3.2 and the passagemath 4.4.1 build side by side on
an Azure Standard_FX4mds_v2; the workstation ran the same script once.

| host and build | milliseconds |
|---|---|
| workstation (laptop), build not recorded in the file | 1,100,108 ([laptop.txt](laptop.txt)) |
| Azure FX4mds_v2, passagemath Singular 4.4.1 | 1,792,470 ([azure.txt](azure.txt)) |
| Azure FX4mds_v2, Ubuntu Singular 4.3.2 | 2,787,152 ([azure.txt](azure.txt)) |

On this one computation the FX4 with passagemath 4.4.1 ran 1.63 times slower than the workstation, and passagemath
4.4.1 ran 1.55 times faster than Ubuntu 4.3.2 on the same VM. The two Azure builds ran concurrently on the VM's four
vCPUs. Each Singular process is single-threaded and had a vCPU to itself, but the two shared memory bandwidth and
cache, so 1.63 is an upper estimate of a solo FX4 run; a passagemath run alone on an FX4 decides it. No Kaggle timing
of the same script exists.
