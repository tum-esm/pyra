import PreviousValue from '../../essential/previous-value';
import Toggle from '../../essential/toggle';
import LabeledRow from '../labeled-row';

export default function ConfigElementToggle(props: {
    key2: string;
    value: boolean;
    oldValue: boolean;
    setValue(v: boolean): void;
}) {
    const { key2, value, oldValue, setValue } = props;

    return (
        <LabeledRow key2={key2} modified={value !== oldValue}>
            <Toggle
                value={value ? 'yes' : 'no'}
                values={['yes', 'no']}
                setValue={(v) => setValue(v === 'yes')}
            />
            <PreviousValue
                previousValue={
                    value !== oldValue ? (oldValue ? 'yes' : 'no') : undefined
                }
            />
        </LabeledRow>
    );
}
