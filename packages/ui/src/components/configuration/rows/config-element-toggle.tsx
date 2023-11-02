import { configurationComponents, essentialComponents } from '../..';

export function ConfigElementToggle(props: {
    title: string;
    value: string;
    values: string[];
    oldValue: string | null;
    setValue(v: string): void;
}) {
    return (
        <configurationComponents.LabeledRow
            title={props.title}
            modified={props.value !== props.oldValue}
        >
            <essentialComponents.Toggle
                value={props.value}
                values={props.values}
                setValue={(v) => props.setValue(v)}
            />
            <essentialComponents.PreviousValue
                previousValue={
                    props.value !== props.oldValue
                        ? props.oldValue === null
                            ? 'null'
                            : props.oldValue
                        : undefined
                }
            />
        </configurationComponents.LabeledRow>
    );
}

export function ConfigElementBooleanToggle(props: {
    title: string;
    value: boolean;
    oldValue: boolean | null;
    setValue(v: boolean): void;
}) {
    return (
        <ConfigElementToggle
            title={props.title}
            value={props.value ? 'yes' : 'no'}
            values={['yes', 'no']}
            oldValue={props.oldValue !== null ? (props.oldValue ? 'yes' : 'no') : 'null'}
            setValue={(v) => props.setValue(v === 'yes')}
        />
    );
}
