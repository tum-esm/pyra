import Button from './button';

export default function Toggle(props: {
    value: boolean;
    setValue(v: boolean): void;
    disabled?: boolean;
    trueLabel?: string;
    falseLabel?: string;
}) {
    const { value, setValue, disabled, trueLabel, falseLabel } = props;

    return (
        <div className="relative flex my-1 gap-x-0">
            <Button
                onClick={() => setValue(true)}
                disabled={disabled}
                variant={value ? 'toggle-active' : 'toggle-inactive'}
                className="py-1 -mr-px rounded-r-none !h-7 rounded-l-md"
            >
                {trueLabel === undefined ? 'yes' : trueLabel}
            </Button>
            <Button
                onClick={() => setValue(false)}
                disabled={disabled}
                variant={value ? 'toggle-inactive' : 'toggle-active'}
                className="py-1 rounded-l-none !h-7 rounded-r-md"
            >
                {falseLabel === undefined ? 'no' : falseLabel}
            </Button>
        </div>
    );
}
