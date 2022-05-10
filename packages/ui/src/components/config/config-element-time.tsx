import TextInput from '../essential/text-input';
import LabeledRow from './labeled-row';
import PreviousValue from '../essential/previous-value';

export default function ConfigElementTime(props: {
    key1: string;
    key2: string;
    value: [number, number, number];
    oldValue: [number, number, number];
    setValue(v: [number, number, number]): void;
    disabled?: boolean;
}) {
    const { key1, key2, value, oldValue, setValue, disabled } = props;

    const hasChanged = JSON.stringify(value) !== JSON.stringify(oldValue);

    return (
        <LabeledRow key2={key2 + ' (h:m:s)'} modified={hasChanged}>
            <div className="relative flex w-full gap-x-1">
                <TextInput
                    value={value[0].toString()}
                    setValue={(v: any) => setValue([v, value[1], value[2]])}
                    small
                />
                :
                <TextInput
                    value={value[1].toString()}
                    setValue={(v: any) => setValue([value[0], v, value[2]])}
                    small
                />
                :
                <TextInput
                    value={value[2].toString()}
                    setValue={(v: any) => setValue([value[0], value[1], v])}
                    small
                />
                <PreviousValue previousValue={hasChanged ? oldValue : undefined} />
            </div>
        </LabeledRow>
    );
}
