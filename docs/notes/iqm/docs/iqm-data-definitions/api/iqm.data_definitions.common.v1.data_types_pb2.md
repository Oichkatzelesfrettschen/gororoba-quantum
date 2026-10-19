> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 efa93c7dc01b71bbf84c2b5a663c0dfec0416e358af30dbcffc37cfd44f439f6.

# data_types_pb2

Generated protocol buffer code.

Full path: iqm.data_definitions.common.v1.data_types_pb2

Protobuf source code

``` proto
// Copyright 2019-2025 IQM
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/*
 Protobuf message definitions for shared data types.
*/

syntax = "proto3";

package iqm.data_definitions.common.v1;

import "google/protobuf/struct.proto";

/*
  A complex number.
 */
message Complex128 {
  double real = 1;
  double imag = 2;
}

/*
 Sequence of integers.
 */
message Int64Sequence {
  repeated sint64 items = 1;
}

/*
 Sequence of doubles.
 */
message Float64Sequence {
  repeated double items = 1;
}

/*
 Sequence of booleans.
 Protobuf uses ints to encode booleans, but keeps track of the type.
 */
message BoolSequence {
  repeated bool items = 1;
}

/*
 Sequence of complex numbers.
 */
message Complex128Sequence {
  repeated double real = 1;
  repeated double imag = 2;
}

/*
 Sequence of strings.
 */
message StringSequence {
  repeated string items = 1;
}


/*
 Generic n-dimensional array, the dimensions of which are
 enumerated in 'shape' (think of "some_numpy_array.shape"),
 and the values themselves are enumerated in "items"  in big-endian order;
 the first dimension is the slowest to change
 (think of "numpy.nditer(some_numpy_array, order='C')").
 */
message Array {
  repeated uint64 shape = 1;
  oneof kind {
    StringSequence string_array = 2;
    BoolSequence bool_array = 3;
    Int64Sequence int64_array = 4;
    Float64Sequence float64_array = 5;
    Complex128Sequence complex128_array = 6;
  }
}


message Arrays {
  repeated Array arrays = 1;
}


/*
 Generic sequence.
 */
message Sequence {
  oneof kind {
    StringSequence string_array = 1;
    BoolSequence bool_array = 2;
    Int64Sequence int64_array = 3;
    Float64Sequence float64_array = 4;
    Complex128Sequence complex128_array = 5;
  }
}

/*
 A single piece of data with flexible datatype. To be used in, for example, in settings.
 */
message Datum
{
  oneof kind
  {
    string string_value = 1;
    bool bool_value = 2;
    sint64 sint64_value = 3;
    double float64_value = 4;
    Complex128 complex128_value = 5;

    Array array = 10;
    Sequence sequence = 11;

    google.protobuf.NullValue null_value = 14;
  }
}
```

Classes

|  |  |
|----|----|
| [`Array`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.Array.html#iqm.data_definitions.common.v1.data_types_pb2.Array "iqm.data_definitions.common.v1.data_types_pb2.Array") |  |
| [`Arrays`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.Arrays.html#iqm.data_definitions.common.v1.data_types_pb2.Arrays "iqm.data_definitions.common.v1.data_types_pb2.Arrays") |  |
| [`BoolSequence`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.BoolSequence.html#iqm.data_definitions.common.v1.data_types_pb2.BoolSequence "iqm.data_definitions.common.v1.data_types_pb2.BoolSequence") |  |
| [`Complex128`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.Complex128.html#iqm.data_definitions.common.v1.data_types_pb2.Complex128 "iqm.data_definitions.common.v1.data_types_pb2.Complex128") |  |
| [`Complex128Sequence`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.Complex128Sequence.html#iqm.data_definitions.common.v1.data_types_pb2.Complex128Sequence "iqm.data_definitions.common.v1.data_types_pb2.Complex128Sequence") |  |
| [`Datum`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.Datum.html#iqm.data_definitions.common.v1.data_types_pb2.Datum "iqm.data_definitions.common.v1.data_types_pb2.Datum") |  |
| [`Float64Sequence`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.Float64Sequence.html#iqm.data_definitions.common.v1.data_types_pb2.Float64Sequence "iqm.data_definitions.common.v1.data_types_pb2.Float64Sequence") |  |
| [`Int64Sequence`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.Int64Sequence.html#iqm.data_definitions.common.v1.data_types_pb2.Int64Sequence "iqm.data_definitions.common.v1.data_types_pb2.Int64Sequence") |  |
| [`Sequence`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.Sequence.html#iqm.data_definitions.common.v1.data_types_pb2.Sequence "iqm.data_definitions.common.v1.data_types_pb2.Sequence") |  |
| [`StringSequence`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.data_types_pb2.StringSequence.html#iqm.data_definitions.common.v1.data_types_pb2.StringSequence "iqm.data_definitions.common.v1.data_types_pb2.StringSequence") |  |
