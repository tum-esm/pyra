export default function Ping(props: { state: boolean | undefined }) {
    let color = 'bg-gray-500';
    if (props.state === true) {
        color = 'bg-green-500';
    }
    if (props.state === false) {
        color = 'bg-red-500';
    }
    return (
        <div className="relative w-2 h-2">
            {props.state === true && (
                <div className={'absolute w-full h-full rounded-full animate-ping ' + color} />
            )}
            <div className={'absolute w-full h-full rounded-full opacity-70 ' + color} />
        </div>
    );
}
