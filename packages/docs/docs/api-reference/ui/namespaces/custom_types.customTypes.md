---
id: "custom_types.customTypes"
title: "Namespace: customTypes"
sidebar_label: "customTypes"
custom_edit_url: null
---

[custom-types](../modules/custom_types.md).customTypes

## Type Aliases

### OSState

Ƭ **OSState**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `cpu_usage` | `number` \| ``null`` |
| `filled_disk_space_fraction` | `number` \| ``null`` |
| `last_boot_time` | `string` \| ``null`` |
| `memory_usage` | `number` \| ``null`` |

#### Defined in

[custom-types.ts:255](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L255)

___

### activityHistory

Ƭ **activityHistory**: { `event`: ``"start-core"`` \| ``"stop-core"`` \| ``"start-measurements"`` \| ``"stop-measurements"`` \| ``"error-occured"`` \| ``"errors-resolved"`` ; `localTime`: `string`  }[]

#### Defined in

[custom-types.ts:274](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L274)

___

### config

Ƭ **config**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `camtracker` | { `config_path`: `string` ; `executable_path`: `string` ; `learn_az_elev_path`: `string` ; `motor_offset_threshold`: `number` ; `sun_intensity_path`: `string`  } |
| `camtracker.config_path` | `string` |
| `camtracker.executable_path` | `string` |
| `camtracker.learn_az_elev_path` | `string` |
| `camtracker.motor_offset_threshold` | `number` |
| `camtracker.sun_intensity_path` | `string` |
| `error_email` | { `notify_recipients`: `boolean` ; `recipients`: `string` ; `sender_address`: `string` ; `sender_password`: `string`  } |
| `error_email.notify_recipients` | `boolean` |
| `error_email.recipients` | `string` |
| `error_email.sender_address` | `string` |
| `error_email.sender_password` | `string` |
| `general` | { `min_sun_elevation`: `number` ; `seconds_per_core_interval`: `number` ; `station_id`: `string` ; `test_mode`: `boolean` ; `version`: ``"4.0.7"``  } |
| `general.min_sun_elevation` | `number` |
| `general.seconds_per_core_interval` | `number` |
| `general.station_id` | `string` |
| `general.test_mode` | `boolean` |
| `general.version` | ``"4.0.7"`` |
| `helios` | ``null`` \| { `camera_id`: `number` ; `edge_detection_threshold`: `number` ; `evaluation_size`: `number` ; `save_images`: `boolean` ; `seconds_per_interval`: `number`  } |
| `measurement_decision` | { `cli_decision_result`: `boolean` ; `manual_decision_result`: `boolean` ; `mode`: ``"automatic"`` \| ``"manual"`` \| ``"cli"``  } |
| `measurement_decision.cli_decision_result` | `boolean` |
| `measurement_decision.manual_decision_result` | `boolean` |
| `measurement_decision.mode` | ``"automatic"`` \| ``"manual"`` \| ``"cli"`` |
| `measurement_triggers` | { `consider_helios`: `boolean` ; `consider_sun_elevation`: `boolean` ; `consider_time`: `boolean` ; `min_sun_elevation`: `number` ; `start_time`: { `hour`: `number` ; `minute`: `number` ; `second`: `number`  } ; `stop_time`: { `hour`: `number` ; `minute`: `number` ; `second`: `number`  }  } |
| `measurement_triggers.consider_helios` | `boolean` |
| `measurement_triggers.consider_sun_elevation` | `boolean` |
| `measurement_triggers.consider_time` | `boolean` |
| `measurement_triggers.min_sun_elevation` | `number` |
| `measurement_triggers.start_time` | { `hour`: `number` ; `minute`: `number` ; `second`: `number`  } |
| `measurement_triggers.start_time.hour` | `number` |
| `measurement_triggers.start_time.minute` | `number` |
| `measurement_triggers.start_time.second` | `number` |
| `measurement_triggers.stop_time` | { `hour`: `number` ; `minute`: `number` ; `second`: `number`  } |
| `measurement_triggers.stop_time.hour` | `number` |
| `measurement_triggers.stop_time.minute` | `number` |
| `measurement_triggers.stop_time.second` | `number` |
| `opus` | { `em27_ip`: `string` ; `executable_path`: `string` ; `experiment_path`: `string` ; `macro_path`: `string` ; `password`: `string` ; `username`: `string`  } |
| `opus.em27_ip` | `string` |
| `opus.executable_path` | `string` |
| `opus.experiment_path` | `string` |
| `opus.macro_path` | `string` |
| `opus.password` | `string` |
| `opus.username` | `string` |
| `tum_plc` | ``null`` \| { `controlled_by_user`: `boolean` ; `ip`: `string` ; `version`: `number`  } |
| `upload` | ``null`` \| { `dst_directory_helios`: `string` ; `dst_directory_ifgs`: `string` ; `host`: `string` ; `password`: `string` ; `remove_src_helios_after_upload`: `boolean` ; `remove_src_ifgs_after_upload`: `boolean` ; `src_directory_ifgs`: `string` ; `upload_helios`: `boolean` ; `upload_ifgs`: `boolean` ; `user`: `string`  } |

#### Defined in

[custom-types.ts:40](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L40)

___

### configSectionKey

Ƭ **configSectionKey**: ``"general"`` \| ``"opus"`` \| ``"camtracker"`` \| ``"error_email"`` \| ``"measurement_triggers"`` \| ``"tum_plc"`` \| ``"helios"`` \| ``"upload"``

#### Defined in

[custom-types.ts:31](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L31)

___

### coreState

Ƭ **coreState**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `enclosure_plc_readings` | [`enclosurePlcReadings`](custom_types.customTypes.md#enclosureplcreadings) |
| `helios_indicates_good_conditions` | `boolean` \| ``null`` |
| `measurements_should_be_running` | `boolean` |
| `os_state` | [`OSState`](custom_types.customTypes.md#osstate) |

#### Defined in

[custom-types.ts:262](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L262)

___

### enclosurePlcReadings

Ƭ **enclosurePlcReadings**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `actors` | { `current_angle`: `number` \| ``null`` ; `fan_speed`: `number` \| ``null``  } |
| `actors.current_angle` | `number` \| ``null`` |
| `actors.fan_speed` | `number` \| ``null`` |
| `connections` | { `camera`: `boolean` \| ``null`` ; `computer`: `boolean` \| ``null`` ; `heater`: `boolean` \| ``null`` ; `router`: `boolean` \| ``null`` ; `spectrometer`: `boolean` \| ``null``  } |
| `connections.camera` | `boolean` \| ``null`` |
| `connections.computer` | `boolean` \| ``null`` |
| `connections.heater` | `boolean` \| ``null`` |
| `connections.router` | `boolean` \| ``null`` |
| `connections.spectrometer` | `boolean` \| ``null`` |
| `control` | { `auto_temp_mode`: `boolean` \| ``null`` ; `manual_control`: `boolean` \| ``null`` ; `manual_temp_mode`: `boolean` \| ``null`` ; `sync_to_tracker`: `boolean` \| ``null``  } |
| `control.auto_temp_mode` | `boolean` \| ``null`` |
| `control.manual_control` | `boolean` \| ``null`` |
| `control.manual_temp_mode` | `boolean` \| ``null`` |
| `control.sync_to_tracker` | `boolean` \| ``null`` |
| `last_read_time` | `string` \| ``null`` |
| `power` | { `camera`: `boolean` \| ``null`` ; `computer`: `boolean` \| ``null`` ; `heater`: `boolean` \| ``null`` ; `router`: `boolean` \| ``null`` ; `spectrometer`: `boolean` \| ``null``  } |
| `power.camera` | `boolean` \| ``null`` |
| `power.computer` | `boolean` \| ``null`` |
| `power.heater` | `boolean` \| ``null`` |
| `power.router` | `boolean` \| ``null`` |
| `power.spectrometer` | `boolean` \| ``null`` |
| `sensors` | { `humidity`: `number` \| ``null`` ; `temperature`: `number` \| ``null``  } |
| `sensors.humidity` | `number` \| ``null`` |
| `sensors.temperature` | `number` \| ``null`` |
| `state` | { `cover_closed`: `boolean` \| ``null`` ; `motor_failed`: `boolean` \| ``null`` ; `rain`: `boolean` \| ``null`` ; `reset_needed`: `boolean` \| ``null`` ; `ups_alert`: `boolean` \| ``null``  } |
| `state.cover_closed` | `boolean` \| ``null`` |
| `state.motor_failed` | `boolean` \| ``null`` |
| `state.rain` | `boolean` \| ``null`` |
| `state.reset_needed` | `boolean` \| ``null`` |
| `state.ups_alert` | `boolean` \| ``null`` |

#### Defined in

[custom-types.ts:177](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L177)

___

### intArray3

Ƭ **intArray3**: [`number`, `number`, `number`]

#### Defined in

[custom-types.ts:28](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L28)

___

### intArray4

Ƭ **intArray4**: [`number`, `number`, `number`, `number`]

#### Defined in

[custom-types.ts:29](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L29)

___

### partialConfig

Ƭ **partialConfig**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `camtracker?` | { `config_path?`: `string` ; `executable_path?`: `string` ; `learn_az_elev_path?`: `string` ; `motor_offset_threshold?`: `number` ; `sun_intensity_path?`: `string`  } |
| `camtracker.config_path?` | `string` |
| `camtracker.executable_path?` | `string` |
| `camtracker.learn_az_elev_path?` | `string` |
| `camtracker.motor_offset_threshold?` | `number` |
| `camtracker.sun_intensity_path?` | `string` |
| `error_email?` | { `notify_recipients?`: `boolean` ; `recipients?`: `string` ; `sender_address?`: `string` ; `sender_password?`: `string`  } |
| `error_email.notify_recipients?` | `boolean` |
| `error_email.recipients?` | `string` |
| `error_email.sender_address?` | `string` |
| `error_email.sender_password?` | `string` |
| `general?` | { `min_sun_elevation?`: `number` ; `seconds_per_core_interval?`: `number` ; `station_id?`: `string` ; `test_mode?`: `boolean` ; `version?`: ``"4.0.7"``  } |
| `general.min_sun_elevation?` | `number` |
| `general.seconds_per_core_interval?` | `number` |
| `general.station_id?` | `string` |
| `general.test_mode?` | `boolean` |
| `general.version?` | ``"4.0.7"`` |
| `helios?` | ``null`` \| { `camera_id?`: `number` ; `edge_detection_threshold?`: `number` ; `evaluation_size?`: `number` ; `save_images?`: `boolean` ; `seconds_per_interval?`: `number`  } |
| `measurement_decision?` | { `cli_decision_result?`: `boolean` ; `manual_decision_result?`: `boolean` ; `mode?`: ``"automatic"`` \| ``"manual"`` \| ``"cli"``  } |
| `measurement_decision.cli_decision_result?` | `boolean` |
| `measurement_decision.manual_decision_result?` | `boolean` |
| `measurement_decision.mode?` | ``"automatic"`` \| ``"manual"`` \| ``"cli"`` |
| `measurement_triggers?` | { `consider_helios?`: `boolean` ; `consider_sun_elevation?`: `boolean` ; `consider_time?`: `boolean` ; `min_sun_elevation?`: `number` ; `start_time?`: { `hour?`: `number` ; `minute?`: `number` ; `second?`: `number`  } ; `stop_time?`: { `hour?`: `number` ; `minute?`: `number` ; `second?`: `number`  }  } |
| `measurement_triggers.consider_helios?` | `boolean` |
| `measurement_triggers.consider_sun_elevation?` | `boolean` |
| `measurement_triggers.consider_time?` | `boolean` |
| `measurement_triggers.min_sun_elevation?` | `number` |
| `measurement_triggers.start_time?` | { `hour?`: `number` ; `minute?`: `number` ; `second?`: `number`  } |
| `measurement_triggers.start_time.hour?` | `number` |
| `measurement_triggers.start_time.minute?` | `number` |
| `measurement_triggers.start_time.second?` | `number` |
| `measurement_triggers.stop_time?` | { `hour?`: `number` ; `minute?`: `number` ; `second?`: `number`  } |
| `measurement_triggers.stop_time.hour?` | `number` |
| `measurement_triggers.stop_time.minute?` | `number` |
| `measurement_triggers.stop_time.second?` | `number` |
| `opus?` | { `em27_ip?`: `string` ; `executable_path?`: `string` ; `experiment_path?`: `string` ; `macro_path?`: `string` ; `password?`: `string` ; `username?`: `string`  } |
| `opus.em27_ip?` | `string` |
| `opus.executable_path?` | `string` |
| `opus.experiment_path?` | `string` |
| `opus.macro_path?` | `string` |
| `opus.password?` | `string` |
| `opus.username?` | `string` |
| `tum_plc?` | ``null`` \| { `controlled_by_user?`: `boolean` ; `ip?`: `string` ; `version?`: `number`  } |
| `upload?` | ``null`` \| { `dst_directory_helios?`: `string` ; `dst_directory_ifgs?`: `string` ; `host?`: `string` ; `password?`: `string` ; `remove_src_helios_after_upload?`: `boolean` ; `remove_src_ifgs_after_upload?`: `boolean` ; `src_directory_ifgs?`: `string` ; `upload_helios?`: `boolean` ; `upload_ifgs?`: `boolean` ; `user?`: `string`  } |

#### Defined in

[custom-types.ts:109](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L109)

___

### partialCoreState

Ƭ **partialCoreState**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `enclosure_plc_readings?` | [`partialEnclosurePlcReadings`](custom_types.customTypes.md#partialenclosureplcreadings) |
| `measurements_should_be_running?` | `boolean` |

#### Defined in

[custom-types.ts:269](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L269)

___

### partialEnclosurePlcReadings

Ƭ **partialEnclosurePlcReadings**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `actors?` | { `current_angle?`: `number` ; `fan_speed?`: `number`  } |
| `actors.current_angle?` | `number` |
| `actors.fan_speed?` | `number` |
| `connections?` | { `camera?`: `boolean` ; `computer?`: `boolean` ; `heater?`: `boolean` ; `router?`: `boolean` ; `spectrometer?`: `boolean`  } |
| `connections.camera?` | `boolean` |
| `connections.computer?` | `boolean` |
| `connections.heater?` | `boolean` |
| `connections.router?` | `boolean` |
| `connections.spectrometer?` | `boolean` |
| `control?` | { `auto_temp_mode?`: `boolean` ; `manual_control?`: `boolean` ; `manual_temp_mode?`: `boolean` ; `sync_to_tracker?`: `boolean`  } |
| `control.auto_temp_mode?` | `boolean` |
| `control.manual_control?` | `boolean` |
| `control.manual_temp_mode?` | `boolean` |
| `control.sync_to_tracker?` | `boolean` |
| `last_read_time?` | `string` |
| `power?` | { `camera?`: `boolean` ; `computer?`: `boolean` ; `heater?`: `boolean` ; `router?`: `boolean` ; `spectrometer?`: `boolean`  } |
| `power.camera?` | `boolean` |
| `power.computer?` | `boolean` |
| `power.heater?` | `boolean` |
| `power.router?` | `boolean` |
| `power.spectrometer?` | `boolean` |
| `sensors?` | { `humidity?`: `number` ; `temperature?`: `number`  } |
| `sensors.humidity?` | `number` |
| `sensors.temperature?` | `number` |
| `state?` | { `cover_closed?`: `boolean` ; `motor_failed?`: `boolean` ; `rain?`: `boolean` ; `reset_needed?`: `boolean` ; `ups_alert?`: `boolean`  } |
| `state.cover_closed?` | `boolean` |
| `state.motor_failed?` | `boolean` |
| `state.rain?` | `boolean` |
| `state.reset_needed?` | `boolean` |
| `state.ups_alert?` | `boolean` |

#### Defined in

[custom-types.ts:216](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L216)

___

### reduxState

Ƭ **reduxState**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `activity` | [`reduxStateActivity`](custom_types.customTypes.md#reduxstateactivity) |
| `config` | [`reduxStateConfig`](custom_types.customTypes.md#reduxstateconfig) |
| `coreProcess` | [`reduxStateCoreProcess`](custom_types.customTypes.md#reduxstatecoreprocess) |
| `coreState` | [`reduxStateCoreState`](custom_types.customTypes.md#reduxstatecorestate) |
| `logs` | [`reduxStateLogs`](custom_types.customTypes.md#reduxstatelogs) |

#### Defined in

[custom-types.ts:21](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L21)

___

### reduxStateActivity

Ƭ **reduxStateActivity**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `history` | [`activityHistory`](custom_types.customTypes.md#activityhistory) \| `undefined` |

#### Defined in

[custom-types.ts:18](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L18)

___

### reduxStateConfig

Ƭ **reduxStateConfig**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `central` | [`config`](custom_types.customTypes.md#config) \| `undefined` |
| `errorMessage` | `string` \| `undefined` |
| `isDiffering` | `boolean` \| `undefined` |
| `local` | [`config`](custom_types.customTypes.md#config) \| `undefined` |

#### Defined in

[custom-types.ts:2](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L2)

___

### reduxStateCoreProcess

Ƭ **reduxStateCoreProcess**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `pid` | `number` \| `undefined` |

#### Defined in

[custom-types.ts:15](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L15)

___

### reduxStateCoreState

Ƭ **reduxStateCoreState**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `body` | [`coreState`](custom_types.customTypes.md#corestate) \| `undefined` |

#### Defined in

[custom-types.ts:14](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L14)

___

### reduxStateLogs

Ƭ **reduxStateLogs**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `debugLines` | `string`[] \| `undefined` |
| `fetchUpdates` | `boolean` |
| `infoLines` | `string`[] \| `undefined` |
| `renderedLogScope` | `string` |

#### Defined in

[custom-types.ts:8](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/custom-types.ts#L8)
