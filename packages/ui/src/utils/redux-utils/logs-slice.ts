import { createSlice } from '@reduxjs/toolkit';
import { customTypes } from '../../custom-types';
import functionalUtils from '../functional-utils';

export const logsSlice = createSlice({
    name: 'logs',
    initialState: {
        infoLines: undefined,
        debugLines: undefined,
    },
    reducers: {
        set: (state: customTypes.reduxStateLogs, action: { payload: string[] }) => {
            const nonEmptyLines = action.payload.filter((l) => l.replace(/\n /g, '').length > 0);
            state.debugLines = functionalUtils.reduceLogLines(nonEmptyLines);
            state.infoLines = functionalUtils
                .reduceLogLines(nonEmptyLines)
                .filter((l) => !l.includes(' - DEBUG - '));
        },
    },
});

export default logsSlice;
