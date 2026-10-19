> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.station_control.v2.task_service_pb2.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.station_control.v2.task_service_pb2.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8d06d3efebc06fc926273b750c48d05e34d380dc766060e93daed771f2d73fd4.

# task_service_pb2

Generated protocol buffer code.

Full path: iqm.data_definitions.station_control.v2.task_service_pb2

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
 Station Task definition.
 */

syntax = "proto3";

package iqm.data_definitions.station_control.v2;

import "iqm/data_definitions/common/v1/data_types.proto";


// Response body for GET /sweeps/{uuid}/results
message SweepResultsResponse
{
  // A UUID that gives identity to the sweep event.
  string sweep_id = 1;
  /* Maps the names of SweepRequest.return_parameters to corresponding list of results arrays.
  The length of the list is equal to the total number of sweep spots -
  each item in the list contains the full results for one sweep spot,
  and they appear in the order dictated by sweep linearization convention.
   */
  map<string, iqm.data_definitions.common.v1.Arrays> results = 2;
}


message SweepResultsChunk {
  // A UUID that gives identity to the sweep event.
  string sweep_id = 1;
  // Zero-based sweep spot index in sweep linearization order.
  uint64 spot_idx = 2;
  // Name of the return parameter this chunk contains data for.
  string return_parameter = 3;
  // Encoded spot-result payload for one return parameter at one sweep spot.
  bytes encoded_value = 4;
}
```

Classes

|  |  |
|----|----|
| [`SweepResultsChunk`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.station_control.v2.task_service_pb2.SweepResultsChunk.html#iqm.data_definitions.station_control.v2.task_service_pb2.SweepResultsChunk "iqm.data_definitions.station_control.v2.task_service_pb2.SweepResultsChunk") |  |
| [`SweepResultsResponse`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.station_control.v2.task_service_pb2.SweepResultsResponse.html#iqm.data_definitions.station_control.v2.task_service_pb2.SweepResultsResponse "iqm.data_definitions.station_control.v2.task_service_pb2.SweepResultsResponse") |  |
