export default function Toggle(props: {
    value: string;
    setValue(v: string): void;
    values: string[];
    className?: string;
}) {
    const { value, setValue, values, className } = props;

    return (
        <div className="flex flex-row elevated-panel h-7">
            {values.map((v) => (
                <button
                    onClick={() => (value !== v ? setValue(v) : {})}
                    className={
                        'first:rounded-l-md last:rounded-r-md ' +
                        'px-3 font-medium flex-row-center text-sm ' +
                        (className !== undefined ? className : '') +
                        ' ' +
                        (value === v
                            ? 'bg-slate-800 text-slate-100 border border-slate-900 -m-px z-10'
                            : 'text-slate-500 hover:bg-slate-100 hover:text-slate-950 z-0')
                    }
                >
                    <div
                        className={
                            'w-2 h-2 mr-1.5 rounded-full ' +
                            (value === v ? 'bg-slate-400 ' : 'bg-slate-300')
                        }
                    />
                    {v}
                </button>
            ))}
        </div>
    );
}
