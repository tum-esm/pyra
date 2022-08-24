import moment from 'moment';
import { customTypes } from '../../custom-types';

type ActivitySection = { from: string; to: string };

export default function generateActivityHistories(activityHistory: customTypes.activityHistory): {
    core: ActivitySection[];
    measurements: ActivitySection[];
    error: ActivitySection[];
} {
    /*
    This function parses the activity logs in reverse. The current state
    can be read from the current log lines (whether measurements should be
    running and/or an error is present).
    */
    const now = moment();

    const measurementsAreRunning = false; // TODO: read from logs
    const errorIsPresent = false; // TODO: read from logs

    let coreEndTime: moment.Moment | undefined = now;
    let measurementsEndTime: moment.Moment | undefined = measurementsAreRunning ? now : undefined;
    let errorEndTime: moment.Moment | undefined = errorIsPresent ? now : undefined;

    let coreHistory: ActivitySection[] = [];
    let measurementsHistory: ActivitySection[] = [];
    let errorHistory: ActivitySection[] = [];

    const reversedActivityHistory: customTypes.activityHistory = JSON.parse(
        JSON.stringify(activityHistory)
    ).reverse();

    reversedActivityHistory.forEach((a) => {
        // when a 'start-core' is encountered, and I know that the
        // core is running at the current state of the parsing
        if (a.event === 'start-core' && coreEndTime !== undefined) {
            coreHistory.push({ from: a.localTime, to: coreEndTime.format('HH:mm:ss') });
            coreEndTime = undefined;
            measurementsEndTime = undefined;
        }

        // when a 'start-measurements' is encountered, and I know that
        // measurments are running at the current state of the parsing
        if (a.event === 'start-measurements') {
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

        if (a.event === 'stop-core') {
            coreEndTime = moment(a.localTime, 'HH:mm:ss');
        }

        if (a.event === 'stop-measurements') {
            measurementsEndTime = moment(a.localTime, 'HH:mm:ss');
        }
    });

    return { core: coreHistory, measurements: measurementsHistory, error: errorHistory };
}
