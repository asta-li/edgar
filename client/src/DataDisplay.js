import React from 'react';
import Typography from '@material-ui/core/Typography';

const DataDisplay = props => {
    console.log(props.response)
    // if this.props.response invalid, then return (<...>)
    return (
        <React.Fragment>
        <Typography component="h2" variant="h6">
        {props.response}
        </Typography>
        </React.Fragment>
    );
}

export { DataDisplay };