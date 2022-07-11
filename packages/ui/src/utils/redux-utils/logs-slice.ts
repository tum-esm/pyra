import { createSlice } from '@reduxjs/toolkit';
import { customTypes } from '../../custom-types';
import functionalUtils from '../functional-utils';

export const logsSlice = createSlice({
    name: 'logs',
    initialState: {
        infoLines: undefined,
        debugLines: undefined,
        fetchUpdates: true,
        renderedLogScope: '3 iterations',
    },
    reducers: {
        set: (state: customTypes.reduxStateLogs, action: { payload: string[] }) => {
            const nonEmptyLines = action.payload.filter((l) => l.replace(/\n /g, '').length > 0);
            const lastFiveMinuteLines = functionalUtils.reduceLogLines(nonEmptyLines, '5 minutes');
            state.debugLines = lastFiveMinuteLines;
            state.infoLines = lastFiveMinuteLines.filter((l) => !l.includes(' - DEBUG - '));
        },
        setFetchUpdates: (state: customTypes.reduxStateLogs, action: { payload: boolean }) => {
            state.fetchUpdates = action.payload;
        },
        setRenderedLogScope: (
            state: customTypes.reduxStateLogs,
            action: { payload: '3 iterations' | '5 minutes' }
        ) => {
            state.renderedLogScope = action.payload;
        },
    },
});

export default logsSlice;
