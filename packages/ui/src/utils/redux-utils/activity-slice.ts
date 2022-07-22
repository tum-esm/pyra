import { createSlice } from '@reduxjs/toolkit';
import { customTypes } from '../../custom-types';

export const activitySlice = createSlice({
    name: 'activity',
    initialState: {
        history: undefined,
    },
    reducers: {
        set: (
            state: customTypes.reduxStateActivity,
            action: { payload: customTypes.activityHistory }
        ) => {
            state.history = JSON.parse(JSON.stringify(action.payload));
        },
    },
});

export default activitySlice;
