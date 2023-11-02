import { configurationComponents, essentialComponents } from '../..';
import fetchUtils from '../../../utils/fetch-utils';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import { Button } from '../../ui/button';

export default function ConfigSectionUpload() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();
    const { runPromisingCommand } = fetchUtils.useCommand();

    const centralSectionConfig = centralConfig?.upload;
    const localSectionConfig = localConfig?.upload;

    function test() {
        runPromisingCommand({
            command: fetchUtils.backend.testUpload,
            label: 'testing connection to upload server',
            successLabel: 'successfully connected to upload server',
        });
    }

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
                <Button onClick={addDefault}>set up now</Button>
                {centralSectionConfig !== null && (
                    <div className="absolute -top-2.5 -left-1 w-1.5 h-[calc(100%+0.625rem)] -translate-x-2.5 bg-yellow-400 rounded-sm" />
                )}
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
            <div className="flex flex-row gap-x-2">
                <Button onClick={setNull}>remove configuration</Button>
                <Button onClick={test}>Test Upload Connection</Button>
            </div>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementNote>
                The IP and credentials of the Linux server to upload data to.
            </configurationComponents.ConfigElementNote>
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
            <configurationComponents.ConfigElementLine />
            TODO: add stream configs
        </>
    );
}
