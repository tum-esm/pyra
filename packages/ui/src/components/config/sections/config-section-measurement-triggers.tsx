import TYPES from '../../../utils/types';
import ConfigElementText from '../rows/config-element-text';
import ConfigElementToggle from '../rows/config-element-toggle';
import ICONS from '../../../assets/icons';

export default function ConfigSectionMeasurementTriggers(props: {
    localConfig: TYPES.config;
    centralConfig: any;
    addLocalUpdate(v: TYPES.partialConfig): void;
}) {
    const { localConfig, centralConfig, addLocalUpdate } = props;

    return (
        <>
            <ConfigElementToggle
                key2="consider_time"
                value={localConfig.measurement_triggers.consider_time}
                setValue={(v: boolean) =>
                    addLocalUpdate({ measurement_triggers: { consider_time: v } })
                }
                oldValue={centralConfig.measurement_triggers.consider_time}
            />
            <div className="h-0 -mt-4" />
            <ConfigElementToggle
                key2="consider_sun_elevation"
                value={localConfig.measurement_triggers.consider_sun_elevation}
                setValue={(v: boolean) =>
                    addLocalUpdate({
                        measurement_triggers: { consider_sun_elevation: v },
                    })
                }
                oldValue={centralConfig.measurement_triggers.consider_sun_elevation}
            />
            <div className="h-0 -mt-4" />
            <ConfigElementToggle
                key2="consider_vbdsd"
                value={localConfig.measurement_triggers.consider_vbdsd}
                setValue={(v: boolean) =>
                    addLocalUpdate({ measurement_triggers: { consider_vbdsd: v } })
                }
                oldValue={centralConfig.measurement_triggers.consider_vbdsd}
            />
            <div className="w-full h-px mb-6 -mt-2 bg-slate-300" />
            <ConfigElementText
                key2="min_sun_elevation"
                value={localConfig.measurement_triggers.min_sun_elevation}
                setValue={(v: number) =>
                    addLocalUpdate({ measurement_triggers: { min_sun_elevation: v } })
                }
                oldValue={centralConfig.measurement_triggers.min_sun_elevation}
            />
            <ConfigElementText
                key2="max_sun_elevation"
                value={localConfig.measurement_triggers.max_sun_elevation}
                setValue={(v: number) =>
                    addLocalUpdate({ measurement_triggers: { max_sun_elevation: v } })
                }
                oldValue={centralConfig.measurement_triggers.max_sun_elevation}
            />
            {/* TODO: start time stop time */}
        </>
    );
}
