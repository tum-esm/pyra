import { configurationComponents } from '../..';
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
                title="Station ID"
                value={localSectionConfig.station_id}
                setValue={(v: string) => setLocalConfigItem('general.station_id', v)}
                oldValue={centralSectionConfig.station_id}
            />
            <configurationComponents.ConfigElementNote>
                Used in logs, emails and Helios images.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Seconds Per Core-Iteration"
                value={localSectionConfig.seconds_per_core_iteration}
                setValue={(v: number) =>
                    setLocalConfigItem('general.seconds_per_core_iteration', v)
                }
                oldValue={centralSectionConfig.seconds_per_core_iteration}
                postfix="second(s)"
                numeric
            />
            <configurationComponents.ConfigElementText
                title="Min. Sun Elevation"
                value={localSectionConfig.min_sun_elevation}
                setValue={(v: number) => setLocalConfigItem('general.min_sun_elevation', v)}
                oldValue={centralSectionConfig.min_sun_elevation}
                postfix="degree(s)"
                numeric
            />
            <configurationComponents.ConfigElementNote>
                The EM27/SUN will power up three degrees below to warm up (only if enclosure is
                configured). Helios will start at this angle. Manual measurements will start at this
                angle.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementBooleanToggle
                title="Test Mode"
                value={localSectionConfig.test_mode}
                setValue={(v: boolean) => setLocalConfigItem('general.test_mode', v)}
                oldValue={centralSectionConfig.test_mode}
            />
            <configurationComponents.ConfigElementNote>
                Only used in development. Otherwise left at `no`. If enabled, Pyra does not connect
                to the enclosure hardware, OPUS and CamTracker so it can run on any computer.
            </configurationComponents.ConfigElementNote>
        </>
    );
}
