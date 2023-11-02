import { dialog, shell } from '@tauri-apps/api';
import { configurationComponents, essentialComponents } from '../..';
import { join } from '@tauri-apps/api/path';
import toast from 'react-hot-toast';

export default function ConfigElementText(props: {
    title: string;
    value: string | number;
    oldValue: string | number | undefined;
    setValue(v: string | number): void;
    disabled?: boolean;
    numeric?: boolean;
    postfix?: string;
    showFileSelector?: boolean;
}) {
    const { title, value, oldValue, setValue, disabled, numeric, postfix } = props;

    async function triggerFileSelection() {
        const result: any = await dialog.open({ title: 'PyRa 4 UI', multiple: false });
        if (result !== null) {
            setValue(result);
        }
    }

    function parseNumericValue(v: string): string {
        const parsedValue = `${v}`.replace(/[^\d\.]/g, '');
        if (parsedValue === '') {
            return '0';
        }
        return parsedValue;
    }

    async function openDirectory() {
        if (typeof value === 'string') {
            await shell
                .open(value.split('/').slice(0, -1).join('/'))
                .catch(() => toast.error('Could not open directory'));
        }
    }

    const showfileSelector = title.endsWith('Path') || props.showFileSelector;
    let hasBeenModified: boolean;
    if (numeric) {
        hasBeenModified = oldValue !== (typeof value === 'string' ? parseFloat(value) : value);
    } else {
        hasBeenModified = oldValue !== value;
    }

    return (
        <configurationComponents.LabeledRow title={title} modified={hasBeenModified}>
            <div className="relative w-full flex-row-center gap-x-1">
                <essentialComponents.TextInput
                    value={value.toString()}
                    setValue={(v) => setValue(numeric ? parseNumericValue(v) : v)}
                    postfix={postfix}
                />
                {showfileSelector && !disabled && (
                    <>
                        <essentialComponents.Button variant="white" onClick={triggerFileSelection}>
                            select
                        </essentialComponents.Button>
                        <essentialComponents.Button variant="white" onClick={openDirectory}>
                            show in explorer
                        </essentialComponents.Button>
                    </>
                )}
            </div>
            <essentialComponents.PreviousValue
                previousValue={
                    hasBeenModified ? (oldValue === undefined ? 'null' : `${oldValue}`) : undefined
                }
            />
        </configurationComponents.LabeledRow>
    );
}
