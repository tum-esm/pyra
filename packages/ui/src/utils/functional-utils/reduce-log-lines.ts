import { takeWhile } from 'lodash';
import moment from 'moment';

export default function reduceLogLines(logLines: string[], mode: '3 iterations' | '5 minutes') {
    let reducedLogLines = [];

    if (mode === '3 iterations') {
        let foundIterationStarts = 0;
        for (let i = logLines.length - 1; i >= 0; i--) {
            const line = logLines[i];
            reducedLogLines.push(line);
            if (line.includes('Starting mainloop inside process with PID')) {
                break;
            }
            if (
                line.includes('Starting iteration') ||
                line.includes('Error in current config file')
            ) {
                foundIterationStarts += 1;
            }
            if (foundIterationStarts == 3) {
                break;
            }
        }
    } else {
        let oldestTime = moment().subtract({ minutes: 5 });
        let oldestTimestamp = oldestTime.format('YYYY-MM-DD HH:mm:ss');
        reducedLogLines = takeWhile(
            logLines.reverse(),
            (l) =>
                !l.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\..*$/) ||
                l.slice(0, 19) >= oldestTimestamp
        );
    }
    return reducedLogLines.reverse();
}
