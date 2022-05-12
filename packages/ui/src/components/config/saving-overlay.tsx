import Button from '../essential/button';

export default function SavingOverlay(props: {
    errorMessage: undefined | string;
    saveLocalJSON(): void;
    restoreCentralJSON(): void;
}) {
    const { errorMessage, saveLocalJSON, restoreCentralJSON } = props;
    return (
        <div className="fixed bottom-0 left-0 z-50 w-full p-3 text-sm font-medium pl-[11.75rem] text-center border-t border-yellow-300 bg-yellow-75 flex-row-right gap-x-2">
            {errorMessage !== undefined && (
                <span className="flex-grow text-left text-yellow-800">
                    {errorMessage}
                </span>
            )}
            <Button onClick={restoreCentralJSON} variant="gray">
                revert
            </Button>
            {errorMessage === undefined && (
                <Button onClick={saveLocalJSON} variant="gray">
                    save
                </Button>
            )}
        </div>
    );
}
