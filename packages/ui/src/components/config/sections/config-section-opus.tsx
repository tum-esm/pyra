import TYPES from '../../../utils/types';
import ConfigElementText from '../rows/config-element-text';

export default function ConfigSectionOpus(props: {
    localConfig: TYPES.config;
    centralConfig: any;
    addLocalUpdate(v: TYPES.partialConfig): void;
}) {
    const { localConfig, centralConfig, addLocalUpdate } = props;

    return (
        <>
            <ConfigElementText
                key2="em27_ip"
                value={localConfig.opus.em27_ip}
                setValue={(v: string) => addLocalUpdate({ opus: { em27_ip: v } })}
                oldValue={centralConfig.opus.em27_ip}
            />
            <ConfigElementText
                key2="executable_path"
                value={localConfig.opus.executable_path}
                setValue={(v: string) =>
                    addLocalUpdate({ opus: { executable_path: v } })
                }
                oldValue={centralConfig.opus.executable_path}
            />
            <ConfigElementText
                key2="executable_parameter"
                value={localConfig.opus.executable_parameter}
                setValue={(v: string) =>
                    addLocalUpdate({ opus: { executable_parameter: v } })
                }
                oldValue={centralConfig.opus.executable_parameter}
            />
            <ConfigElementText
                key2="experiment_path"
                value={localConfig.opus.experiment_path}
                setValue={(v: string) =>
                    addLocalUpdate({ opus: { experiment_path: v } })
                }
                oldValue={centralConfig.opus.experiment_path}
            />
            <ConfigElementText
                key2="macro_path"
                value={localConfig.opus.macro_path}
                setValue={(v: string) => addLocalUpdate({ opus: { macro_path: v } })}
                oldValue={centralConfig.opus.macro_path}
            />
        </>
    );
}
