import { configurationComponents } from '../..';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';

export default function ConfigSectionMeasurementTriggers() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();

    const centralSectionConfig = centralConfig?.measurement_triggers;
    const localSectionConfig = localConfig?.measurement_triggers;

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configurationComponents.ConfigElementBooleanToggle
                title="Consider Time"
                value={localSectionConfig.consider_time}
                setValue={(v: boolean) =>
                    setLocalConfigItem('measurement_triggers.consider_time', v)
                }
                oldValue={centralSectionConfig.consider_time}
            />
            <configurationComponents.ConfigElementBooleanToggle
                title="Consider Sun Elevation"
                value={localSectionConfig.consider_sun_elevation}
                setValue={(v: boolean) =>
                    setLocalConfigItem('measurement_triggers.consider_sun_elevation', v)
                }
                oldValue={centralSectionConfig.consider_sun_elevation}
            />
            <configurationComponents.ConfigElementBooleanToggle
                title="Consider Helios"
                value={localSectionConfig.consider_helios}
                setValue={(v: boolean) =>
                    setLocalConfigItem('measurement_triggers.consider_helios', v)
                }
                oldValue={centralSectionConfig.consider_helios}
            />
            <configurationComponents.ConfigElementNote>
                Pyra only does measurements when ALL of the activated triggers are true - e.g. when
                time is between start and stop time AND sun elevation is higher than the minimum
                elevation.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementTime
                title="Start Time"
                value={localSectionConfig.start_time}
                setValue={(v) => setLocalConfigItem('measurement_triggers.start_time', v)}
                oldValue={centralSectionConfig.start_time}
            />
            <configurationComponents.ConfigElementTime
                title="Stop Time"
                value={localSectionConfig.stop_time}
                setValue={(v) => setLocalConfigItem('measurement_triggers.stop_time', v)}
                oldValue={centralSectionConfig.stop_time}
            />
            <configurationComponents.ConfigElementNote>
                Pyra only does measurements between start and stop time (computer time is used).
                <br />
                The format is "hour : minute : second"
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Min. Sun Elevation"
                value={localSectionConfig.min_sun_elevation}
                setValue={(v: number) =>
                    setLocalConfigItem('measurement_triggers.min_sun_elevation', v)
                }
                oldValue={centralSectionConfig.min_sun_elevation}
                postfix="degree(s)"
                numeric
            />
            <configurationComponents.ConfigElementNote>
                Pyra only does measurements, when sun angle is higher than this value. This angle
                will only have an effect if it is higher than "general.min_sun_elevation".
            </configurationComponents.ConfigElementNote>
        </>
    );
}
