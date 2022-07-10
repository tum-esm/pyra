export default function LogLine(props: { text: string }) {
    let { text } = props;

    if (!text.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6} - .* - .* - .*$/)) {
        const textStyle =
            text === 'More log lines inside logs folder ...'
                ? 'text-gray-400'
                : 'text-red-700 bg-red-100 ';
        return <div className={`font-light px-4 py-0.5 ${textStyle}`}>{text}</div>;
    }

    const timeStamp = text.slice(11, 23);
    const logSections = text.split(' - ');
    const logSource = logSections[1];
    const logType = logSections[2];
    const logMessage = logSections[3];

    let textStyle: string;
    switch (logType) {
        case 'DEBUG':
            textStyle = 'font-light text-gray-400';
            break;
        case 'WARNING':
        case 'CRITICAL':
        case 'ERROR':
        case 'EXCEPTION':
            textStyle = 'font-bold text-red-700 bg-red-100 ';
            break;
        default:
            textStyle = 'font-medium text-gray-800';
    }

    return (
        <div
            className={
                `flex-row-left gap-x-3 ${textStyle} px-4 py-0.5 flex-shrink-0 ` +
                `first:border-t-0 first:mt-0 first:pt-0.5 w-full ` +
                (logMessage.includes('Starting iteration')
                    ? 'border-t border-gray-300 pt-2 mt-2 '
                    : ' ') +
                (logMessage.includes('Starting mainloop')
                    ? 'border-t border-gray-300 pt-2 mt-2 bg bg-teal-100 font-bold text-teal-700 '
                    : ' ')
            }
        >
            <div className="flex-shrink-0">{timeStamp}</div>
            <div className="flex-shrink-0 w-44">{logSource}</div>
            <div className="flex-shrink-0 min-w-[3rem]">{logType}</div>
            <div className="flex-shrink-0 pr-4">{logMessage}</div>
        </div>
    );
}
