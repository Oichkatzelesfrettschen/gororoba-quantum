> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.observation_pb2.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.observation_pb2.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1f9bb57515ff2497a6f3263b7f9a50e84431647f4f118937accf01ff683c19e7.

# observation_pb2

Generated protocol buffer code.

Full path: iqm.data_definitions.common.v1.observation_pb2

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
 Observation value and uncertainty declarations.
 */

syntax = "proto3";

package iqm.data_definitions.common.v1;

import "iqm/data_definitions/common/v1/data_types.proto";


/*
 Represents an integer array, the dimensions of which are
 enumerated in 'shape' (think of "some_numpy_array.shape"),
 and the integers themselves are enumerated in "items"
 (think of "numpy.nditer(some_numpy_array, order='C')").
 */
message Int64Array {
  repeated int64 shape = 1 [packed = true];
  repeated int64 items = 2 [packed = true];
}


/*
 Represents a float array, the dimensions of which are
 enumerated in 'shape' (think of "some_numpy_array.shape"),
 and the integers themselves are enumerated in "items"
 (think of "numpy.nditer(some_numpy_array, order='C')").
 */
message Float64Array {
  repeated int64 shape = 1 [packed = true];
  repeated double items = 2 [packed = true];
}


/*
 Represents a complex array, the dimensions of which are
 enumerated in 'shape' (think of "some_numpy_array.shape"),
 and the integers themselves are enumerated in "items"
 (think of "numpy.nditer(some_numpy_array, order='C')").
 */
message Complex128Array {
  repeated int64 shape = 1 [packed = true];
  repeated iqm.data_definitions.common.v1.Complex128 items = 2;
}


message ObservationValue {
  oneof value {
      string str_value = 1;

      int64 int64_value = 2;
      double float64_value = 3;
      iqm.data_definitions.common.v1.Complex128 complex128_value = 4;

      Int64Array int64_array = 5;
      Float64Array float64_array = 6;
      Complex128Array complex128_array = 7;

      bytes legacy_value = 8;

      bool bool_value = 9;
      iqm.data_definitions.common.v1.Array array = 10;

  }
}


message ObservationUncertainty {
  oneof value {
      int64 int64_value = 1;
      double float64_value = 2;
      iqm.data_definitions.common.v1.Complex128 complex128_value = 3;

      Int64Array int64_array = 4;
      Float64Array float64_array = 5;
      Complex128Array complex128_array = 6;

      bytes legacy_value = 7;
  }
}
```

Classes

|  |  |
|----|----|
| [`Complex128Array`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.observation_pb2.Complex128Array.html#iqm.data_definitions.common.v1.observation_pb2.Complex128Array "iqm.data_definitions.common.v1.observation_pb2.Complex128Array") |  |
| [`Float64Array`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.observation_pb2.Float64Array.html#iqm.data_definitions.common.v1.observation_pb2.Float64Array "iqm.data_definitions.common.v1.observation_pb2.Float64Array") |  |
| [`Int64Array`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.observation_pb2.Int64Array.html#iqm.data_definitions.common.v1.observation_pb2.Int64Array "iqm.data_definitions.common.v1.observation_pb2.Int64Array") |  |
| [`ObservationUncertainty`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.observation_pb2.ObservationUncertainty.html#iqm.data_definitions.common.v1.observation_pb2.ObservationUncertainty "iqm.data_definitions.common.v1.observation_pb2.ObservationUncertainty") |  |
| [`ObservationValue`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.observation_pb2.ObservationValue.html#iqm.data_definitions.common.v1.observation_pb2.ObservationValue "iqm.data_definitions.common.v1.observation_pb2.ObservationValue") |  |
