> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.parameter_pb2.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.parameter_pb2.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cbc246b4dac08ee34d298d0f668e41fb6b002c67f4fee9a410f562a0ed12f7e4.

# parameter_pb2

Generated protocol buffer code.

Full path: iqm.data_definitions.common.v1.parameter_pb2

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
 Protobuf message definitions for generic parameters.
*/

syntax = "proto3";

package iqm.data_definitions.common.v1;


// Station Control parameter
message Parameter {
  // Collection type
  enum CollectionType {
    COLLECTION_TYPE_UNSPECIFIED = 0;
    COLLECTION_TYPE_SCALAR = 1;
    COLLECTION_TYPE_SEQUENCE = 2;
    COLLECTION_TYPE_ARRAY = 3;
  }

  // Collection type
  enum DataType {
    DATA_TYPE_UNSPECIFIED = 0;
    DATA_TYPE_STRING = 1;
    DATA_TYPE_BOOL = 2;
    DATA_TYPE_INT64 = 3;
    DATA_TYPE_FLOAT64 = 4;
    DATA_TYPE_COMPLEX128 = 5;
  }

  // parameter name
  string name = 1;
  // human-readable label
  string label = 2;
  // SI unit
  string unit = 3;
  CollectionType collection_type = 4;
  DataType data_type = 5;
  repeated int64 element_indices = 6;
  string parent_name = 7;
  string parent_label = 8;
}
```

Classes

|  |  |
|----|----|
| [`Parameter`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.parameter_pb2.Parameter.html#iqm.data_definitions.common.v1.parameter_pb2.Parameter "iqm.data_definitions.common.v1.parameter_pb2.Parameter") |  |
