export default function reduceLogLines(logLines: string[]) {
    const reducedLogLines = [];
    let foundIterationStarts = 0;
    for (let i = logLines.length - 1; i >= 0; i--) {
        const line = logLines[i];
        reducedLogLines.push(line);
        if (line.includes('Starting mainloop inside process with PID')) {
            break;
        }
        if (line.includes('Starting iteration')) {
            foundIterationStarts += 1;
        }
        if (foundIterationStarts == 10) {
            reducedLogLines.push('More log lines inside logs folder ...');
            break;
        }
    }
    return reducedLogLines.reverse();
}
