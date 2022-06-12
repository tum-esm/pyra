import TYPES from '../../../utils/types';
import ConfigElementText from '../rows/config-element-text';

export default function ConfigSectionCamtracker(props: {
    localConfig: TYPES.config;
    centralConfig: any;
    addLocalUpdate(v: TYPES.partialConfig): void;
}) {
    const { localConfig, centralConfig, addLocalUpdate } = props;

    return (
        <>
            <ConfigElementText
                key2="config_path"
                value={localConfig.camtracker.config_path}
                setValue={(v: string) =>
                    addLocalUpdate({ camtracker: { config_path: v } })
                }
                oldValue={centralConfig.camtracker.config_path}
            />
            <ConfigElementText
                key2="executable_path"
                value={localConfig.camtracker.executable_path}
                setValue={(v: string) =>
                    addLocalUpdate({ camtracker: { executable_path: v } })
                }
                oldValue={centralConfig.camtracker.executable_path}
            />
            <ConfigElementText
                key2="executable_path"
                value={localConfig.camtracker.executable_path}
                setValue={(v: string) =>
                    addLocalUpdate({ camtracker: { executable_path: v } })
                }
                oldValue={centralConfig.camtracker.executable_path}
            />
            <ConfigElementText
                key2="learn_az_elev_path"
                value={localConfig.camtracker.learn_az_elev_path}
                setValue={(v: string) =>
                    addLocalUpdate({ camtracker: { learn_az_elev_path: v } })
                }
                oldValue={centralConfig.camtracker.learn_az_elev_path}
            />
            <ConfigElementText
                key2="motor_offset_threshold"
                value={localConfig.camtracker.motor_offset_threshold}
                setValue={(v: number) =>
                    addLocalUpdate({ camtracker: { motor_offset_threshold: v } })
                }
                oldValue={centralConfig.camtracker.motor_offset_threshold}
            />
        </>
    );
}
