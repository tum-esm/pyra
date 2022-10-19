import { dialog } from '@tauri-apps/api';
import { functionalUtils } from '../../../utils';
import { configurationComponents, essentialComponents } from '../..';

export default function ConfigElementText(props: {
    title: string;
    value: string | number;
    oldValue: string | number;
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

    function parseNumericValue(v: string): any {
        return `${v}`.replace(/[^\d\.]/g, '');
    }

    const showfileSelector = title.endsWith('Path') || props.showFileSelector;
    const hasBeenModified = !functionalUtils.deepEqual(oldValue, value);

    return (
        <configurationComponents.LabeledRow title={title} modified={hasBeenModified}>
            <div className="relative w-full flex-row-center gap-x-1">
                <essentialComponents.TextInput
                    value={value.toString()}
                    setValue={(v) => (numeric ? setValue(parseNumericValue(v)) : setValue(v))}
                    postfix={postfix}
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
