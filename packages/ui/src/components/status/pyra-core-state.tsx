import backend from '../../utils/backend';
import { useState, useEffect } from 'react';

export default function PyraCoreState(props: {}) {
    const [stateJSON, setStateJSON] = useState<object | undefined>(undefined);
    const [loading, setLoading] = useState(false);

    async function loadStateJSON() {
        setLoading(true);
        const p = await backend.getState();
        try {
            setStateJSON(JSON.parse(p.stdout));
        } catch {
            setStateJSON(undefined);
        }
        setLoading(false);
    }

    useEffect(() => {
        loadStateJSON();
    }, []);

    return (
        <div className={'w-full text-sm flex-row-left gap-x-2 px-6'}>
            {loading && '...'}
            {!loading &&
                stateJSON === undefined &&
                'state of pyra-core could not be loaded'}
            {!loading && stateJSON !== undefined && JSON.stringify(stateJSON)}
        </div>
    );
}
