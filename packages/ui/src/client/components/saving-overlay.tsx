import React from 'react';
import Button from './button';

export default function SavingOverlay(props: {
    errorMessage: undefined | string;
    saveLocalJSON(): void;
    restoreCentralJSON(): void;
}) {
    const { errorMessage, saveLocalJSON, restoreCentralJSON } = props;
    return (
        <div className='absolute bottom-0 left-0 z-50 flex flex-row items-center justify-center w-full px-6 py-2 text-sm font-medium text-center bg-white shadow-lg gap-x-2'>
            {errorMessage !== undefined && (
                <span className='text-red-700'>
                    {errorMessage}
                    <br />
                    <div className='h-1.5' />
                    <Button
                        text='revert changes'
                        onClick={restoreCentralJSON}
                        variant='red'
                    />
                </span>
            )}
            {errorMessage === undefined && (
                <>
                    <div>Save changes?</div>
                    <Button
                        text='yes'
                        onClick={saveLocalJSON}
                        variant='green'
                    />
                    <Button
                        text='no'
                        onClick={restoreCentralJSON}
                        variant='red'
                    />
                </>
            )}
        </div>
    );
}
