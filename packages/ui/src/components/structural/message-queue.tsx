import { ICONS } from '../../assets';
import toast, { resolveValue, Toaster, useToasterStore } from 'react-hot-toast';
import { useEffect } from 'react';
import { minBy } from 'lodash';

export default function MessageQueue() {
    const { toasts, pausedAt } = useToasterStore();

    console.log({ toasts });

    useEffect(() => {
        if (toasts.length > 4) {
            const oldestToast = minBy(toasts, (t) => t.createdAt);
            if (oldestToast !== undefined) {
                toast.dismiss(oldestToast.id);
            }
        }
    }, [toasts.length]);

    return (
        <Toaster
            position="bottom-right"
            toastOptions={{
                duration: 24 * 3600 * 1000,
            }}
            gutter={6}
        >
            {(t) => {
                let typeIconColor = '';
                let typeIcon = <></>;
                switch (resolveValue(t.type, t)) {
                    case 'error':
                        typeIconColor = 'text-red-300';
                        typeIcon = ICONS.alert;
                        break;
                    case 'success':
                        typeIconColor = 'text-green-300';
                        typeIcon = ICONS.check;
                        break;
                }
                return (
                    <div
                        className={
                            'bg-gray-900 rounded-md shadow text-sm flex-row-center overflow-hidden'
                        }
                        style={{ opacity: t.visible ? 1 : 0 }}
                    >
                        <div className={`w-6 h-6 p-0.5 ml-1.5 mr-1 ${typeIconColor} flex-shrink-0`}>
                            {typeIcon}
                        </div>
                        <div className={'pr-3 py-2 leading-tight text-sm text-gray-200 max-w-md'}>
                            {resolveValue(t.message, t)}
                        </div>
                        <button
                            onClick={() => toast.dismiss(resolveValue(t.id, t))}
                            className={
                                'h-full flex-row-center cursor-pointer flex-shrink-0 ' +
                                'bg-gray-800 hover:bg-gray-700 text-gray-200'
                            }
                        >
                            <div className="w-6 h-6 mx-1">{ICONS.close}</div>
                        </button>
                    </div>
                );
            }}
        </Toaster>
    );
}
