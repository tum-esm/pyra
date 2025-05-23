import { configurationComponents, essentialComponents } from '../..';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import { Button } from '../../ui/button';

export default function ConfigSectionTUMEnclosure() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();

    const centralSectionConfig = centralConfig?.tum_enclosure;
    const localSectionConfig = localConfig?.tum_enclosure;

    function addDefault() {
        setLocalConfigItem('tum_enclosure', {
            ip: '10.10.0.4',
            version: 1,
            controlled_by_user: false,
        });
    }

    function setNull() {
        setLocalConfigItem('tum_enclosure', null);
    }

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }

    if (localSectionConfig === null) {
        return (
            <div className="relative space-y-2 text-sm flex-col-left">
                <Button onClick={addDefault}>set up now</Button>
                <essentialComponents.PreviousValue
                    previousValue={
                        centralSectionConfig !== null
                            ? JSON.stringify(centralSectionConfig)
                                  .replace(/":/g, '": ')
                                  .replace(/,"/g, ', "')
                            : undefined
                    }
                />
                {centralSectionConfig !== null && (
                    <div className="absolute -top-2.5 -left-1 w-1 h-[calc(100%+0.625rem)] -translate-x-2.5 bg-blue-300" />
                )}
            </div>
        );
    }

    return (
        <>
            <div>
                <Button onClick={setNull}>remove configuration</Button>
            </div>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="IP"
                value={localSectionConfig.ip}
                setValue={(v: string) => setLocalConfigItem('tum_enclosure.ip', v)}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.ip : 'null'}
            />
            <configurationComponents.ConfigElementText
                title="Version"
                value={localSectionConfig.version}
                setValue={(v: any) => setLocalConfigItem('tum_enclosure.version', v)}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.version : 'null'}
                numeric
            />
        </>
    );
}
