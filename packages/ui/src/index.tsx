import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import './styles/index.css';
//import Main from './main';
import { reduxUtils } from './utils';
import { useEffect, useState } from 'react';
import io from 'socket.io-client';
import { take } from 'lodash';

const socket = io('http://localhost:5001');

function SocketTester() {
    const [isConnected, setIsConnected] = useState(socket.connected);
    const [logLines, setLogLines] = useState<string[]>([]);

    useEffect(() => {
        socket.connect();
        socket.emit('register_as_pyra_ui');
        return () => {
            socket.disconnect();
        };
    }, []);

    useEffect(() => {
        socket.on('connect', () => {
            setIsConnected(true);
        });

        socket.on('disconnect', () => {
            setIsConnected(false);
        });

        socket.on('connect_error', (err) => {
            console.log(`connect_error due to ${err}`);
        });

        socket.on('new_log_lines', (data) => {
            const newLogLines = data;
            setLogLines(newLogLines);
        });

        return () => {
            socket.off('connect');
            socket.off('disconnect');
            socket.off('new_log_line');
        };
    }, []);

    return (
        <div className="p-2 flex-col-left gap-y-1">
            <h1 className="font-semibold text-gray-900">Socket tester</h1>
            <div
                className={
                    'rounded-md px-2 py-0.5 text-sm ' +
                    (isConnected ? 'text-green-800 bg-green-150 ' : 'text-red-800 bg-red-150 ')
                }
            >
                {isConnected ? 'connected' : 'not connected'}
            </div>
            <pre className="text-xs">{logLines}</pre>
        </div>
    );
}

// @ts-ignore
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <Provider store={reduxUtils.store}>
        <SocketTester />
    </Provider>
);
