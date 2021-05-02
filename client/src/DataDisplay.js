import React from 'react';
import Typography from '@material-ui/core/Typography';
import NumberFormat from 'react-number-format';
import {Bar, Line} from 'react-chartjs-2';

const GraphDisplay = props => {
    console.log(props.data)
    
    //  Truncate timestamp from dates.
    var dates = [];
    for (var i = 0; i < props.data.x.length; ++i) {
        dates.push(props.data.x[i].substring(0, 16));
    }

    var values = [];
    var label = "";
    if (Math.abs(props.data.y[0]) > 1000000) {
        label = "In millions USD"
        for (var i = 0; i < props.data.y.length; ++i) {
            values.push(parseFloat(props.data.y[i]) / 1000000.0);
        }
    } else {
        values = props.data.y;
    }

    const data = {
        labels: dates,
        datasets: [
            {
                label: label,
                fill: false,
                lineTension: 0.1,
                backgroundColor: 'rgba(75,192,192,0.4)',
                borderColor: 'rgba(75,192,192,1)',
                borderCapStyle: 'butt',
                borderDash: [],
                borderDashOffset: 0.0,
                borderJoinStyle: 'miter',
                pointBorderColor: 'rgba(75,192,192,1)',
                pointBackgroundColor: '#fff',
                pointBorderWidth: 1,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: 'rgba(75,192,192,1)',
                pointHoverBorderColor: 'rgba(220,220,220,1)',
                pointHoverBorderWidth: 2,
                pointRadius: 1,
                pointHitRadius: 10,
                data: values
            }
        ]
    };
    return (
        <React.Fragment>
        <Line data={data} options={{ legend: { display: false } }} />
        </React.Fragment>
    );
}

const BarDisplay = props => {
    var values = [];
    var label = "";
    if (Math.abs(props.data.y[0]) > 1000000) {
        label = "In millions USD"
        for (var i = 0; i < props.data.y.length; ++i) {
            values.push(parseFloat(props.data.y[i]) / 1000000.0);
        }
    } else {
        values = props.data.y;
    }
    
    const data = {
        labels: props.data.x,
        datasets: [
            {
                label: label,
                backgroundColor: 'rgba(75,192,192,0.6)',
                borderColor: 'rgba(220,220,220,1)',
                borderWidth: 1,
                hoverBackgroundColor: 'rgba(75,192,192,1)',
                hoverBorderColor: 'rgba(220,220,220,1)',
                data: values
            }
        ]
    };
    return (
        <React.Fragment>
        <Bar data={data} options={{ legend: { display: false } }} />
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
    if (props.response.type == "number") {
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
    if (props.response.type == "bar") {
        return (
            <React.Fragment>
            <BarDisplay data={props.response.value} />
            </React.Fragment>
        );
    }
    if (props.response.type == "plot") {
        return (
            <React.Fragment>
            <GraphDisplay data={props.response.value} />
            </React.Fragment>
        );
    }
    return (
        <React.Fragment>
        <Typography component="h2" variant="h6">
        { props.response.value }
        </Typography>
        </React.Fragment>
    );
}

export { DataDisplay };