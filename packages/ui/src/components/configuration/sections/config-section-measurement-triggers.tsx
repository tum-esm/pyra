import { configurationComponents } from '../..';
import { ICONS } from '../../../assets';
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
            <configurationComponents.ConfigElementToggle
                title="Consider Time"
                value={localSectionConfig.consider_time}
                setValue={(v: boolean) =>
                    setLocalConfigItem('measurement_triggers.consider_time', v)
                }
                oldValue={centralSectionConfig.consider_time}
            />
            <div className="h-0 -mt-4" />
            <configurationComponents.ConfigElementToggle
                title="Consider Sun Elevation"
                value={localSectionConfig.consider_sun_elevation}
                setValue={(v: boolean) =>
                    setLocalConfigItem('measurement_triggers.consider_sun_elevation', v)
                }
                oldValue={centralSectionConfig.consider_sun_elevation}
            />
            <div className="h-0 -mt-4" />
            <configurationComponents.ConfigElementToggle
                title="Consider Helios"
                value={localSectionConfig.consider_helios}
                setValue={(v: boolean) =>
                    setLocalConfigItem('measurement_triggers.consider_helios', v)
                }
                oldValue={centralSectionConfig.consider_helios}
            />
            <div className="w-full h-px mb-6 -mt-2 bg-gray-300" />
            <configurationComponents.ConfigElementTime
                title="Start Time"
                value={localSectionConfig.start_time}
                setValue={(v) => setLocalConfigItem('measurement_triggers.start_time', v)}
                oldValue={centralSectionConfig.start_time}
            />
            <div className="h-0 -mt-4" />
            <configurationComponents.ConfigElementTime
                title="Stop Time"
                value={localSectionConfig.stop_time}
                setValue={(v) => setLocalConfigItem('measurement_triggers.stop_time', v)}
                oldValue={centralSectionConfig.stop_time}
            />
            <configurationComponents.ConfigElementText
                title="Min. Sun Elevation"
                value={localSectionConfig.min_sun_elevation}
                setValue={(v: number) => setLocalConfigItem('general.min_sun_elevation', v)}
                oldValue={centralSectionConfig.min_sun_elevation}
                postfix="degree(s)"
            />
            <div className="w-full -mt-[1.125rem] pl-[12.5rem] text-xs text-blue-600 flex-row-left gap-x-1">
                <div className="w-4 h-4 text-blue-400">{ICONS.info}</div>This angle will only have
                an effect if it is higher than "general.min_sun_elevation".
            </div>
        </>
    );
}
