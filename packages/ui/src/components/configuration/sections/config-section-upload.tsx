import { pullAt } from 'lodash';
import { configurationComponents, essentialComponents } from '../..';
import fetchUtils from '../../../utils/fetch-utils';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import { Button } from '../../ui/button';
import { Fragment } from 'react';
import toast from 'react-hot-toast';

export default function ConfigSectionUpload() {
    const { centralConfig, localConfig, setLocalConfigItem, configIsDiffering } = useConfigStore();
    const { runPromisingCommand } = fetchUtils.useCommand();

    const centralSectionConfig = centralConfig?.upload;
    const localSectionConfig = localConfig?.upload;

    function test() {
        if (configIsDiffering()) {
            toast.error('Please save your configuration before testing the upload.');
        } else {
            runPromisingCommand({
                command: fetchUtils.backend.testUpload,
                label: 'testing connection to upload server',
                successLabel: 'successfully connected to upload server',
            });
        }
    }

    function addDefault() {
        setLocalConfigItem('upload', {
            host: '1.2.3.4',
            user: '...',
            password: '...',
            streams: [],
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
                    <div className="absolute -top-2.5 -left-1 w-1 h-[calc(100%+0.625rem)] -translate-x-2.5 bg-blue-300" />
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

    function addStream() {
        if (localSectionConfig) {
            setLocalConfigItem('upload.streams', [
                ...localSectionConfig.streams,
                {
                    is_active: false,
                    label: 'datalogger',
                    variant: 'files',
                    dated_regex: '^.*%Y-%m-%d.*$',
                    src_directory: '...',
                    dst_directory: '...',
                    remove_src_after_upload: false,
                },
            ]);
        }
    }

    function removeStream(index: number) {
        if (localSectionConfig) {
            setLocalConfigItem(
                'upload.streams',
                localSectionConfig.streams.length === 1
                    ? []
                    : pullAt(localSectionConfig.streams, index)
            );
        }
    }

    return (
        <>
            <div className="flex flex-row gap-x-2">
                <Button onClick={setNull}>remove configuration</Button>
                <Button onClick={test}>test upload connection</Button>
            </div>
            <div className="flex-shrink-0 w-full mt-1 text-xs text-slate-500 flex-row-left gap-x-1">
                <p>
                    This upload feature uses the `circadian-scp-upload` Python library (
                    <a
                        href="https://github.com/dostuffthatmatters/circadian-scp-upload"
                        target="_blank"
                        className="inline text-blue-500 underline"
                    >
                        github.com/dostuffthatmatters/circadian-scp-upload
                    </a>
                    ). You can use it to upload your inteferograms, your datalogger files, and so
                    on: Any data generated day by day that has to be uploaded to a server.
                </p>
            </div>
            {centralSectionConfig &&
                centralSectionConfig?.streams.length > localSectionConfig.streams.length && (
                    <div className="text-xs font-normal text-blue-400 top-7">
                        modified:{' '}
                        {centralSectionConfig?.streams.length - localSectionConfig.streams.length}{' '}
                        stream(s) have been deleted
                    </div>
                )}
            <configurationComponents.ConfigElementLine />
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
            <configurationComponents.ConfigElementBooleanToggle
                title="Only Upload At Night"
                value={localSectionConfig.only_upload_at_night}
                setValue={(v: boolean) => setLocalConfigItem(`upload.only_upload_at_nighte`, v)}
                oldValue={
                    centralSectionConfig !== null ? centralSectionConfig.only_upload_at_night : null
                }
            />
            <configurationComponents.ConfigElementNote>
                At night = below 0° sun elevation
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
            {localSectionConfig.streams.map((stream, index) => (
                <Fragment key={`${index}`}>
                    <div className="flex flex-col pl-8 border-l-2 border-dotted border-slate-300 gap-y-2">
                        <div className="flex flex-row items-baseline text-xs font-semibold text-slate-950">
                            <div>
                                Stream {index + 1} ({stream.label})
                            </div>
                            <div className="flex-grow" />
                            <div className="flex flex-row gap-x-2">
                                <Button onClick={() => removeStream(index)}>
                                    remove upload stream
                                </Button>
                            </div>
                        </div>
                        <configurationComponents.ConfigElementBooleanToggle
                            title="Is Active"
                            value={stream.is_active}
                            setValue={(v: boolean) =>
                                setLocalConfigItem(`upload.streams.${index}.is_active`, v)
                            }
                            oldValue={
                                centralSectionConfig?.streams[index]
                                    ? centralSectionConfig.streams[index]?.is_active
                                    : null
                            }
                        />
                        <configurationComponents.ConfigElementText
                            title="Label"
                            value={stream.label}
                            setValue={(v: string) =>
                                setLocalConfigItem(`upload.streams.${index}.label`, v)
                            }
                            oldValue={
                                centralSectionConfig !== null
                                    ? centralSectionConfig.streams[index]?.label
                                    : 'null'
                            }
                        />
                        <configurationComponents.ConfigElementLine />
                        <configurationComponents.LabeledRow
                            title={'Variant'}
                            modified={
                                centralSectionConfig?.streams[index]?.variant !== stream.variant
                            }
                        >
                            <div className="flex flex-row text-xs gap-x-2">
                                <button
                                    className={
                                        'flex flex-col border divide-y rounded-lg shadow-sm divide-slate-200 border-slate-300 w-52 items-center bg-slate-100 ' +
                                        (stream.variant === 'directories'
                                            ? 'opacity-100'
                                            : 'opacity-50')
                                    }
                                    onClick={() =>
                                        setLocalConfigItem(
                                            `upload.streams.${index}.variant`,
                                            'directories'
                                        )
                                    }
                                >
                                    <div
                                        className={
                                            'w-full py-2 text-sm font-medium text-center rounded-t-lg ' +
                                            (stream.variant === 'directories'
                                                ? 'bg-slate-900 text-white'
                                                : 'bg-slate-100 text-slate-950')
                                        }
                                    >
                                        directories
                                    </div>
                                    <div className="relative flex-grow p-2 font-mono text-left whitespace-pre text-slate-800">
                                        {'📁 data-directory\n' +
                                            ' ├── 📁 20190101\n' +
                                            ' │    ├── 📄 file1.txt\n' +
                                            ' │    ├── 📄 file2.txt\n' +
                                            ' │    └── 📄 file3.txt\n' +
                                            ' └── 📁 20190102\n' +
                                            '      ├── 📄 file1.txt\n' +
                                            '      ├── 📄 file2.txt\n' +
                                            '      └── 📄 file3.txt'}
                                    </div>
                                </button>
                                <button
                                    className={
                                        'flex flex-col border divide-y rounded-lg shadow-sm divide-slate-200 border-slate-300 w-52 items-center bg-slate-100 ' +
                                        (stream.variant === 'files' ? 'opacity-100' : 'opacity-50')
                                    }
                                    onClick={() =>
                                        setLocalConfigItem(
                                            `upload.streams.${index}.variant`,
                                            'files'
                                        )
                                    }
                                >
                                    <div
                                        className={
                                            'w-full py-2 text-sm font-medium text-center rounded-t-lg ' +
                                            (stream.variant === 'files'
                                                ? 'bg-slate-900 text-white'
                                                : 'bg-slate-100 text-slate-950')
                                        }
                                    >
                                        files
                                    </div>
                                    <div className="flex-grow p-2 font-mono text-left whitespace-pre text-slate-800">
                                        {'📁 data-directory\n' +
                                            ' ├── 📄 20190101.txt\n' +
                                            ' ├── 📄 20190102-a.txt\n' +
                                            ' ├── 📄 20190102-b.txt\n' +
                                            ' └── 📄 20190103.txt'}
                                    </div>
                                </button>
                            </div>
                            <essentialComponents.PreviousValue
                                previousValue={
                                    centralSectionConfig?.streams[index]?.variant === undefined
                                        ? 'null'
                                        : centralSectionConfig?.streams[index]?.variant ===
                                          stream.variant
                                        ? undefined
                                        : centralSectionConfig?.streams[index]?.variant
                                }
                            />
                        </configurationComponents.LabeledRow>
                        <configurationComponents.ConfigElementText
                            title="Dated Regex"
                            value={stream.dated_regex}
                            setValue={(v: string) =>
                                setLocalConfigItem(`upload.streams.${index}.dated_regex`, v)
                            }
                            oldValue={
                                centralSectionConfig !== null
                                    ? centralSectionConfig.streams[index]?.dated_regex
                                    : 'null'
                            }
                        />
                        <configurationComponents.ConfigElementNote>
                            `^.*%Y-%m-%d.*$` (as an example) will look for directories/files named
                            for `...2019-01-01...` to determine when they have been created.
                        </configurationComponents.ConfigElementNote>
                        <configurationComponents.ConfigElementLine />
                        <configurationComponents.ConfigElementText
                            title="Source Directory"
                            value={stream.src_directory}
                            setValue={(v: string) =>
                                setLocalConfigItem(`upload.streams.${index}.src_directory`, v)
                            }
                            oldValue={
                                centralSectionConfig !== null
                                    ? centralSectionConfig.streams[index]?.src_directory
                                    : 'null'
                            }
                            showSelector="directory"
                        />
                        <configurationComponents.ConfigElementText
                            title="Destination Directory"
                            value={stream.dst_directory}
                            setValue={(v: string) =>
                                setLocalConfigItem(`upload.streams.${index}.dst_directory`, v)
                            }
                            oldValue={centralSectionConfig?.streams[index]?.dst_directory}
                        />
                        <configurationComponents.ConfigElementBooleanToggle
                            title="Remove Source After Upload"
                            value={stream.remove_src_after_upload}
                            setValue={(v: boolean) =>
                                setLocalConfigItem(
                                    `upload.streams.${index}.remove_src_after_upload`,
                                    v
                                )
                            }
                            oldValue={
                                centralSectionConfig?.streams[index]
                                    ? centralSectionConfig.streams[index]?.remove_src_after_upload
                                    : null
                            }
                        />
                    </div>
                    <configurationComponents.ConfigElementLine />
                </Fragment>
            ))}
            <div className="flex flex-row gap-x-2">
                <div className="flex-grow" />
                <Button onClick={addStream}>add upload stream</Button>
            </div>
        </>
    );
}
