export default function TextInput(props: {
    value: string;
    setValue(v: string): void;
    disabled?: boolean;
    postfix?: string | undefined;
    className?: string;
}) {
    return (
        <div
            className={
                'relative flex-grow ' + (props.disabled ? 'text-gray-500 ' : 'text-gray-900 ')
            }
        >
            <input
                type="text"
                value={props.value}
                onChange={(e) => props.setValue(e.target.value)}
                className={
                    'shadow-sm rounded-lg border-slate-300 text-sm w-full ' +
                    'focus:ring-blue-100 focus:border-blue-300 focus:ring ' +
                    'flex-grow h-9 ' +
                    (props.disabled ? 'cursor-not-allowed bg-gray-100 ' : ' ') +
                    (props.className ? props.className : '')
                }
                disabled={props.disabled}
            />
            {props.postfix !== undefined && (
                <div
                    className={
                        'absolute text-sm -translate-y-[calc(50%-0.5px)] opacity-50 top-1/2 pointer-events-none whitespace-pre max-w-[calc(100%-1rem)] overflow-hidden left-3 '
                    }
                >
                    <span className="opacity-0">{props.value}</span> {props.postfix}
                </div>
            )}
        </div>
    );
}
