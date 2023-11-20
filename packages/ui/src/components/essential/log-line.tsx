export function CoreLogLine(props: { text: string }) {
    const text = props.text.replace('\\r', '');

    if (
        !text.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6} UTC(\+|-)\d(\.\d)? - .* - .* - .*/)
    ) {
        const textStyle =
            text === 'More log lines inside logs folder ...'
                ? 'text-gray-400'
                : 'text-red-700 bg-red-75 ';
        return <div className={`font-light px-4 py-0.5 ${textStyle}`}>{text}</div>;
    }

    const timeStamp = text.slice(11, 23);
    const logSections = text.split(' - ');
    const logSource = logSections[1];
    const logType = logSections[2];
    const logMessage = logSections.slice(3).join(' - ');

    let textStyle: string;
    switch (logType) {
        case 'DEBUG':
            textStyle = 'font-light text-gray-500';
            break;
        case 'WARNING':
        case 'CRITICAL':
        case 'ERROR':
        case 'EXCEPTION':
            textStyle = 'font-bold text-red-700 bg-red-75 ';
            break;
        default:
            textStyle = 'font-medium text-gray-800';
    }

    return (
        <>
            {(logMessage.includes('Starting mainloop') ||
                logMessage.includes('Starting iteration')) && (
                <hr className="w-full my-1.5 border-0 bg-gray-200 first:hidden h-px" />
            )}
            <div
                className={
                    'flex flex-row items-start justify-start leading-tight ' +
                    `gap-x-3 ${textStyle} pl-4 py-0.5 flex-shrink-0 ` +
                    `w-full !break-all first-of-type:pt-2 last-of-type:pb-2 ` +
                    (logMessage.includes('Starting mainloop')
                        ? ' bg-teal-100 font-bold text-teal-700 '
                        : ' ')
                }
            >
                <div className="flex-shrink-0">{timeStamp}</div>
                <div className="flex-shrink-0 w-44">{logSource}</div>
                <div className="flex-shrink-0 min-w-[3rem]">{logType}</div>
                <div className="flex-grow pr-4 ">{logMessage}</div>
            </div>
        </>
    );
}

export function UILogLine(props: {
    logLine: { timestamp: number; text: string; details: string };
}) {
    return (
        <>
            <hr className="w-full my-1.5 border-0 bg-gray-100 first:hidden h-px" />
            <div
                className={
                    'flex flex-row items-start justify-start leading-tight ' +
                    `gap-x-3 font-medium text-gray-800 px-4 py-0.5 flex-shrink-0 ` +
                    `w-full !break-all first-of-type:pt-2 last-of-type:pb-2 `
                }
            >
                <div className="flex-shrink-0 min-w-[9.25rem]">
                    {new Date(props.logLine.timestamp).toLocaleString()}
                </div>
                <div className="flex flex-col items-start justify-start flex-grow w-[calc(100%-10rem)]">
                    <div>{props.logLine.text}</div>
                    <div className="w-full overflow-hidden text-xs font-light leading-tight text-gray-400 break-all whitespace-pre-wrap">
                        {props.logLine.details.replaceAll('\n\n', '\n')}
                    </div>
                </div>
            </div>
        </>
    );
}
