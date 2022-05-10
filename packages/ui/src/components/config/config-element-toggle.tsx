import PreviousValue from '../essential/previous-value';
import Toggle from '../essential/toggle';
import LabeledRow from './labeled-row';

const customLabels: any = {
    'measurement_triggers.manual_override': {
        trueLabel: 'force measurements to run',
        falseLabel: 'evaluate sun state',
    },
};

export default function ConfigElementToggle(props: {
    key1: string;
    key2: string;
    value: boolean;
    oldValue: boolean;
    setValue(v: boolean): void;
}) {
    const { key1, key2, value, oldValue, setValue } = props;

    const customLabel = customLabels[`${key1}.${key2}`];
    let trueLabel = 'yes';
    let falseLabel = 'no';
    if (customLabel !== undefined) {
        trueLabel = customLabel.trueLabel;
        falseLabel = customLabel.falseLabel;
    }

    return (
        <LabeledRow key2={key2} modified={value !== oldValue}>
            <Toggle {...{ value, setValue, trueLabel, falseLabel }} />
            <PreviousValue
                previousValue={
                    value !== oldValue ? (oldValue ? trueLabel : falseLabel) : undefined
                }
            />
        </LabeledRow>
    );
}
