import React from 'react';
import Button from './essential/button';

export default function SavingOverlay(props: {
    errorMessage: undefined | string;
    saveLocalJSON(): void;
    restoreCentralJSON(): void;
}) {
    const { errorMessage, saveLocalJSON, restoreCentralJSON } = props;
    return (
        <div className='absolute bottom-0 left-0 z-50 w-full p-3 text-sm font-medium text-center border-t border-yellow-300 bg-yellow-75 flex-row-right gap-x-2'>
            {errorMessage !== undefined && (
                <span className='flex-grow text-left text-yellow-800'>
                    {errorMessage}
                </span>
            )}
            <Button text='revert' onClick={restoreCentralJSON} variant='gray' />
            {errorMessage === undefined && (
                <Button text='save' onClick={saveLocalJSON} variant='gray' />
            )}
        </div>
    );
}
