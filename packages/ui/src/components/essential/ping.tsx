export default function Ping(props: { state: boolean | undefined }) {
    let color = 'bg-gray-500';
    if (props.state === true) {
        color = 'bg-green-500';
    }
    if (props.state === false) {
        color = 'bg-red-500';
    }
    return (
        <div className="relative h-2.5 w-2.5">
            {props.state === true && (
                <div
                    className={
                        'absolute w-full h-full rounded-full animate-ping ' + color
                    }
                />
            )}
            <div
                className={'absolute w-full h-full rounded-full opacity-70 ' + color}
            />
        </div>
    );
}
