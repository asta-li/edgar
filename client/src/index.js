import React from 'react';
import ReactDOM from 'react-dom';
import CssBaseline from '@material-ui/core/CssBaseline';
import { ThemeProvider } from '@material-ui/core/styles';
import {
    BrowserRouter as Router,
} from 'react-router-dom';
import App from './App';
import theme from './theme';

ReactDOM.render(
    <ThemeProvider theme={theme}>
        <CssBaseline />
        <React.StrictMode>
            <Router>
                <App />
            </Router>
        </React.StrictMode>
        ,
    </ThemeProvider>,
    document.getElementById('root')
);
