export default function PreviousValue(props: { previousValue?: string | number | any }) {
    const { previousValue } = props;
    const sharedClasses1 = 'ml-1 text-xs font-normal flex-row-left opacity-80 gap-x-1';
    const sharedClasses2 =
        'rounded-md bg-blue-100 border border-blue-300 px-1.5 py-0.5 text-blue-950 text-xs break-all';

    if (typeof previousValue === 'string' || typeof previousValue === 'number') {
        return (
            <span className={sharedClasses1}>
                <span className="whitespace-nowrap">previous value: </span>
                <span className={sharedClasses2}>{previousValue}</span>
            </span>
        );
    } else if (typeof previousValue === 'object' && previousValue.length !== undefined) {
        return (
            <span className={sharedClasses1}>
                <span className="whitespace-nowrap">previous value: </span>
                {previousValue.map((v: any, i: number) => (
                    <span key={i} className={sharedClasses2}>
                        {v}
                    </span>
                ))}
            </span>
        );
    } else {
        return <></>;
    }
}
