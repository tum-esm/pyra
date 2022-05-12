import TextInput from '../essential/text-input';
import Button from '../essential/button';
import LabeledRow from './labeled-row';
import PreviousValue from '../essential/previous-value';
import { dialog } from '@tauri-apps/api';
import parseNumberTypes from '../../utils/parse-number-types';

const postfixes: any = {
    'camtracker.motor_offset_threshold': 'degrees',
    'em27.power_min_angle': 'degrees',
    'enclosure.min_sun_angle': 'degrees',
    'measurement_triggers.sun_angle_start': 'degrees',
    'measurement_triggers.sun_angle_stop': 'degrees',
    'pyra.seconds_per_interval': 'seconds',
    'vbdsd.evaluation_size': 'images',
    'vbdsd.min_sun_angle': 'degrees',
    'vbdsd.seconds_per_interval': 'seconds',
};

export default function ConfigElementText(props: {
    key1: string;
    key2: string;
    value: string | number;
    oldValue: string | number;
    setValue(v: string | number): void;
    disabled?: boolean;
}) {
    const { key1, key2, value, oldValue, setValue, disabled } = props;

    async function triggerFileSelection() {
        const result = await dialog.open({ title: 'PyRa 4 UI', multiple: false });
        if (result !== null && result.length > 0) {
            setValue(result[0]);
        }
    }

    const showfileSelector = key2.endsWith('_path');
    const hasBeenModified = parseNumberTypes(oldValue, value) !== oldValue;

    return (
        <LabeledRow key2={key2} modified={hasBeenModified}>
            <div className="relative flex w-full gap-x-1">
                <TextInput
                    value={value.toString()}
                    setValue={setValue}
                    postfix={postfixes[`${key1}.${key2}`]}
                />
                {showfileSelector && !disabled && (
                    <Button variant="blue" onClick={triggerFileSelection}>
                        choose path
                    </Button>
                )}
            </div>
            <PreviousValue
                previousValue={hasBeenModified ? `${oldValue}` : undefined}
            />
        </LabeledRow>
    );
}
