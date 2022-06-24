import { essentialComponents } from '..';

export default function SavingOverlay(props: {
    errorMessage: undefined | string;
    saveLocalConfig(): void;
    restoreCentralConfig(): void;
    isSaving: boolean;
}) {
    const { errorMessage, saveLocalConfig, restoreCentralConfig, isSaving } = props;
    return (
        <div className="fixed bottom-0 left-0 z-50 w-full p-3 text-sm font-medium pl-[11.75rem] text-center border-t border-yellow-300 bg-yellow-75 flex-row-right gap-x-2">
            {errorMessage !== undefined && (
                <span className="flex-grow text-left text-yellow-800">
                    {errorMessage}
                </span>
            )}
            <essentialComponents.Button
                onClick={restoreCentralConfig}
                variant="slate"
                disabled={isSaving}
            >
                revert
            </essentialComponents.Button>
            {errorMessage === undefined && (
                <essentialComponents.Button
                    onClick={saveLocalConfig}
                    variant="slate"
                    spinner={isSaving}
                >
                    save
                </essentialComponents.Button>
            )}
        </div>
    );
}
