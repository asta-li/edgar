import React from 'react';
import Typography from '@material-ui/core/Typography';
import NumberFormat from 'react-number-format';

const GraphDisplay = props => {
    return (
        <React.Fragment>
        <Typography component="h2" variant="h6">
        {JSON.stringify(props.plot)}
        </Typography>
        </React.Fragment>
    );
}

const DataDisplay = props => {
    console.log(props.response)
    if (props.response == null) {
        return (null);
    }
    if (!props.response.type) {
        return (
            <React.Fragment>
            <Typography component="h2" variant="h6">
            {props.response}
            </Typography>
            </React.Fragment>
        );
    }
    if (props.response.type == "value") {
        return (
            <React.Fragment>
            <Typography component="h2" variant="h6">
            {"The answer is: "}
            <NumberFormat
             value={props.response.value}
             displayType={'text'}
             thousandSeparator={true}
             prefix={'$'}
            />
            </Typography>
            </React.Fragment>
        );
    }
    if (props.response.type == "plot") {
        return (
            <React.Fragment>
            <GraphDisplay plot={props.response.plot} />
            </React.Fragment>
        );
    }
    return (
        <React.Fragment>
        <Typography component="h2" variant="h6">
        {JSON.stringify(props.response)}
        </Typography>
        </React.Fragment>
    );
}

export { DataDisplay };