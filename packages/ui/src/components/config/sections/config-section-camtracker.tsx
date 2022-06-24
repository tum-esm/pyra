import { customTypes } from '../../../custom-types';
import { configComponents } from '../..';

export default function ConfigSectionCamtracker(props: {
    localConfig: customTypes.config;
    centralConfig: any;
    addLocalUpdate(v: customTypes.partialConfig): void;
}) {
    const { localConfig, centralConfig, addLocalUpdate } = props;

    return (
        <>
            <configComponents.ConfigElementText
                key2="config_path"
                value={localConfig.camtracker.config_path}
                setValue={(v: string) =>
                    addLocalUpdate({ camtracker: { config_path: v } })
                }
                oldValue={centralConfig.camtracker.config_path}
            />
            <configComponents.ConfigElementText
                key2="executable_path"
                value={localConfig.camtracker.executable_path}
                setValue={(v: string) =>
                    addLocalUpdate({ camtracker: { executable_path: v } })
                }
                oldValue={centralConfig.camtracker.executable_path}
            />
            <configComponents.ConfigElementText
                key2="executable_path"
                value={localConfig.camtracker.executable_path}
                setValue={(v: string) =>
                    addLocalUpdate({ camtracker: { executable_path: v } })
                }
                oldValue={centralConfig.camtracker.executable_path}
            />
            <configComponents.ConfigElementText
                key2="learn_az_elev_path"
                value={localConfig.camtracker.learn_az_elev_path}
                setValue={(v: string) =>
                    addLocalUpdate({ camtracker: { learn_az_elev_path: v } })
                }
                oldValue={centralConfig.camtracker.learn_az_elev_path}
            />
            <configComponents.ConfigElementText
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
