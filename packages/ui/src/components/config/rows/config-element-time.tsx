import { functionalUtils } from '../../../utils';
import { configComponents, essentialComponents } from '../..';

export default function ConfigElementTime(props: {
    key2: string;
    value: { hour: number; minute: number; second: number };
    oldValue: { hour: number; minute: number; second: number };
    setValue(v: { hour: number; minute: number; second: number }): void;
    disabled?: boolean;
}) {
    const { key2, value, oldValue, setValue, disabled } = props;

    const hasChanged = !functionalUtils.deepEqual(value, oldValue);

    function parseNumericValue(v: string): any {
        return `${v}`.replace(/[^\d\.]/g, '');
    }

    return (
        <configComponents.LabeledRow key2={key2 + ' (h:m:s)'} modified={hasChanged}>
            <div className="relative flex w-full gap-x-1">
                <essentialComponents.TextInput
                    value={value.hour.toString()}
                    setValue={(v: string) =>
                        setValue({ ...value, hour: parseNumericValue(v) })
                    }
                    small
                />
                :
                <essentialComponents.TextInput
                    value={value.minute.toString()}
                    setValue={(v: any) =>
                        setValue({ ...value, minute: parseNumericValue(v) })
                    }
                    small
                />
                :
                <essentialComponents.TextInput
                    value={value.second.toString()}
                    setValue={(v: any) =>
                        setValue({ ...value, second: parseNumericValue(v) })
                    }
                    small
                />
                <essentialComponents.PreviousValue
                    previousValue={
                        hasChanged
                            ? `${oldValue.hour} : ${oldValue.minute} : ${oldValue.second}`
                            : undefined
                    }
                />
            </div>
        </configComponents.LabeledRow>
    );
}
