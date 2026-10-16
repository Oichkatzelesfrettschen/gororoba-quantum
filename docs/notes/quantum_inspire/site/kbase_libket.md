> Full piece: [https://www.quantum-inspire.com/kbase/libket/](https://www.quantum-inspire.com/kbase/libket/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 96c9d88abc2aa71465f5d847395ee96f84f5a9eef92aa765a785ee475beb8bd9.

# LibKet

# LibKet - Kwantum Expression Template Library

The open-source expression template library [LibKet](https://gitlab.com/mmoelle1/LibKet) makes it possible to develop quantum-accelerated scientific applications and test them on different gate-based quantum computing platforms like Quantum Inspire, [IBM's Quantum Experience](https://www.ibm.com/quantum-computing/) and [Rigetti's Quantum Cloud Services](https://qcs.rigetti.com/request-access) without the need to reimplement quantum algorithms in vendor-specific SDKs like [Qiskit](https://qiskit.org/) and [PyQuil](https://github.com/rigetti/pyquil). LibKet is designed as C++14 expression template library that allows to formulate quantum algorithms as generic expressions, which are synthesized to backend-optimized quantum kernels that can be executed in quantum simulators and cloud-based quantum computers. Next to the basic quantum gates, LibKet comes with a growing collection of customizable quantum algorithms and building blocks like the Quantum Fourier transformation that simplify the development of quantum-accelerated applications.

The following code snippet shows how to generate the quantum kernel for an n-qubit QFT and execute it first on the Quantum Inspire simulator platform using 6-qubits and then on IBM's Quantum Experience cloud service using one of the 5-qubit quantum processors. Beneath it the generated cQASM code and circuit is shown.

```clike

#include <LibKet.hpp>

using namespace LibKet;
using namespace LibKet::circuits;
using namespace LibKet::filters;
using namespace LibKet::gates;

// Create generic quantum expression
auto expr = qft(init());

// Execute QFT<6> on Quantum-Inspire platform
try {
  QDevice<QDeviceType::qi_26_simulator, 6> qi; qi(expr);
  utils::json result = qi.execute();
                      
  QInfo << result << std::endl;

  QInfo << "job ID     : " << qi.get<QResultType::id>(result)               << std::endl;
  QInfo << "time stamp : " << qi.get<QResultType::timestamp>(result)        << std::endl;
  QInfo << "duration   : " << qi.get<QResultType::duration>(result).count() << std::endl;
  QInfo << "best       : " << qi.get<QResultType::best>(result)             << std::endl;
  QInfo << "histogram  : " << qi.get<QResultType::histogram>(result)        << std::endl;
                                         
} catch(const std::exception &e) {
  QWarn << e.what() << std::endl;
}

// Execute QFT<5> on IBM Quantum Experience platform
try {
  QDevice<QDeviceType::ibmq_5_london, 5> ibmq; ibmq(expr);
  utils::json result = ibmq.execute();
                       
  QInfo << result << std::endl;

  QInfo << "job ID     : " << qi.get<QResultType::id>(result)               << std::endl;
  QInfo << "time stamp : " << qi.get<QResultType::timestamp>(result)        << std::endl;
  QInfo << "duration   : " << qi.get<QResultType::duration>(result).count() << std::endl;
  QInfo << "best       : " << qi.get<QResultType::best>(result)             << std::endl;
  QInfo << "histogram  : " << qi.get<QResultType::histogram>(result)        << std::endl;
                                                                                                                                           
} catch(const std::exception &e) {
  QWarn << e.what() << std::endl;
}
```

```cqasm
version 3.0

qubit[6] q
bit[6] b

H q[0]
CR(1.570796326794896558) q[1], q[0]
CR(0.785398163397448279) q[2], q[0]
CR(0.392699081698724139) q[3], q[0]
CR(0.196349540849362070) q[4], q[0]
CR(0.098174770424681035) q[5], q[0]
H q[1]
CR(1.570796326794896558) q[2], q[1]
CR(0.785398163397448279) q[3], q[1]
CR(0.392699081698724139) q[4], q[1]
CR(0.196349540849362070) q[5], q[1]
H q[2]
CR(1.570796326794896558) q[3], q[2]
CR(0.785398163397448279) q[4], q[2]
CR(0.392699081698724139) q[5], q[2]
H q[3]
CR(1.570796326794896558) q[4], q[3]
CR(0.785398163397448279) q[5], q[3]
H q[4]
CR(1.570796326794896558) q[5], q[4]
H q[5]
SWAP q[0], q[5]
SWAP q[1], q[4]
SWAP q[2], q[3]

b[0:5] = measure q[0:5]
```

[Previous](https://www.quantum-inspire.com/kbase/low-level-api/) [Next](https://www.quantum-inspire.com/kbase/deutsch-jozsa-algorithm/)
