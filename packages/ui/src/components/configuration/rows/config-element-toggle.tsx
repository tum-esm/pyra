import { configurationComponents, essentialComponents } from '../..';

export default function ConfigElementToggle(props: {
    title: string;
    value: boolean;
    oldValue: boolean;
    setValue(v: boolean): void;
}) {
    const { title, value, oldValue, setValue } = props;

    return (
        <configurationComponents.LabeledRow title={title} modified={value !== oldValue}>
            <essentialComponents.Toggle
                value={value ? 'yes' : 'no'}
                values={['yes', 'no']}
                setValue={(v) => setValue(v === 'yes')}
            />
            <essentialComponents.PreviousValue
                previousValue={value !== oldValue ? (oldValue ? 'yes' : 'no') : undefined}
            />
        </configurationComponents.LabeledRow>
    );
}
