import moment from 'moment';
import { ActivityHistory } from '../zustand-utils/activity-zustand';

type ActivitySection = { from: string; to: string };

export default function generateActivityHistories(
    activityHistory: ActivityHistory,
    measurementsAreRunning: boolean,
    errorIsPresent: boolean
): {
    core: ActivitySection[];
    measurements: ActivitySection[];
    error: ActivitySection[];
} {
    /*
    This function parses the activity logs in reverse. The current state
    can be read from the current log lines (whether measurements should be
    running and/or an error is present).

    measurementsAreRunning and errorIsPresent is determined from the current
    log lines.
    */
    const now = moment();

    let coreEndTime: moment.Moment | undefined = now;
    let measurementsEndTime: moment.Moment | undefined = measurementsAreRunning ? now : undefined;
    let errorEndTime: moment.Moment | undefined = errorIsPresent ? now : undefined;

    let coreHistory: ActivitySection[] = [];
    let measurementsHistory: ActivitySection[] = [];
    let errorHistory: ActivitySection[] = [];

    const reversedActivityHistory: ActivityHistory = JSON.parse(
        JSON.stringify(activityHistory)
    ).reverse();

    reversedActivityHistory.forEach((a) => {
        if (a.event === 'start-core' && coreEndTime !== undefined) {
            coreHistory.push({ from: a.localTime, to: coreEndTime.format('HH:mm:ss') });
            coreEndTime = undefined;
            measurementsEndTime = undefined;
        }

        if (a.event === 'start-measurements') {
            // if I have already seen an unpaired "stop-measurements"
            if (measurementsEndTime !== undefined) {
                measurementsHistory.push({
                    from: a.localTime,
                    to: measurementsEndTime.format('HH:mm:ss'),
                });
            } else if (coreEndTime !== undefined) {
                measurementsHistory.push({
                    from: a.localTime,
                    to: coreEndTime.format('HH:mm:ss'),
                });
            }
            measurementsEndTime = undefined;
        }

        if (a.event === 'error-occured' && errorEndTime !== undefined) {
            errorHistory.push({ from: a.localTime, to: errorEndTime.format('HH:mm:ss') });
            errorEndTime = undefined;
        }

        if (a.event === 'stop-core') {
            coreEndTime = moment(a.localTime, 'HH:mm:ss');
        }
        if (a.event === 'stop-measurements') {
            measurementsEndTime = moment(a.localTime, 'HH:mm:ss');
        }
        if (a.event === 'errors-resolved') {
            errorEndTime = moment(a.localTime, 'HH:mm:ss');
        }
    });

    return { core: coreHistory, measurements: measurementsHistory, error: errorHistory };
}
