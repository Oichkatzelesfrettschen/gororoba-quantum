> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.channel_properties_pb2.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.channel_properties_pb2.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e2102269a838cbc69f9cc9a112dc04bd1c5f983ae8f6778ba544cf8a05aa0bb2.

# channel_properties_pb2

Generated protocol buffer code.

Full path: iqm.data_definitions.common.v1.channel_properties_pb2

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
 Definition of channel properties for hw devices
 */

syntax = "proto3";

package iqm.data_definitions.common.v1;


message ChannelPropertyDictionary {
    map<string, ChannelPropertyEntry> channel_property_mapping = 1;
}

message ChannelPropertyEntry {
    oneof value {
        AWGProperties awg = 1;
        ReadoutProperties ro = 2;
    }
}

message ChannelProperties {
    // sample rate of the instrument responsible for the channel (in Hz)
    double sampling_rate = 1;
    // Unused
    double instruction_duration_granularity = 2;
    // Unused
    double instruction_duration_min = 3;
    // instruction types that are allowed on this channel
    repeated string compatible_instructions = 4;

    // all instruction durations on this channel must be multiples of this granularity (in samples) 
    uint64 instruction_duration_granularity_samples = 5;
    // all instruction durations on this channel must at least this long (in samples)
    uint64 instruction_duration_min_samples = 6;
}


message AWGProperties {
    ChannelProperties channel_properties = 1;

    // Defines compatible fast feedback sources
    repeated string fast_feedback_sources = 3;

    // Whether this AWG contains a local oscillator or not.
    bool local_oscillator = 4;

    //  Whether this AWG has mixer correction or not.
    bool mixer_correction = 5;
}


message ReadoutProperties {
    ChannelProperties channel_properties = 1;
    // Unused.
    double integration_start_dead_time = 4;
    // Unused.
    double integration_stop_dead_time = 5;
     // Dead time samples before integration 
    uint64 integration_start_dead_time_samples = 6;
    // Dead time samples after integration.
    uint64 integration_stop_dead_time_samples = 7;
}
```

Classes

|  |  |
|----|----|
| [`AWGProperties`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.channel_properties_pb2.AWGProperties.html#iqm.data_definitions.common.v1.channel_properties_pb2.AWGProperties "iqm.data_definitions.common.v1.channel_properties_pb2.AWGProperties") |  |
| [`ChannelProperties`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.channel_properties_pb2.ChannelProperties.html#iqm.data_definitions.common.v1.channel_properties_pb2.ChannelProperties "iqm.data_definitions.common.v1.channel_properties_pb2.ChannelProperties") |  |
| [`ChannelPropertyDictionary`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.channel_properties_pb2.ChannelPropertyDictionary.html#iqm.data_definitions.common.v1.channel_properties_pb2.ChannelPropertyDictionary "iqm.data_definitions.common.v1.channel_properties_pb2.ChannelPropertyDictionary") |  |
| [`ChannelPropertyEntry`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.channel_properties_pb2.ChannelPropertyEntry.html#iqm.data_definitions.common.v1.channel_properties_pb2.ChannelPropertyEntry "iqm.data_definitions.common.v1.channel_properties_pb2.ChannelPropertyEntry") |  |
| [`ReadoutProperties`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.channel_properties_pb2.ReadoutProperties.html#iqm.data_definitions.common.v1.channel_properties_pb2.ReadoutProperties "iqm.data_definitions.common.v1.channel_properties_pb2.ReadoutProperties") |  |
