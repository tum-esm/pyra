import React, { useEffect, useState } from 'react';
import TYPES from '../../types/index';

export default function SetupTab(props: {}) {
    const [setupJSON, setSetupJSON] = useState<TYPES.setupJSON>(undefined);

    async function updateSetupJSON() {
        setSetupJSON(await window.electron.readSetupJSON());
    }

    useEffect(() => {
        updateSetupJSON();
    }, []);

    return (
        <div className='flex flex-col w-full h-full p-6'>
            {JSON.stringify(setupJSON)}
        </div>
    );
}
