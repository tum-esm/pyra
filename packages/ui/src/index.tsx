import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import './styles/index.css';

import App from './app';
import { reduxUtils } from './utils';

// @ts-ignore
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <Provider store={reduxUtils.store}>
        <App />
    </Provider>
);
