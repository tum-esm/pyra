import { customTypes } from '../../../custom-types';
import { configComponents } from '../..';

export default function ConfigSectionGeneral(props: {
    localConfig: customTypes.config;
    centralConfig: any;
    addLocalUpdate(v: customTypes.partialConfig): void;
}) {
    const { localConfig, centralConfig, addLocalUpdate } = props;

    return (
        <>
            <configComponents.ConfigElementText
                key2="seconds_per_core_interval"
                value={localConfig.general.seconds_per_core_interval}
                setValue={(v: number) =>
                    addLocalUpdate({ general: { seconds_per_core_interval: v } })
                }
                oldValue={centralConfig.general.seconds_per_core_interval}
            />
            <configComponents.ConfigElementToggle
                key2="test_mode"
                value={localConfig.general.test_mode}
                setValue={(v: boolean) => addLocalUpdate({ general: { test_mode: v } })}
                oldValue={centralConfig.general.test_mode}
            />
            <configComponents.ConfigElementText
                key2="station_id"
                value={localConfig.general.station_id}
                setValue={(v: string) => addLocalUpdate({ general: { station_id: v } })}
                oldValue={centralConfig.general.station_id}
            />
        </>
    );
}
