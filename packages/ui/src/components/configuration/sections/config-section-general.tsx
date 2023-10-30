import { configurationComponents } from '../..';
import { ICONS } from '../../../assets';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';

export default function ConfigSectionGeneral() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();

    const centralSectionConfig = centralConfig?.general;
    const localSectionConfig = localConfig?.general;

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configurationComponents.ConfigElementText
                title="Seconds Per Core Interval"
                value={localSectionConfig.seconds_per_core_interval}
                setValue={(v: number) => setLocalConfigItem('general.seconds_per_core_interval', v)}
                oldValue={centralSectionConfig.seconds_per_core_interval}
                postfix="second(s)"
            />
            <configurationComponents.ConfigElementToggle
                title="Test Mode"
                value={localSectionConfig.test_mode}
                setValue={(v: boolean) => setLocalConfigItem('general.test_mode', v)}
                oldValue={centralSectionConfig.test_mode}
            />
            <configurationComponents.ConfigElementText
                title="Station ID"
                value={localSectionConfig.station_id}
                setValue={(v: string) => setLocalConfigItem('general.station_id', v)}
                oldValue={centralSectionConfig.station_id}
            />
            <configurationComponents.ConfigElementText
                title="Min. Sun Elevation"
                value={localSectionConfig.min_sun_elevation}
                setValue={(v: number) => setLocalConfigItem('general.min_sun_elevation', v)}
                oldValue={centralSectionConfig.min_sun_elevation}
                postfix="degree(s)"
            />
            <div className="w-full -mt-[1.125rem] pl-[12.5rem] text-xs text-blue-600 flex-row-left gap-x-1">
                <div className="w-4 h-4 text-blue-400">{ICONS.info}</div>The TUM PLC will start its
                operation one degree earlier. Helios will start at this angle.
            </div>
        </>
    );
}
