import { configurationComponents, essentialComponents } from '../..';
import { renderTimeObject } from '../../../utils/functions';

export default function ConfigElementTime(props: {
    title: string;
    value: { hour: number; minute: number; second: number };
    oldValue: { hour: number; minute: number; second: number };
    setValue(v: { hour: number; minute: number; second: number }): void;
    disabled?: boolean;
}) {
    const { title, value, oldValue, setValue, disabled } = props;

    function parseNumericValue(v: string): number {
        return parseInt(`${v}`.replace(/[^\d]/g, '')) || 0;
    }

    let hasBeenModified =
        value.hour !== oldValue.hour ||
        value.minute !== oldValue.minute ||
        value.second !== oldValue.second;

    return (
        <configurationComponents.LabeledRow title={title + ' (h:m:s)'} modified={hasBeenModified}>
            <div className="relative flex flex-row items-baseline w-full gap-x-1">
                <essentialComponents.TextInput
                    value={value.hour.toString()}
                    setValue={(v: string) => setValue({ ...value, hour: parseNumericValue(v) })}
                    disabled={disabled}
                />
                :
                <essentialComponents.TextInput
                    value={value.minute.toString()}
                    setValue={(v: any) => setValue({ ...value, minute: parseNumericValue(v) })}
                    disabled={disabled}
                />
                :
                <essentialComponents.TextInput
                    value={value.second.toString()}
                    setValue={(v: any) => setValue({ ...value, second: parseNumericValue(v) })}
                    disabled={disabled}
                />
            </div>
            <essentialComponents.PreviousValue
                previousValue={hasBeenModified ? renderTimeObject(oldValue) : undefined}
            />
        </configurationComponents.LabeledRow>
    );
}
