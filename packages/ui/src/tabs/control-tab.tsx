export default function ControlTab(props: { visible: boolean }) {
    return (
        <div
            className={
                'w-full h-full relative ' + (props.visible ? 'flex ' : 'hidden ')
            }
        >
            TODO
        </div>
    );
}
