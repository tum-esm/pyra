import { essentialComponents } from '..';
export default function LiveSwitch(props: { isLive: boolean; toggle(v: boolean): void }) {
    const { isLive, toggle } = props;

    return (
        <button
            onClick={() => toggle(!isLive)}
            className={
                'first:rounded-l-md last:rounded-r-md gap-x-2 ' +
                'px-3 font-medium flex-row-center text-sm ' +
                'elevated-panel h-7 hover:bg-gray-100 ' +
                (isLive ? 'text-gray-900' : 'text-gray-600')
            }
        >
            <essentialComponents.Ping state={isLive} />
            {isLive ? 'live' : 'paused'}
        </button>
    );
}
