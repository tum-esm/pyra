import TextInput from '../../essential/text-input';
import LabeledRow from '../labeled-row';
import PreviousValue from '../../essential/previous-value';

export default function ConfigElementTime(props: {
    key2: string;
    value: { hour: number; minute: number; second: number };
    oldValue: { hour: number; minute: number; second: number };
    setValue(v: { hour: number; minute: number; second: number }): void;
    disabled?: boolean;
}) {
    const { key2, value, oldValue, setValue, disabled } = props;

    const hasChanged =
        value.hour != oldValue.hour ||
        value.minute != oldValue.minute ||
        value.second != oldValue.second;

    return (
        <LabeledRow key2={key2 + ' (h:m:s)'} modified={hasChanged}>
            <div className="relative flex w-full gap-x-1">
                <TextInput
                    value={value.hour.toString()}
                    setValue={(v: string) => setValue({ ...value, hour: parseInt(v) })}
                    small
                />
                :
                <TextInput
                    value={value.minute.toString()}
                    setValue={(v: any) => setValue({ ...value, minute: parseInt(v) })}
                    small
                />
                :
                <TextInput
                    value={value.second.toString()}
                    setValue={(v: any) => setValue({ ...value, second: parseInt(v) })}
                    small
                />
                <PreviousValue previousValue={hasChanged ? oldValue : undefined} />
            </div>
        </LabeledRow>
    );
}
