import { configurationComponents, essentialComponents } from '../..';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import { Button } from '../../ui/button';

export default function ConfigSectionUpload() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();

    const centralSectionConfig = centralConfig?.upload;
    const localSectionConfig = localConfig?.upload;

    function addDefault() {
        setLocalConfigItem('upload', {
            host: '1.2.3.4',
            user: '...',
            password: '...',
            streams: [
                {
                    is_active: false,
                    label: 'interferograms',
                    variant: 'directories',
                    dated_regex: '^%Y%m%d$',
                    src_directory: '...',
                    dst_directory: '...',
                    remove_src_after_upload: false,
                },
                {
                    is_active: false,
                    label: 'datalogger',
                    variant: 'files',
                    dated_regex: '^datalogger-%Y-%m-%d*$',
                    src_directory: '...',
                    dst_directory: '...',
                    remove_src_after_upload: false,
                },
            ],
        });
    }

    function setNull() {
        setLocalConfigItem('upload', null);
    }

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }

    if (localSectionConfig === null) {
        return (
            <div className="relative space-y-2 text-sm flex-col-left">
                <div className="space-x-2 text-sm flex-row-left">
                    <span className="whitespace-nowrap">Not configured yet</span>
                    <Button onClick={addDefault}>set up now</Button>
                    {centralSectionConfig !== null && (
                        <div className="absolute -top-2.5 -left-1 w-1.5 h-[calc(100%+0.625rem)] -translate-x-2.5 bg-yellow-400 rounded-sm" />
                    )}
                </div>
                <essentialComponents.PreviousValue
                    previousValue={
                        centralSectionConfig !== null
                            ? JSON.stringify(centralSectionConfig)
                                  .replace(/":/g, '": ')
                                  .replace(/,"/g, ', "')
                            : undefined
                    }
                />
            </div>
        );
    }

    return (
        <>
            <Button onClick={setNull}>remove configuration</Button>
            <div className="w-full h-px my-6 bg-gray-300" />
            <configurationComponents.ConfigElementText
                title="Host"
                value={localSectionConfig.host}
                setValue={(v: string) => setLocalConfigItem('upload.host', v)}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.host : 'null'}
            />
            <configurationComponents.ConfigElementText
                title="User"
                value={localSectionConfig.user}
                setValue={(v: string) => setLocalConfigItem('upload.user', v)}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.user : 'null'}
            />
            <configurationComponents.ConfigElementText
                title="Password"
                value={localSectionConfig.password}
                setValue={(v: string) => setLocalConfigItem('upload.password', v)}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.password : 'null'}
            />
            <div className="w-full h-px my-6 bg-gray-300" />
            TODO: add stream configs
        </>
    );
}
