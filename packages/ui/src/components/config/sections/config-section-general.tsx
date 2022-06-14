import TYPES from '../../../utils/types';
import ConfigElementText from '../rows/config-element-text';
import ConfigElementToggle from '../rows/config-element-toggle';

export default function ConfigSectionGeneral(props: {
    localConfig: TYPES.config;
    centralConfig: any;
    addLocalUpdate(v: TYPES.partialConfig): void;
}) {
    const { localConfig, centralConfig, addLocalUpdate } = props;

    return (
        <>
            <ConfigElementText
                key2="seconds_per_core_interval"
                value={localConfig.general.seconds_per_core_interval}
                setValue={(v: number) =>
                    addLocalUpdate({ general: { seconds_per_core_interval: v } })
                }
                oldValue={centralConfig.general.seconds_per_core_interval}
            />
            <ConfigElementToggle
                key2="test_mode"
                value={localConfig.general.test_mode}
                setValue={(v: boolean) => addLocalUpdate({ general: { test_mode: v } })}
                oldValue={centralConfig.general.test_mode}
            />
        </>
    );
}
