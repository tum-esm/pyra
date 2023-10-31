import { Button } from '../ui/button';

export default function SavingOverlay(props: {
    errorMessage: undefined | string;
    onSave(): void;
    onRevert(): void;
    isSaving: boolean;
}) {
    return (
        <div className="fixed bottom-0 left-0 z-50 w-full p-3 text-sm pl-[11.75rem] text-center border-t border-blue-300 bg-blue-200 flex-row-right gap-x-2">
            <div className="flex-grow text-left text-blue-950">
                <div className="max-w-xl break-all">
                    {props.errorMessage === undefined && 'Save your changes now!'}
                    {props.errorMessage !== undefined &&
                        props.errorMessage.replace('ConfigPartial is invalid: Error in ', '')}
                </div>
            </div>

            <Button onClick={props.onRevert} disabled={props.isSaving}>
                revert
            </Button>
            <Button onClick={props.onSave} disabled={props.isSaving}>
                save
            </Button>
        </div>
    );
}
