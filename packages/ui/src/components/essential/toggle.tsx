export default function Toggle(props: {
    value: string;
    setValue(v: string): void;
    values: string[];
    className?: string;
}) {
    const { value, setValue, values, className } = props;

    return (
        <div className="flex-row-left">
            <div className="flex flex-row h-8 elevated-panel">
                {values.map((v) => (
                    <button
                        key={v}
                        onClick={() => (value !== v ? setValue(v) : {})}
                        className={
                            'first:rounded-l-md last:rounded-r-md ' +
                            'px-4 font-medium flex-row-center text-sm ' +
                            (className !== undefined ? className : '') +
                            ' ' +
                            (value === v
                                ? 'bg-gray-800 text-gray-50 border border-gray-800 -m-px z-10'
                                : 'text-gray-500 hover:bg-gray-100 hover:text-gray-950 z-0')
                        }
                    >
                        {v}
                    </button>
                ))}
            </div>
            <div className="flex-grow" />
        </div>
    );
}
