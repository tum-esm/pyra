import { dialog } from '@tauri-apps/api';
import { functionalUtils } from '../../../utils';
import { configurationComponents, essentialComponents } from '../..';

function getPostfix(key: string) {
    if (key.includes('angle') || key.includes('threshold') || key.includes('elevation')) {
        return 'degrees';
    }
    if (key.includes('seconds')) {
        return 'seconds';
    }
    if (key.includes('evaluation_size')) {
        return 'images';
    }
    return undefined;
}

export default function ConfigElementText(props: {
    key2: string;
    value: string | number;
    oldValue: string | number;
    setValue(v: string | number): void;
    disabled?: boolean;
    numeric?: boolean;
}) {
    const { key2, value, oldValue, setValue, disabled, numeric } = props;

    async function triggerFileSelection() {
        const result: any = await dialog.open({ title: 'PyRa 4 UI', multiple: false });
        console.log({ result });
        if (result !== null) {
            setValue(result);
        }
    }

    function parseNumericValue(v: string): any {
        return `${v}`.replace(/[^\d\.]/g, '');
    }

    const showfileSelector = key2.endsWith('_path');
    const hasBeenModified = !functionalUtils.deepEqual(oldValue, value);

    return (
        <configurationComponents.LabeledRow key2={key2} modified={hasBeenModified}>
            <div className="relative w-full flex-row-center gap-x-1">
                <essentialComponents.TextInput
                    value={value.toString()}
                    setValue={(v) => (numeric ? setValue(parseNumericValue(v)) : setValue(v))}
                    postfix={getPostfix(key2)}
                />
                {showfileSelector && !disabled && (
                    <essentialComponents.Button variant="white" onClick={triggerFileSelection}>
                        select
                    </essentialComponents.Button>
                )}
            </div>
            <essentialComponents.PreviousValue
                previousValue={hasBeenModified ? `${oldValue}` : undefined}
            />
        </configurationComponents.LabeledRow>
    );
}