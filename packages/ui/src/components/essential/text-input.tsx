export default function TextInput(props: {
    value: string;
    setValue(v: string): void;
    disabled?: boolean;
    small?: boolean;
    postfix?: string | undefined;
}) {
    return (
        <div
            className={
                'relative ' +
                (props.small ? ' ' : 'flex-grow ') +
                (props.disabled ? 'text-gray-500 ' : 'text-gray-900 ')
            }
        >
            <input
                type="text"
                value={props.value}
                onChange={(e) => props.setValue(e.target.value)}
                className={
                    'shadow-sm rounded-md border-slate-250 text-sm w-full ' +
                    'focus:ring-blue-500 focus:border-blue-500 ' +
                    (props.small ? 'w-14 h-7 px-2 ' : 'flex-grow h-9 ') +
                    (props.disabled ? 'cursor-not-allowed bg-gray-100 ' : ' ')
                }
                disabled={props.disabled}
            />
            {props.postfix !== undefined && (
                <div
                    className={
                        'absolute text-sm -translate-y-[calc(50%-0.5px)] opacity-50 top-1/2 left-2 pointer-events-none whitespace-pre max-w-[calc(100%-1rem)] overflow-hidden '
                    }
                >
                    <span className="opacity-0">{props.value}</span> {props.postfix}
                </div>
            )}
        </div>
    );
}
