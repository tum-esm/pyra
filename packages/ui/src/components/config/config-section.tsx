import ConfigElementText from './config-element-text';
import ConfigElementToggle from './config-element-toggle';
import ConfigElementMatrix from './config-element-matrix';
import ConfigElementTime from './config-element-time';

import sortConfigKeys from '../../utils/sort-config-keys';

/*
Special triggers:

If (!measurement_triggers.type.sun_angle) {
    hide and set to old value -> measurement_triggers.sun_angle_start
    hide and set to old value -> measurement_triggers.sun_angle_stop
}

If (!measurement_triggers.type.time) {
    hide and set to old value -> measurement_triggers.start_time
    hide and set to old value -> measurement_triggers.stop_time
}

TODO: rename measurement_triggers.user_trigger_present!!!
If (!measurement_triggers.type.user_control) {
    hide and set to old value -> measurement_triggers.user_trigger_present
}

If (!plc.is_present) {
    hide and set to old value -> all other stuff inside plc
    set plc.ip to 0.0.0.0
}

TODO: remove vbdsd.image_storage_path
TODO: rename vbdsd.sensor_is_present to vbdsd.is_present
If (!vbdsd.sensor_is_present) {
    hide and set to old value -> all other stuff inside vbdsd
    hide the whole vbdsd section inside parameters
}
*/
export default function ConfigSection(props: {
    key1: string;
    localConfig: any;
    centralConfig: any;
    addLocalUpdate(v: any): void;
}) {
    const {
        key1,
        localConfig: localJSON,
        centralConfig: centralJSON,
        addLocalUpdate,
    } = props;

    const key0 = 'parameters';

    return (
        <>
            {sortConfigKeys(centralJSON[key1]).map((key2: string, j: number) => {
                const commonProps = {
                    key: key2,
                    key1: key1,
                    key2: key2,
                    value: localJSON[key1][key2],
                    oldValue: centralJSON[key1][key2],
                    setValue: (v: any) =>
                        addLocalUpdate({
                            [key1]: {
                                [key2]: v,
                            },
                        }),
                };
                const oldValue: any = centralJSON[key1][key2];

                /*if (key0 === 'setup') {
                    if (key1 === 'tum_plc') {
                        const noTUMPLC = !localJSON['tum_plc']['is_present'];
                        if (noTUMPLC && key2 !== 'is_present') {
                            return <></>;
                        }
                    }
                    if (key1 === 'vbdsd') {
                        const noVBDSD = !localJSON['vbdsd']['is_present'];
                        if (noVBDSD && key2 !== 'is_present') {
                            return <></>;
                        }
                    }
                }*/
                if (key0 === 'parameters') {
                    if (key1 === 'measurement_triggers') {
                        const triggerOverride =
                            localJSON['measurement_triggers']['manual_override'];

                        const ignoringSunAngle =
                            !localJSON['measurement_triggers']['type']['sun_angle'];

                        const ignoringTime =
                            !localJSON['measurement_triggers']['type']['time'];

                        if (
                            (triggerOverride && key2 !== 'manual_override') ||
                            (ignoringSunAngle && key2.startsWith('sun_angle')) ||
                            (ignoringTime && key2.endsWith('time'))
                        ) {
                            return <></>;
                        }
                    }
                }

                switch (typeof oldValue) {
                    case 'string':
                    case 'number':
                        return (
                            /* @ts-ignore */
                            <ConfigElementText {...commonProps} />
                        );
                    case 'boolean':
                        return (
                            /* @ts-ignore */
                            <ConfigElementToggle {...commonProps} />
                        );
                    case 'object':
                        if (oldValue.length === undefined) {
                            return (
                                /* @ts-ignore */
                                <ConfigElementMatrix {...commonProps} />
                            );
                        } else if (oldValue.length === 3) {
                            return (
                                /* @ts-ignore */
                                <ConfigElementTime {...commonProps} />
                            );
                        }
                }
            })}
        </>
    );
}
