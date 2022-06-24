import { configComponents, essentialComponents } from '../..';

export default function ConfigElementToggle(props: {
    key2: string;
    value: boolean;
    oldValue: boolean;
    setValue(v: boolean): void;
}) {
    const { key2, value, oldValue, setValue } = props;

    return (
        <configComponents.LabeledRow key2={key2} modified={value !== oldValue}>
            <essentialComponents.Toggle
                value={value ? 'yes' : 'no'}
                values={['yes', 'no']}
                setValue={(v) => setValue(v === 'yes')}
            />
            <essentialComponents.PreviousValue
                previousValue={
                    value !== oldValue ? (oldValue ? 'yes' : 'no') : undefined
                }
            />
        </configComponents.LabeledRow>
    );
}
