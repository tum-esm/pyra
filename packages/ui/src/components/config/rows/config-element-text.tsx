import TextInput from '../../essential/text-input';
import Button from '../../essential/button';
import LabeledRow from '../labeled-row';
import PreviousValue from '../../essential/previous-value';
import { dialog } from '@tauri-apps/api';
import parseNumberTypes from '../../../utils/parse-number-types';

function getPostfix(key: string) {
    if (
        key.includes('angle') ||
        key.includes('threshold') ||
        key.includes('elevation')
    ) {
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
}) {
    const { key2, value, oldValue, setValue, disabled } = props;

    async function triggerFileSelection() {
        const result: any = await dialog.open({ title: 'PyRa 4 UI', multiple: false });
        console.log({ result });
        if (result !== null) {
            setValue(result);
        }
    }

    const showfileSelector = key2.endsWith('_path');
    const hasBeenModified = value != oldValue;

    return (
        <LabeledRow key2={key2} modified={hasBeenModified}>
            <div className="relative w-full flex-row-center gap-x-1">
                <TextInput
                    value={value.toString()}
                    setValue={setValue}
                    postfix={getPostfix(key2)}
                />
                {showfileSelector && !disabled && (
                    <Button variant="slate" onClick={triggerFileSelection}>
                        select
                    </Button>
                )}
            </div>
            <PreviousValue
                previousValue={hasBeenModified ? `${oldValue}` : undefined}
            />
        </LabeledRow>
    );
}
